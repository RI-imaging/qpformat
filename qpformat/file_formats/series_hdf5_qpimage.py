import h5py
import qpimage

from .dataset import DataSet


class SeriesHdf5Qpimage(DataSet):
    def __init__(self, *args, **kwargs):
        super(SeriesHdf5Qpimage, self).__init__(*args, **kwargs)
        self._qpseries = qpimage.QPSeries(h5file=self.path,
                                          h5mode="r")
        self._dataset = None

    def __len__(self):
        return len(self._qpseries)

    def get_qpimage(self, idx=0):
        """Return background-corrected QPImage of data at index `idx`"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            return super(SeriesHdf5Qpimage, self).get_qpimage(idx)
        else:
            # We can use the background data stored in the qpimage hdf5 file
            return self._qpseries.get_qpimage(index=idx).copy()

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        qpi = self._qpseries.get_qpimage(index=idx).copy()
        # Remove previously performed background correction
        qpi.set_bg_data(None)
        return qpi

    def get_time(self, idx=0):
        """Return the time of the QPImage data"""
        qpi = self._qpseries.get_qpimage(index=idx)
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
            qpi0 = h5["qpi_0"]
        except:
            pass
        else:
            if ("qpimage version" in qpi0.attrs and
                "phase" in qpi0 and
                "amplitude" in qpi0 and
                "bg_data" in qpi0["phase"] and
                    "bg_data" in qpi0["amplitude"]):
                valid = True
        return valid
