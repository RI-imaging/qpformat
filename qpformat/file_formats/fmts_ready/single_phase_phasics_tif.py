import calendar
from os import fspath
import time
import xml.etree.ElementTree as ET

import numpy as np
import qpimage
import tifffile

from ..single_base import SingleData


# baseline clamp intensity normalization for phasics tif files
INTENSITY_BASELINE_CLAMP = 150

# https://www.loc.gov/preservation/digital/formats/content/tiff_tags.shtml
TIFF_TAGS = {
    "MaxSampleValue": 281,
}


class LoadTifPhasicsError(BaseException):
    pass


class SinglePhasePhasicsTif(SingleData):
    """Phasics image ("SID PHA*.tif")

    Notes
    -----
    - Only the processed phase data files are supported, i.e. TIFF
      file names starting with "SID PHA" exported by the commercial
      Phasics software.

    - If the "wavelength" key in `meta_data` is not set (units: [m]),
      then the wavelength is extracted from the xml data stored in
      tag "61238" of the tif file.
    """
    storage_type = "phase,intensity"

    def __init__(self, path, meta_data=None, *args, **kwargs):
        if meta_data is None:
            meta_data = {}
        if "wavelength" not in meta_data:
            # get wavelength if not given
            wl = self._get_wavelength(path)
            if not np.isnan(wl):
                meta_data["wavelength"] = wl
            else:
                # We need the wavelength to convert OPD to phase
                msg = "'wavelength' must be specified in `meta_data`!"
                raise LoadTifPhasicsError(msg)

        super(SinglePhasePhasicsTif, self).__init__(path=path,
                                                    meta_data=meta_data,
                                                    *args, **kwargs)

    @staticmethod
    def _get_meta_data(path, section, name):
        with SinglePhasePhasicsTif._get_tif(path) as tf:
            meta = tf.pages[0].tags[61238].value
        meta = meta.strip("'b")
        meta = meta.replace("\\n", "\n")
        meta = meta.replace("\\r", "")
        root = ET.fromstring("<root>\n" + meta + "</root>")
        for phadata in root:
            for cluster in phadata:
                sec = cluster[0].text
                for child in cluster:
                    if len(child) == 2:
                        nm, val = child
                        # print(sec, nm.text, val.text)
                        if (sec.lower() == section and
                                nm.text.lower() == name):
                            return val.text
        else:
            return None

    @staticmethod
    def _get_tif(path):
        if hasattr(path, "seek"):  # opened file
            # Seek open file zero to avoid error in tifffile:
            # "ValueError: invalid TIFF file"
            path.seek(0)
        else:  # path
            path = fspath(path)
        return tifffile.TiffFile(path)

    def _get_wavelength(self, path):
        for section in ["analyse data", "analyse data v1"]:
            wl_str = SinglePhasePhasicsTif._get_meta_data(path=path,
                                                          section=section,
                                                          name="lambda(nm)")
            if wl_str:
                wavelength = float(wl_str) * 1e-9
                break
        else:
            wavelength = np.nan
        return wavelength

    def get_metadata(self, idx=0):
        """Get image metadata

        The time is stored in the "61238" tag.
        """
        meta_data = {}

        timestr = SinglePhasePhasicsTif._get_meta_data(
            path=self.path,
            section="acquisition info",
            name="date & heure")
        if timestr is not None:
            timestr = timestr.replace(",", ".")
            timestrf, timeus = timestr.split(".")
            # '2016-04-29_17h31m35s.00827'
            structtime = time.strptime(timestrf,
                                       "%Y-%m-%d_%Hh%Mm%Ss")
            fracsec = float(timeus) * 1e-5
            # use calendar, because we need UTC
            thetime = calendar.timegm(structtime) + fracsec
            meta_data["time"] = thetime

        smeta = super(SinglePhasePhasicsTif, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with SinglePhasePhasicsTif._get_tif(self.path) as tf:
            # page 0 contains intensity
            # page 1 contains phase in nm
            # page 2 contains phase in wavelengths
            # Intensity:
            inttags = tf.pages[0].tags
            imin = inttags["61243"].value
            imax = inttags["61242"].value
            isamp = inttags[TIFF_TAGS["MaxSampleValue"]].value
            blc = INTENSITY_BASELINE_CLAMP
            inten = tf.pages[0].asarray() * (imax - imin) / isamp + imin - blc
            inten[inten < 0] = 0
            # Phase
            # The SID4Bio records two phase images, one in wavelengths and
            # one in nanometers. Surprisingly, these two phase images are
            # not derived from the same recording. The first image (pages[1])
            # (in wavelengths) matches the intensity image (pages[0]). The
            # second image (pages[2]) is recorded at a different time point.
            # Initially, I thought it would be best to compute the phase
            # directly from the measured value in nanometers (pages[2]) using
            # the known wavelength given by the qpformat user. However, since
            # phase and amplitude won't match up in that case, the wavelength
            # phase image (pages[1]) has to be used. Since phasics uses its own
            # wavelength (set by the user in the acquisition/extraction
            # software) which might be wrong, I decided to first compute
            # the phase in nanometers from tf.pages[1] using the phasics
            # wavelength and then proceed as before, computing the phase
            # in radians using the correct, user-given wavelength.
            wl_phasics = self._get_wavelength(self.path)
            if not np.isnan(wl_phasics):
                # proceed with phase in wavelengths
                phaid = 1
            else:
                # proceed with phase in nanometers
                phaid = 2
            phatags = tf.pages[phaid].tags
            pmin = phatags["61243"].value
            pmax = phatags["61242"].value
            psamp = phatags[TIFF_TAGS["MaxSampleValue"]].value
            if psamp == 0 or pmin == pmax:
                # no phase data
                pha = np.zeros_like(inten)
            else:
                # optical path difference
                opd = tf.pages[phaid].asarray() * (pmax - pmin) / psamp + pmin
                if phaid == 1:  # convert [wavelengths] to [nm]
                    assert not np.isnan(wl_phasics)
                    opd *= wl_phasics * 1e9
                # convert from [nm] to [rad]
                pha = opd / (self.meta_data["wavelength"] * 1e9) * 2 * np.pi

        qpi = qpimage.QPImage(data=(pha, inten),
                              which_data="phase,intensity",
                              meta_data=self.get_metadata(idx),
                              h5dtype=self.as_type)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` is a phasics phase/intensity TIFF file"""
        valid = False
        try:
            tf = SinglePhasePhasicsTif._get_tif(path)
        except (ValueError, IsADirectoryError, KeyError,
                tifffile.tifffile.TiffFileError):
            pass
        else:
            if (len(tf.pages) == 3 and
                61243 in tf.pages[0].tags and
                61242 in tf.pages[0].tags and
                61238 in tf.pages[0].tags and
                61243 in tf.pages[1].tags and
                61242 in tf.pages[1].tags and
                TIFF_TAGS["MaxSampleValue"] in tf.pages[0].tags and
                (tf.pages[0].tags[61242].value !=
                 tf.pages[1].tags[61242].value)):
                valid = True
            tf.close()
        return valid
