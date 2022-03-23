import io
import functools
import zipfile

from ..series_base import SeriesData
from .single_phase_phasics_tif import SinglePhasePhasicsTif


class SeriesPhasePhasicsZipTif(SeriesData):
    """Phasics series data (zipped "SID PHA*.tif" files)

    The data are stored as multiple TIFF files
    (:class:`qpformat.file_formats.SingleTifPhasics`) in a zip file.
    """
    storage_type = "phase,intensity"
    priority = -1  # should get higher priority than SeriesZipTifHolo

    def __init__(self, *args, **kwargs):
        super(SeriesPhasePhasicsZipTif, self).__init__(*args, **kwargs)
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
            self._dataset[idx] = SinglePhasePhasicsTif(
                path=fd,
                meta_data=self.meta_data,
                as_type=self.as_type)
        assert len(self._dataset[idx]) == 1, "unknown phasics tif file"
        return self._dataset[idx]

    @staticmethod
    @functools.lru_cache(maxsize=32)
    def _index_files(path):
        """Search zip file for SID PHA files"""
        with zipfile.ZipFile(path) as zf:
            names = sorted(zf.namelist())
            names = [nn for nn in names if nn.endswith(".tif")]
            names = [nn for nn in names if nn.startswith("SID PHA")]
            phasefiles = []
            for name in names:
                with zf.open(name) as pt:
                    fd = io.BytesIO(pt.read())
                    if SinglePhasePhasicsTif.verify(fd):
                        phasefiles.append(name)
            return phasefiles

    @property
    def files(self):
        """List of Phasics tif file names in the input zip file"""
        if self._files is None:
            self._files = SeriesPhasePhasicsZipTif._index_files(self.path)
        return self._files

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        ds = self._get_dataset(idx)
        qpi = ds.get_qpimage_raw()
        qpi["identifier"] = self.get_identifier(idx)
        return qpi

    def get_time(self, idx):
        # Obtain the time from the tif meta data
        ds = self._get_dataset(idx)
        return ds.get_time()

    @staticmethod
    def verify(path):
        """Verify that `path` is a zip file with Phasics TIFF files"""
        valid = False
        try:
            zf = zipfile.ZipFile(path)
        except (zipfile.BadZipfile, IsADirectoryError):
            pass
        else:
            names = sorted(zf.namelist())
            names = [nn for nn in names if nn.endswith(".tif")]
            names = [nn for nn in names if nn.startswith("SID PHA")]
            for name in names:
                with zf.open(name) as pt:
                    fd = io.BytesIO(pt.read())
                    if SinglePhasePhasicsTif.verify(fd):
                        valid = True
                        break
            zf.close()
        return valid
