import h5py
import qpimage

from .dataset import SeriesData


class SeriesHdf5Qpimage(SeriesData):
    """Qpimage series (HDF5 format)"""
    storage_type = "phase,amplitude"

    def __init__(self, *args, **kwargs):
        super(SeriesHdf5Qpimage, self).__init__(*args, **kwargs)
        self._dataset = None

    def __len__(self):
        with self._qpseries() as qps:
            return len(qps)

    def _qpseries(self):
        return qpimage.QPSeries(h5file=self.path, h5mode="r")

    def get_qpimage(self, idx):
        """Return background-corrected QPImage of data at index `idx`"""
        if self._bgdata:
            # The user has explicitly chosen different background data
            # using `get_qpimage_raw`.
            qpi = super(SeriesHdf5Qpimage, self).get_qpimage(idx)
        else:
            # We can use the background data stored in the qpimage hdf5 file
            with self._qpseries() as qps:
                qpi = qps.get_qpimage(index=idx).copy()
            # Force meta data
            for key in self.meta_data:
                qpi[key] = self.meta_data[key]
            # set identifier
            qpi["identifier"] = self.get_identifier(idx)
        return qpi

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        with self._qpseries() as qps:
            qpi = qps.get_qpimage(index=idx).copy()
        # Remove previously performed background correction
        qpi.set_bg_data(None)
        # Force meta data
        for key in self.meta_data:
            qpi[key] = self.meta_data[key]
        qpi["identifier"] = self.get_identifier(idx)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has the qpimage series file format"""
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
