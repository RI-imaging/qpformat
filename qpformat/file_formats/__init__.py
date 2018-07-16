from functools import lru_cache
from os.path import commonprefix
import pathlib

from .dataset import SeriesData, hash_obj
from .dataset import SingleData  # noqa:F401 (user convenience)
from .series_hdf5_hyperspy import SeriesHdf5HyperSpy
from .series_hdf5_qpimage import SeriesHdf5Qpimage
from .series_zip_tif_holo import SeriesZipTifHolo
from .series_zip_tif_phasics import SeriesZipTifPhasics
from .single_hdf5_qpimage import SingleHdf5Qpimage
from .single_npy_numpy import SingleNpyNumpy
from .single_tif_holo import SingleTifHolo
from .single_tif_phasics import SingleTifPhasics


class MultipleFormatsNotSupportedError(BaseException):
    """Used when a folder contains series file formats

    (see `GitHub issue #1 <https://github.com/RI-imaging/qpformat/issues/1>`__)
    """
    pass


class UnknownFileFormatError(BaseException):
    """Used when a file format could not be detected"""
    pass


class SeriesFolder(SeriesData):
    """Folder-based wrapper file format"""
    # storage_type is implemented as a property

    def __init__(self, *args, **kwargs):
        super(SeriesFolder, self).__init__(*args, **kwargs)
        self._files = None
        self._formats = None
        self._dataset = None

    def __len__(self):
        return len(self.files)

    @lru_cache(maxsize=32)
    def _get_cropped_file_names(self):
        """self.files with common path prefix/suffix removed"""
        files = [ff.name for ff in self.files]
        prefix = commonprefix(files)
        suffix = commonprefix([f[::-1] for f in files])[::-1]
        cropped = [f[len(prefix):-len(suffix)] for f in files]
        return cropped

    def _get_dataset(self, idx):
        if self._dataset is None:
            self._dataset = [None] * len(self)
        if self._dataset[idx] is None:
            format_class = formats_dict[self._formats[idx]]
            self._dataset[idx] = format_class(path=self._files[idx],
                                              meta_data=self.meta_data,
                                              as_type=self.as_type)
        if len(self._dataset[idx]) != 1:
            # TODO:
            # - add enumeration within files
            # - required for `self.get_*` functions
            msg = "Multiple qpimages per SeriesFolder file not supported yet!"
            raise NotImplementedError(msg)
        return self._dataset[idx]

    @lru_cache(maxsize=32)
    def _identifier_data(self):
        """Return a unique identifier for the folder data"""
        # Use only file names
        data = [ff.name for ff in self.files]
        data.sort()
        # also use the folder name
        data.append(self.path.name)
        # add meta data
        data += self._identifier_meta()
        return hash_obj(data)

    @staticmethod
    @lru_cache(maxsize=32)
    def _search_files(path):
        path = pathlib.Path(path)
        fifo = []

        for fp in path.rglob("*"):
            if fp.is_dir():
                continue
            for fmt in formats:
                if fmt.verify(fp):
                    fifo.append((fp, fmt.__name__))
                    break

        # ignore qpimage formats if multiple formats were
        # detected.
        theformats = [ff[1] for ff in fifo]
        formset = set(theformats)
        if len(formset) > 1:
            fmts_qpimage = ["SingleHdf5Qpimage", "SeriesHdf5Qpimage"]
            fifo = [ff for ff in fifo if ff[1] not in fmts_qpimage]
        # ignore raw tif files if single_tif_phasics is detected
        if len(formset) > 1 and "SingleTifPhasics" in theformats:
            fmts_badtif = "SingleTifHolo"
            fifo = [ff for ff in fifo if ff[1] not in fmts_badtif]
        # otherwise, prevent multiple file formats
        theformats2 = [ff[1] for ff in fifo]
        formset2 = set(theformats2)
        if len(formset2) > 1:
            msg = "Qpformat does not support multiple different file " \
                  + "formats within one directory: {}".format(formset2)
            raise MultipleFormatsNotSupportedError(msg)
        # sort the lists
        fifo = sorted(fifo)
        return fifo

    @property
    def files(self):
        """List of files (only supported file formats)"""
        if self._files is None:
            fifo = SeriesFolder._search_files(self.path)
            self._files = [ff[0] for ff in fifo]
            self._formats = [ff[1] for ff in fifo]
        return self._files

    @property
    def storage_type(self):
        """The storage type depends on the wrapped file format"""
        ds = self._get_dataset(0)
        return ds.storage_type

    def get_identifier(self, idx):
        """Return an identifier for the data at index `idx`"""
        name = self._get_cropped_file_names()[idx]
        return "{}:{}:{}".format(self.identifier, name, idx)

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        ds = self._get_dataset(idx)
        return ds.get_qpimage_raw()

    def get_time(self, idx):
        ds = self._get_dataset(idx)
        return ds.get_time()

    @staticmethod
    def verify(path):
        """Verify folder file format

        The folder file format is only valid when
        there is only one file format present.
        """
        fifo = SeriesFolder._search_files(path)
        fifmts = [ff[1] for ff in fifo]
        return len(set(fifmts)) == 1


# the order is important
formats = [SeriesFolder,
           SingleHdf5Qpimage,
           SingleTifPhasics,
           SingleTifHolo,
           SingleNpyNumpy,
           SeriesHdf5HyperSpy,
           SeriesHdf5Qpimage,
           SeriesZipTifPhasics,
           SeriesZipTifHolo,  # after phasics, b/c phasics has extra keywords
           ]

# convenience dictionary
formats_dict = {}
for fmt in formats:
    formats_dict[fmt.__name__] = fmt
