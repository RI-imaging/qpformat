import h5py
import qpimage

from .dataset import SeriesData


class SeriesHdf5Qpimage(SeriesData):
    def __init__(self, *args, **kwargs):
        super(SeriesHdf5Qpimage, self).__init__(*args, **kwargs)
        self._qpseries = qpimage.QPSeries(h5file=self.path,
                                          h5mode="r")
        self._dataset = None

    def __len__(self):
        return len(self._qpseries)

    def get_qpimage(self, idx):
        """Return background-corrected QPImage of data at index `idx`"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            return super(SeriesHdf5Qpimage, self).get_qpimage(idx)
        else:
            # We can use the background data stored in the qpimage hdf5 file
            return self._qpseries.get_qpimage(index=idx).copy()

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        qpi = self._qpseries.get_qpimage(index=idx).copy()
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
            qpi0 = h5["qpi_0"]
        except (OSError, KeyError):
            pass
        else:
            if ("qpimage version" in qpi0.attrs and
                "phase" in qpi0 and
                "amplitude" in qpi0 and
                "bg_data" in qpi0["phase"] and
                    "bg_data" in qpi0["amplitude"]):
                valid = True
        return valid
