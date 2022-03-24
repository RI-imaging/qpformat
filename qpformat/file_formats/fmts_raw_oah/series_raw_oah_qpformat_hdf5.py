import copy
import functools

import h5py
import numpy as np
import qpimage

from ..series_base import SeriesData


class SeriesRawOAHQpformatHDF5(SeriesData):
    """Raw off-axis holography series data (HDF5)"""
    storage_type = "raw-oah"
    priority = -10  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SeriesRawOAHQpformatHDF5, self).__init__(*args, **kwargs)

    @functools.cache
    def __len__(self):
        with h5py.File(self.path) as h5:
            return len(h5)

    def get_time(self, idx):
        """Time for each dataset"""
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            thetime = ds.attrs.get("time", np.nan)
        return thetime

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            attrs = dict(ds.attrs)
            data = ds[:]

        meta_data = copy.deepcopy(self.meta_data)
        for key in qpimage.meta.META_KEYS:
            if (key not in self.meta_data
                    and key in attrs):
                meta_data[key] = attrs[key]

        qpi = qpimage.QPImage(data=data,
                              which_data="raw-oah",
                              meta_data=meta_data,
                              qpretrieve_kw=self.qpretrieve_kw,
                              h5dtype=self.as_type)
        # set identifier
        qpi["identifier"] = self.get_identifier(idx)
        qpi["time"] = self.get_time(idx)
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
                    and "0" in h5 and "1" in h5):
                valid = True
            h5.close()
        return valid
