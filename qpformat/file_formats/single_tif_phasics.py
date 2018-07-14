import calendar
import copy
from os import fspath
import time
import xml.etree.ElementTree as ET

import numpy as np
import qpimage
from skimage.external import tifffile

from .dataset import SingleData


# baseline clamp intensity normalization for phasics tif files
INTENSITY_BASELINE_CLAMP = 150


class LoadTifPhasicsError(BaseException):
    pass


class SingleTifPhasics(SingleData):
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

    def __init__(self, path, meta_data={}, *args, **kwargs):
        if "wavelength" not in meta_data:
            # get wavelength if not given
            wl_str = SingleTifPhasics._get_meta_data(path=path,
                                                     section="analyse data",
                                                     name="lambda(nm)")
            if wl_str:
                wavelength = float(wl_str) * 1e-9
                meta_data["wavelength"] = wavelength
            else:
                # We need the wavelength to convert OPD to phase
                msg = "'wavelength' must be specified in `meta_data`!"
                raise LoadTifPhasicsError(msg)

        super(SingleTifPhasics, self).__init__(path=path,
                                               meta_data=meta_data,
                                               *args, **kwargs)

    @staticmethod
    def _get_meta_data(path, section, name):
        with SingleTifPhasics._get_tif(path) as tf:
            meta = tf.pages[0].tags["61238"].as_str()

        meta = meta.strip("'b")
        meta = meta.replace("\\n", "\n")
        meta = meta.replace("\\r", "")
        root = ET.fromstring("<root>\n" + meta + "</root>")
        for phadata in root.getchildren():
            for cluster in phadata.getchildren():
                sec = cluster.getchildren()[0].text
                for child in cluster.getchildren():
                    gchild = child.getchildren()
                    if len(gchild) == 2:
                        nm, val = gchild
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

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with SingleTifPhasics._get_tif(self.path) as tf:
            # page 0 contains intensity
            # page 1 contains phase in nm
            # page 2 contains phase in wavelengths
            # Intensity:
            inttags = tf.pages[0].tags
            imin = inttags["61243"].value
            imax = inttags["61242"].value
            isamp = inttags["max_sample_value"].value
            blc = INTENSITY_BASELINE_CLAMP
            inten = tf.pages[0].asarray() * (imax - imin) / isamp + imin - blc
            # Phase
            phatags = tf.pages[2].tags
            pmin = phatags["61243"].value
            pmax = phatags["61242"].value
            psamp = phatags["max_sample_value"].value
            if psamp == 0 or pmin == pmax:
                # no phase data
                pha = np.zeros_like(inten)
            else:
                # optical path difference is in nm
                opd = tf.pages[2].asarray() * (pmax - pmin) / psamp + pmin
                pha = opd / (self.meta_data["wavelength"] * 1e9) * 2 * np.pi

        meta_data = copy.copy(self.meta_data)
        if "time" not in meta_data:
            meta_data["time"] = self.get_time()
        qpi = qpimage.QPImage(data=(pha, inten),
                              which_data="phase,intensity",
                              meta_data=meta_data,
                              h5dtype=self.as_type)
        return qpi

    def get_time(self, idx=0):
        """Return the time of the tif data since the epoch

        The time is stored in the "61238" tag.
        """
        timestr = SingleTifPhasics._get_meta_data(path=self.path,
                                                  section="acquisition info",
                                                  name="date & heure")
        if timestr is not None:
            timestr = timestr.split(".")
            # '2016-04-29_17h31m35s.00827'
            structtime = time.strptime(timestr[0],
                                       "%Y-%m-%d_%Hh%Mm%Ss")
            fracsec = float(timestr[1]) * 1e-5
            # use calendar, because we need UTC
            thetime = calendar.timegm(structtime) + fracsec
        else:
            thetime = 0
        return thetime

    @staticmethod
    def verify(path):
        """Verify that `path` is a phasics phase/intensity TIFF file"""
        valid = False
        try:
            tf = SingleTifPhasics._get_tif(path)
        except (ValueError, IsADirectoryError):
            pass
        else:
            if (len(tf) == 3 and
                "61243" in tf.pages[0].tags and
                "61242" in tf.pages[0].tags and
                "61238" in tf.pages[0].tags and
                "max_sample_value" in tf.pages[0].tags and
                (tf.pages[0].tags["61242"].value !=
                 tf.pages[1].tags["61242"].value)):
                valid = True
        return valid
