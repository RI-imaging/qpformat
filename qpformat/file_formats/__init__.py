import functools
import hashlib
import os
import os.path as op

from .dataset import SeriesData
from .series_hdf5_qpimage import SeriesHdf5Qpimage
from .series_zip_tif_phasics import SeriesZipTifPhasics
from .single_hdf5_qpimage import SingleHdf5Qpimage
from .single_npy_numpy import SingleNpyNumpy
from .single_tif_phasics import SingleTifPhasics


class SeriesFolder(SeriesData):
    def __init__(self, *args, **kwargs):
        super(SeriesFolder, self).__init__(*args, **kwargs)
        self._files = None
        self._formats = None
        self._dataset = None

    def __len__(self):
        return len(self.files)

    @staticmethod
    def _search_files(path):
        fifo = []
        for root, _dirs, files in os.walk(path):
            for ff in files:
                fp = op.join(root, ff)
                for fmt in formats:
                    if fmt.verify(fp):
                        fifo.append((fp, fmt.__name__))
        # remove qpimage formats if multiple formats were
        # detected.
        theformats = [ff[1] for ff in fifo]
        formset = set(theformats)
        if len(formset) > 1:
            fmts_qpimage = ["SingleHdf5Qpimage", "SeriesHdf5Qpimage"]
            fifo = [ff for ff in fifo if ff[1] not in fmts_qpimage]
        # sort the lists
        fifo = sorted(fifo)
        return fifo

    def _get_dataset(self, idx):
        if self._dataset is None:
            self._dataset = [None] * len(self)
        if self._dataset[idx] is None:
            format_class = formats_dict[self._formats[idx]]
            self._dataset[idx] = format_class(path=self._files[idx],
                                              meta_data=self.meta_data)
        if len(self._dataset[idx]) != 1:
            # TODO:
            # - add enumeration within files
            # - required for `self.get_*` functions
            msg = "Multiple qpimages per SeriesFolder file not supported yet!"
            raise NotImplementedError(msg)
        return self._dataset[idx]

    @property
    def files(self):
        if self._files is None:
            fifo = SeriesFolder._search_files(self.path)
            self._files = [ff[0] for ff in fifo]
            self._formats = [ff[1] for ff in fifo]
        return self._files

    @property
    @functools.lru_cache(maxsize=32)
    def identifier(self):
        """Return a unique identifier for the given data set"""
        # Use only file names
        data = [op.basename(ff) for ff in self.files]
        data.sort()
        # also use the folder name
        data.append(op.basename(self.path))
        for key in sorted(list(self.meta_data.keys())):
            data.append("{}={}".format(key, self.meta_data[key]))
        idsum = hashlib.md5("".join(data).encode("utf-8")).hexdigest()[:5]
        return idsum

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
        - there is only one file format present
        """
        fifo = SeriesFolder._search_files(path)
        fifmts = [ff[1] for ff in fifo]
        return len(set(fifmts)) == 1


class UnknownFileFormatError(BaseException):
    pass


# the order is important for
formats = [SeriesFolder,
           SingleHdf5Qpimage,
           SingleTifPhasics,
           SingleNpyNumpy,
           SeriesHdf5Qpimage,
           SeriesZipTifPhasics,
           ]

# convenience dictionary
formats_dict = {}
for fmt in formats:
    formats_dict[fmt.__name__] = fmt
