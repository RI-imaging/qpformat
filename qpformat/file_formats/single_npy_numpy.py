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

    def get_qpimage_raw(self):
        """Return QPImage without background correction"""
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
            except (OSError, ValueError, IsADirectoryError):
                pass
            else:
                if len(nf.shape) == 2:
                    valid = True
        return valid
