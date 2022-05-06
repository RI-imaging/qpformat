import copy
import functools

import h5py
import numpy as np
import qpimage

from ..series_base import SeriesData


class SeriesRawQLSIQpformatHDF5(SeriesData):
    """Raw quadriwave lateral shearing interferometry series data (HDF5)

    If you would like to have gradient-based background correction,
    you must store a reference image in the HDF5 dataset named
    "reference" (next to the "0", "1", etc. datasets with your
    measurement data).
    """
    storage_type = "raw-qlsi"
    priority = -10  # higher priority, because it's fast

    def __init__(self, *args, **kwargs):
        super(SeriesRawQLSIQpformatHDF5, self).__init__(*args, **kwargs)
        # We keep a reference to the background data, because this way
        # qpretrieve can keep a weak reference and remember the Fourier
        # transform of the reference data.
        self._bg_data = None

    @functools.cache
    def __len__(self):
        with h5py.File(self.path) as h5:
            has_ref = "reference" in h5
            has_logs = "logs" in h5
            return len(h5) - has_ref - has_logs

    def get_time(self, idx):
        """Time for each dataset"""
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            thetime = ds.attrs.get("time", np.nan)
        return thetime

    def get_metadata(self, idx):
        """Get metadata directly from HDF5 attributes"""
        meta_data = {}
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            attrs = dict(ds.attrs)
            for key in qpimage.meta.META_KEYS:
                if key in attrs:
                    meta_data[key] = attrs[key]

        smeta = super(SeriesRawQLSIQpformatHDF5, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx):
        """Return raw QPImage (can already be background-corrected)

        Note that this QLSI file format may contain a reference dataset
        which will be taken into account during data processing.
        In this case, the data returned by `get_qpimage_raw` is already
        background-corrected with this reference image. The reason
        behind this unintuitive behavior is that in QLSI, you can
        perform the background correction in the phase gradient image
        before integration (and not after computing the phase as in
        e.g. DHM).
        """
        # Get metadata
        metadata = self.get_metadata(idx)
        qpretrieve_kw = copy.deepcopy(self.qpretrieve_kw)
        if "wavelength" in metadata:
            qpretrieve_kw.setdefault("wavelength", metadata["wavelength"])
        # Load experimental data
        with h5py.File(self.path) as h5:
            ds = h5[str(idx)]
            data = ds[:]
            # try to get optional reference data
            if self._bg_data is None:
                if "reference" in h5:
                    self._bg_data = h5["reference"][:]
            # get additional metadata required for data analysis
            if "qlsi_pitch_term" in ds.attrs:
                qpretrieve_kw.setdefault("qlsi_pitch_term",
                                         ds.attrs["qlsi_pitch_term"])

        qpi = qpimage.QPImage(data=data,
                              bg_data=self._bg_data,
                              which_data="raw-qlsi",
                              meta_data=metadata,
                              qpretrieve_kw=qpretrieve_kw,
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
                    "quadriwave lateral shearing interferometry"
                    and "0" in h5 and "1" in h5):
                valid = True
            h5.close()
        return valid
