import copy

import h5py
import numpy as np
import qpimage

from ..single_base import SingleData


class SingleRawQLSIQpformatHDF5(SingleData):
    """Raw quadriwave lateral shearing interferometry data (HDF5)"""
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

    def get_time(self, idx=0):
        """Time for each dataset"""
        with h5py.File(self.path) as h5:
            ds = h5["0"]
            thetime = ds.attrs.get("time", np.nan)
        return thetime

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with h5py.File(self.path) as h5:
            holo = h5["0"][:]
        meta_data = copy.copy(self.meta_data)
        qpi = qpimage.QPImage(data=holo,
                              which_data="raw-qlsi",
                              meta_data=meta_data,
                              qpretrieve_kw=self.qpretrieve_kw,
                              h5dtype=self.as_type)
        # set identifier
        qpi["identifier"] = self.get_identifier()
        qpi["time"] = self.get_time()
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
