import h5py
import qpimage

from ..single_base import SingleData


class SingleRawOAHQpformatHDF5(SingleData):
    """Raw off-axis holography data (HDF5)"""
    storage_type = "raw-oah"
    priority = -10  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SingleRawOAHQpformatHDF5, self).__init__(*args, **kwargs)
        # update meta data
        with h5py.File(self.path, mode="r") as h5:
            attrs = dict(h5["0"].attrs)
        for key in qpimage.meta.META_KEYS:
            if (key not in self.meta_data
                    and key in attrs):
                self.meta_data[key] = attrs[key]

    def get_metadata(self, idx=0):
        """Get metadata directly from HDF5 attributes"""
        meta_data = {}
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            attrs = dict(ds.attrs)
            for key in qpimage.meta.META_KEYS:
                if key in attrs:
                    meta_data[key] = attrs[key]

        smeta = super(SingleRawOAHQpformatHDF5, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with h5py.File(self.path) as h5:
            holo = h5["0"][:]
        qpi = qpimage.QPImage(data=holo,
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
                    and "0" in h5
                    and "1" not in h5):
                valid = True
            h5.close()
        return valid
