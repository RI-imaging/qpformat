from functools import lru_cache
from os.path import commonprefix
import pathlib

from .errors import BadFileFormatError
from .series_base import SeriesData
from .registry import get_format_classes, get_format_dict
from .util import hash_obj


class MultipleFormatsNotSupportedError(BadFileFormatError):
    """Used when a folder contains series file formats

    (see `GitHub issue #1 <https://github.com/RI-imaging/qpformat/issues/1>`__)
    """
    pass


class SeriesFolder(SeriesData):
    """Folder-based wrapper file format"""
    # storage_type is implemented as a property
    priority = -3  # higher than zip file format (issues on Windows)

    def __init__(self, *args, **kwargs):
        super(SeriesFolder, self).__init__(*args, **kwargs)
        self._files = None
        self._formats = None
        self._series = None
        self.format_dict = get_format_dict()

    @lru_cache()
    def __len__(self):
        return len(self._get_sub_image_mapping())

    @lru_cache()
    def _get_cropped_file_names(self):
        """self.files with common path prefix/suffix removed"""
        files = [ff.name for ff in self.files]
        prefix = commonprefix(files)
        suffix = commonprefix([f[::-1] for f in files])[::-1]
        cropped = [f[len(prefix):-len(suffix)] for f in files]
        return cropped

    def _get_series_from_file(self, file_idx):
        if self._series is None:
            self._series = [None] * len(self.files)
        if self._series[file_idx] is None:
            format_class = self.format_dict[self._formats[file_idx]]
            self._series[file_idx] = format_class(
                path=self._files[file_idx],
                meta_data=self.meta_data,
                as_type=self.as_type,
                qpretrieve_kw=self.qpretrieve_kw)
        return self._series[file_idx]

    @lru_cache()
    def _get_sub_image_mapping(self):
        mapping = []
        for file_idx in range(len(self.files)):
            ds = self._get_series_from_file(file_idx)
            for jj in range(len(ds)):
                # index of file, index of image in file
                mapping.append((file_idx, jj))
        return mapping

    @lru_cache()
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
        """Search a folder for data files

        .. versionchanged:: 0.6.0
            `path` is not searched recursively anymore

        .. versionchanged:: 0.13.0
            series file formats are now supported
        """
        path = pathlib.Path(path)
        fifo = []

        for fp in path.glob("*"):
            if fp.is_dir():
                continue
            for fmt in get_format_classes():
                if fmt.verify(fp):
                    fifo.append((fp, fmt.__name__))
                    break

        # Ignore qpimage formats if multiple formats were
        # detected.
        theformats = [ff[1] for ff in fifo]
        formset = set(theformats)
        if len(formset) > 1:
            fmts_qpimage = ["SinglePhaseQpimageHDF5",
                            "SeriesPhaseQpimageHDF5"]
            fifo = [ff for ff in fifo if ff[1] not in fmts_qpimage]

        # Ignore raw tif files if SinglePhasePhasicsTif is detected
        if len(formset) > 1 and "SinglePhasePhasicsTif" in theformats:
            fmts_badtif = "SingleRawOAHTif"
            fifo = [ff for ff in fifo if ff[1] not in fmts_badtif]

        # Otherwise, prevent multiple file formats in one directory.
        theformats2 = [ff[1] for ff in fifo]
        formset2 = set(theformats2)
        if len(formset2) > 1:
            msg = "Qpformat does not support multiple different file " \
                  + "formats within one directory: {}".format(formset2)
            raise MultipleFormatsNotSupportedError(msg)

        # Finally, sort the list.
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
        ds = self._get_series_from_file(0)
        return ds.storage_type

    def get_identifier(self, idx):
        """Return an identifier for the data at index `idx`

        .. versionchanged:: 0.4.2
            indexing starts at 1 instead of 0
        """
        file_idx, jj = self._get_sub_image_mapping()[idx]
        name = self._get_cropped_file_names()[file_idx]
        return f"{self.identifier}:{name}:{jj}:{idx}"

    def get_name(self, idx):
        """Return name of data at index `idx`

        .. versionadded:: 0.4.2
        """
        file_idx, jj = self._get_sub_image_mapping()[idx]
        return f"{self.path / self.files[file_idx]}:{jj}"

    def get_time(self, idx):
        file_idx, jj = self._get_sub_image_mapping()[idx]
        ds = self._get_series_from_file(file_idx)
        return ds.get_time(jj)

    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""
        file_idx, jj = self._get_sub_image_mapping()[idx]
        ds = self._get_series_from_file(file_idx)
        qpi = ds.get_qpimage_raw(jj)
        qpi["identifier"] = self.get_identifier(idx)
        return qpi

    @staticmethod
    def verify(path):
        """Verify folder file format

        The folder file format is only valid when
        there is only one file format present.
        """
        valid = True
        fifo = SeriesFolder._search_files(path)
        # dataset size
        if len(fifo) == 0:
            valid = False
        # number of different file formats
        fifmts = [ff[1] for ff in fifo]
        if len(set(fifmts)) != 1:
            valid = False
        return valid
