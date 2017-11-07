import h5py
import qpimage

from .dataset import SingleData


class SingleHdf5Qpimage(SingleData):
    def get_qpimage(self):
        """Return background-corrected QPImage"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            return super(SingleHdf5Qpimage, self).get_qpimage()
        else:
            # We can use the background data stored in the qpimage hdf5 file
            return qpimage.QPImage(h5file=self.path, h5mode="r").copy()

    def get_qpimage_raw(self):
        """Return QPImage without background correction"""
        qpi = qpimage.QPImage(h5file=self.path, h5mode="r").copy()
        # Remove previously performed background correction
        qpi.set_bg_data(None)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has the qpimage file format

        Returns `True` if the file format matches.
        """
        valid = False
        try:
            h5 = h5py.File(path, mode="r")
        except (OSError,):
            pass
        else:
            if ("qpimage version" in h5.attrs and
                "phase" in h5 and
                "amplitude" in h5 and
                "bg_data" in h5["phase"] and
                    "bg_data" in h5["amplitude"]):
                valid = True
        return valid
