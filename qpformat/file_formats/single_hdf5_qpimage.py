import h5py
import qpimage

from .dataset import SingleData


class SingleHdf5Qpimage(SingleData):
    """Qpimage single (HDF5 format)

    See the documentation of :ref:`qpimage <qpimage:index>` for more
    information.
    """
    storage_type = "phase,amplitude"

    def get_qpimage(self, idx=0):
        """Return background-corrected QPImage"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            qpi = super(SingleHdf5Qpimage, self).get_qpimage()
        else:
            # We can use the background data stored in the qpimage hdf5 file
            qpi = qpimage.QPImage(h5file=self.path,
                                  h5mode="r",
                                  h5dtype=self.as_type,
                                  ).copy()
            # Force meta data
            for key in self.meta_data:
                qpi[key] = self.meta_data[key]
            # set identifier
            qpi["identifier"] = self.get_identifier(idx)
        return qpi

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        qpi = qpimage.QPImage(h5file=self.path,
                              h5mode="r",
                              h5dtype=self.as_type,
                              ).copy()
        # Remove previously performed background correction
        qpi.set_bg_data(None)
        # Force meta data
        for key in self.meta_data:
            qpi[key] = self.meta_data[key]
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has the qpimage file format"""
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
