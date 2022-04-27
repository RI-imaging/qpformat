import copy

import h5py
import qpimage

from ..single_base import SingleData


class SingleRawQLSIQpformatHDF5(SingleData):
    """Raw quadriwave lateral shearing interferometry data (HDF5)

    If you would like to have gradient-based background correction,
    you must store a reference image in the HDF5 dataset named
    "reference" (next to the "0" dataset with your measurement data).
    """
    storage_type = "raw-qlsi"
    priority = -10  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SingleRawQLSIQpformatHDF5, self).__init__(*args, **kwargs)
        # update meta data
        with h5py.File(self.path, mode="r") as h5:
            attrs = dict(h5["0"].attrs)
        for key in qpimage.meta.META_KEYS:
            if (key not in self.meta_data
                    and key in attrs):
                self.meta_data[key] = attrs[key]

    def get_metadata(self, idx=0):
        """Get metadata directly from HDF5 attributes"""
        meta_data = {}
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            attrs = dict(ds.attrs)
            for key in qpimage.meta.META_KEYS:
                if key in attrs:
                    meta_data[key] = attrs[key]

        smeta = super(SingleRawQLSIQpformatHDF5, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx=0):
        """Return raw QPImage (can already be background-corrected)

        Note that this QLSI file format may contain a reference dataset
        which will be taken into account during data processing.
        In this case, the data returned by `get_qpimage_raw` is already
        background-corrected with this reference image. The reason
        behind this unintuitive behavior is that in QLSI, you can
        perform the background correction in the phase gradient image
        before integration (and not after computing the phase as in
        e.g. DHM).
        """
        # Get metadata
        metadata = self.get_metadata(0)
        qpretrieve_kw = copy.deepcopy(self.qpretrieve_kw)
        if "wavelength" in metadata:
            qpretrieve_kw.setdefault("wavelength", metadata["wavelength"])
        # Load experimental data
        with h5py.File(self.path) as h5:
            ds = h5["0"]
            data = ds[:]
            # try to get optional reference data
            if "reference" in h5:
                bg_data = h5["reference"][:]
            else:
                bg_data = None
            # get additional metadata required for data analysis
            if "qlsi_pitch_term" in ds.attrs:
                qpretrieve_kw.setdefault("qlsi_pitch_term",
                                         ds.attrs["qlsi_pitch_term"])

        qpi = qpimage.QPImage(data=data,
                              bg_data=bg_data,
                              which_data="raw-qlsi",
                              meta_data=self.get_metadata(idx),
                              qpretrieve_kw=qpretrieve_kw,
                              h5dtype=self.as_type)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` is in the correct file format"""
        valid = False
        try:
            h5 = h5py.File(path, mode="r")
        except (OSError,):
            pass
        else:
            if (h5.attrs.get("file_format", "") == "qpformat"
                and h5.attrs.get("imaging_modality", "") ==
                    "quadriwave lateral shearing interferometry"
                    and "0" in h5
                    and "1" not in h5):
                valid = True
            h5.close()
        return valid
