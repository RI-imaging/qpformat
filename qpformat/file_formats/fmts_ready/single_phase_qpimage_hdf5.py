import h5py
import qpimage

from ..single_base import SingleData


class SinglePhaseQpimageHDF5(SingleData):
    """Qpimage single (HDF5 format)

    See the documentation of :ref:`qpimage <qpimage:index>` for more
    information.
    """
    storage_type = "phase,amplitude"
    priority = -9  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SinglePhaseQpimageHDF5, self).__init__(*args, **kwargs)
        # update meta data
        with h5py.File(self.path, mode="r") as h5:
            attrs = dict(h5.attrs)
        for key in qpimage.meta.META_KEYS:
            if (key not in self.meta_data
                    and key in attrs):
                self.meta_data[key] = attrs[key]

    def get_metadata(self, idx=0):
        meta_data = {}
        with qpimage.QPImage(h5file=self.path,
                             h5mode="r",
                             h5dtype=self.as_type,
                             ) as qpi:
            meta_data.update(qpi.meta)

        smeta = super(SinglePhaseQpimageHDF5, self).get_metadata()
        meta_data.update(smeta)
        return meta_data

    def get_qpimage(self, idx=0):
        """Return background-corrected QPImage"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            qpi = super(SinglePhaseQpimageHDF5, self).get_qpimage()
        else:
            # We can use the background data stored in the qpimage hdf5 file
            qpi = qpimage.QPImage(h5file=self.path,
                                  h5mode="r",
                                  h5dtype=self.as_type,
                                  ).copy()
            # Force meta data
            meta_data = self.get_metadata()
            for key in meta_data:
                qpi[key] = meta_data[key]
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
        meta_data = self.get_metadata()
        for key in meta_data:
            qpi[key] = meta_data[key]
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
            h5.close()
        return valid
