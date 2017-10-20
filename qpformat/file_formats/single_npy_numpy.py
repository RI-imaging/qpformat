import copy

import numpy as np
import qpimage

from .dataset import DataSet


class SingleNpyNumpy(DataSet):
    """Field data stored in numpy's .npy file format

    The experimental data given in `path` consist of a single
    2D ndarray (no pickled objects). The ndarray is either
    complex-valued (scattered field) or real-valued (phase).
    """

    def __len__(self):
        return 1

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        if idx != 0:
            raise ValueError("Single file format, only one entry (`idx!=0`)!")
        # Load experimental data
        nf = np.load(self.path, mmap_mode="c", allow_pickle=False)
        if np.iscomplexobj(nf):
            which_data = "field"
        else:
            which_data = "phase"
        meta_data = copy.copy(self.meta_data)
        qpi = qpimage.QPImage(data=nf,
                              which_data=which_data,
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
            except:
                pass
            else:
                if len(nf.shape) == 2:
                    valid = True
        return valid
