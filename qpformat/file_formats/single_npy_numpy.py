from functools import lru_cache
import copy

import numpy as np
import qpimage

from .dataset import SingleData


class SingleNpyNumpy(SingleData):
    """Field data stored in numpy's .npy file format

    The experimental data given in `path` consist of a single
    2D ndarray (no pickled objects). The ndarray is either
    complex-valued (scattered field) or real-valued (phase).
    """
    # storage type is implemented as a property

    @property
    @lru_cache(maxsize=32)
    def storage_type(self):
        nf = np.load(self.path, mmap_mode="c", allow_pickle=False)
        if np.iscomplexobj(nf):
            st = "field"
        else:
            st = "phase"
        return st

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        nf = np.load(self.path, mmap_mode="c", allow_pickle=False)
        meta_data = copy.copy(self.meta_data)
        qpi = qpimage.QPImage(data=nf,
                              which_data=self.storage_type,
                              meta_data=meta_data)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has the qpimage file format

        Returns `True` if the file format matches.
        """
        valid = False
        if path.endswith(".npy"):
            try:
                nf = np.load(path, mmap_mode="r", allow_pickle=False)
            except (OSError, ValueError, IsADirectoryError):
                pass
            else:
                if len(nf.shape) == 2:
                    valid = True
        return valid
