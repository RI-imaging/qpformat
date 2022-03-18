import copy

import h5py
import numpy as np
import qpimage

from ..dataset import SingleData


class SingleHDF5RawOAH(SingleData):
    """Raw off-axis holography data stored in an HDF5 file"""
    storage_type = "raw-oah"
    priority = -10  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SingleHDF5RawOAH, self).__init__(*args, **kwargs)
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
                              which_data="raw-oah",
                              meta_data=meta_data,
                              holo_kw=self.holo_kw,
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
                    "off-axis holography"
                    and "0" in h5
                    and "1" not in h5):
                valid = True
            h5.close()
        return valid
