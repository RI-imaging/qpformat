import io
import functools
import time
import zipfile

import numpy as np

from ..series_base import SeriesData

from .single_raw_oah_tif import SingleRawOAHTif


class SeriesRawOAHZipTif(SeriesData):
    """Off-axis hologram series (zipped TIFF files)

    The data are stored as multiple TIFF files
    (:class:`qpformat.file_formats.SingleTifHolo`) in a zip file.
    """
    storage_type = "raw-oah"

    def __init__(self, *args, **kwargs):
        super(SeriesRawOAHZipTif, self).__init__(*args, **kwargs)
        self._files = None
        self._dataset = None

    def __len__(self):
        return len(self.files)

    def _get_dataset(self, idx):
        if self._dataset is None:
            self._dataset = [None] * len(self)
        if self._dataset[idx] is None:
            # Use ``zipfile.ZipFile.open`` to return an open file
            zf = zipfile.ZipFile(self.path)
            pt = zf.open(self.files[idx])
            fd = io.BytesIO(pt.read())
            self._dataset[idx] = SingleRawOAHTif(
                path=fd,
                meta_data=self.meta_data,
                as_type=self.as_type,
                qpretrieve_kw=self.qpretrieve_kw)
        return self._dataset[idx]

    @staticmethod
    @functools.lru_cache(maxsize=32)
    def _index_files(path):
        """Search zip file for tif files"""
        with zipfile.ZipFile(path) as zf:
            names = sorted(zf.namelist())
            names = [nn for nn in names if nn.endswith(".tif")]
            phasefiles = []
            for name in names:
                with zf.open(name) as pt:
                    fd = io.BytesIO(pt.read())
                    if SingleRawOAHTif.verify(fd):
                        phasefiles.append(name)
            return phasefiles

    @property
    def files(self):
        """List of hologram data file names in the input zip file"""
        if self._files is None:
            self._files = SeriesRawOAHZipTif._index_files(self.path)
        return self._files

    @functools.cache
    def get_metadata(self, idx):
        """Metadata for each TIFF file

        If there are no metadata keyword arguments defined for the
        TIFF file format, then the zip file `date_time` value is
        used.
        """
        meta_data = {}
        # first try to get the time from the TIFF file
        # (possible meta data keywords)
        ds = self._get_dataset(idx)
        thetime = ds.get_metadata().get("time", np.nan)
        if np.isnan(thetime):
            # use zipfile date_time
            zf = zipfile.ZipFile(self.path)
            info = zf.getinfo(self.files[idx])
            timetuple = tuple(list(info.date_time) + [0, 0, 0])
            thetime = time.mktime(timetuple)
        meta_data["time"] = thetime

        smeta = super(SeriesRawOAHZipTif, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        ds = self._get_dataset(idx)
        qpi = ds.get_qpimage_raw()
        meta_data = self.get_metadata(idx)
        for key in meta_data:
            qpi[key] = meta_data[key]
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` is a zip file containing TIFF files"""
        valid = False
        try:
            zf = zipfile.ZipFile(path)
        except (zipfile.BadZipfile, IsADirectoryError):
            pass
        else:
            names = sorted(zf.namelist())
            names = [nn for nn in names if nn.endswith(".tif")]
            for name in names:
                with zf.open(name) as pt:
                    fd = io.BytesIO(pt.read())
                    if SingleRawOAHTif.verify(fd):
                        valid = True
                        break
            zf.close()
        return valid
