import functools

import h5py
import qpimage

from ..series_base import SeriesData


class SeriesRawOAHQpformatHDF5(SeriesData):
    """Raw off-axis holography series data (HDF5)"""
    storage_type = "raw-oah"
    priority = -10  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SeriesRawOAHQpformatHDF5, self).__init__(*args, **kwargs)

    @functools.cache
    def __len__(self):
        with h5py.File(self.path) as h5:
            has_ref = "reference" in h5
            has_logs = "logs" in h5
            return len(h5) - has_ref - has_logs

    def get_metadata(self, idx):
        """Get metadata directly from HDF5 attributes"""
        meta_data = {}
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            attrs = dict(ds.attrs)
            for key in qpimage.meta.META_KEYS:
                if key in attrs:
                    meta_data[key] = attrs[key]

        smeta = super(SeriesRawOAHQpformatHDF5, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            data = ds[:]
        qpi = qpimage.QPImage(data=data,
                              which_data="raw-oah",
                              meta_data=self.get_metadata(idx),
                              qpretrieve_kw=self.qpretrieve_kw,
                              h5dtype=self.as_type)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` is in the correct file format"""
        valid = False
        try:
            h5 = h5py.File(path, mode="r")
        except (OSError,):
            pass
        else:
            if (h5.attrs.get("file_format", "") == "qpformat"
                and h5.attrs.get("imaging_modality", "") ==
                    "off-axis holography"
                    and "0" in h5 and "1" in h5):
                valid = True
            h5.close()
        return valid
