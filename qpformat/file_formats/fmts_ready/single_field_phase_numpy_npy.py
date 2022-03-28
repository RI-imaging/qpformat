from functools import lru_cache
import pathlib

import numpy as np
import qpimage

from ..single_base import SingleData


class SingleFieldPhaseNumpyNpy(SingleData):
    """Numpy complex field or phase data (numpy binary format)

    The experimental data given in `path` consist of a single
    2D ndarray (no pickled objects). The ndarray is either
    complex-valued (scattered field) or real-valued (phase).
    """
    # storage type is implemented as a property

    @property
    @lru_cache(maxsize=32)
    def storage_type(self):
        """Depending on input data type, the storage type is either
        "field" (complex) or "phase" (real)."""
        nf = np.load(str(self.path), mmap_mode="c", allow_pickle=False)
        if np.iscomplexobj(nf):
            st = "field"
        else:
            st = "phase"
        return st

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        nf = np.load(str(self.path), mmap_mode="c", allow_pickle=False)
        qpi = qpimage.QPImage(data=nf,
                              which_data=self.storage_type,
                              meta_data=self.get_metadata(),
                              h5dtype=self.as_type)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has a supported numpy file format"""
        path = pathlib.Path(path)
        valid = False
        if path.suffix == ".npy":
            try:
                nf = np.load(str(path), mmap_mode="r", allow_pickle=False)
            except (OSError, ValueError, IsADirectoryError):
                pass
            else:
                if len(nf.shape) == 2:
                    valid = True
        return valid
