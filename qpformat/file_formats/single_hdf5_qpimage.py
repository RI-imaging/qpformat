import h5py
import qpimage

from .dataset import SingleData


class SingleHdf5Qpimage(SingleData):
    storage_type = "phase,amplitude"

    @property
    def identifier(self):
        with qpimage.QPImage(h5file=self.path, h5mode="r") as qpi:
            if "identifier" in qpi:
                identifier = qpi["identifier"]
            else:
                identifier = super(SingleHdf5Qpimage, self).identifier
        return identifier

    def get_identifier(self, idx=0):
        return self.identifier

    def get_qpimage(self, idx=0):
        """Return background-corrected QPImage"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            qpi = super(SingleHdf5Qpimage, self).get_qpimage()
        else:
            # We can use the background data stored in the qpimage hdf5 file
            qpi = qpimage.QPImage(h5file=self.path, h5mode="r").copy()
            # Force meta data
            for key in self.meta_data:
                qpi[key] = self.meta_data[key]
        return qpi

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        qpi = qpimage.QPImage(h5file=self.path, h5mode="r").copy()
        # Remove previously performed background correction
        qpi.set_bg_data(None)
        # Force meta data
        for key in self.meta_data:
            qpi[key] = self.meta_data[key]
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
