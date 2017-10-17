import h5py
import qpimage

from .dataset import DataSet


class SingleHdf5Qpimage(DataSet):
    def __len__(self):
        return 1

    def get_qpimage(self, idx=0):
        """Return background-corrected QPImage of data at index `idx`"""
        if idx != 0:
            raise ValueError("Single file format, only one entry (`idx!=0`)!")
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            return super(SingleHdf5Qpimage, self).get_qpimage(idx)
        else:
            # We can use the background data stored in the qpimage hdf5 file
            return qpimage.QPImage(h5file=self.path, h5mode="r").copy()

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        if idx != 0:
            raise ValueError("Single file format, only one entry (`idx!=0`)!")
        qpi = qpimage.QPImage(h5file=self.path, h5mode="r").copy()
        # Remove previously performed background correction
        qpi.set_bg_data(None)
        return qpi

    def get_time(self, idx=0):
        """Return the time of the QPImage data"""
        if idx != 0:
            raise ValueError("Single file format, only one entry (`idx!=0`)!")
        qpi = qpimage.QPImage(h5file=self.path, h5mode="r")
        if "time" in qpi.meta:
            return qpi.meta["time"]
        else:
            return 0

    @staticmethod
    def verify(path):
        """Verify that `path` has the qpimage file format

        Returns `True` if the file format matches.
        """
        valid = False
        try:
            h5 = h5py.File(path, mode="r")
        except:
            pass
        else:
            if ("qpimage version" in h5.attrs and
                "phase" in h5 and
                "amplitude" in h5 and
                "bg_data" in h5["phase"] and
                    "bg_data" in h5["amplitude"]):
                valid = True
        return valid
