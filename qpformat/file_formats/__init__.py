import os
import os.path as op

from .dataset import DataSet
# from .group_hdf5_qpimage import GroupHdf5Qpimage
# from .group_zip_tif_phasics import GroupZipTifPhasics
from .single_hdf5_qimage import SingleHdf5Qpimage
# from .single_tif_phasics import SingleTifPhasics


class GroupFolder(DataSet):
    def __init__(self, *args, **kwargs):
        super(GroupFolder, self).__init__(*args, **kwargs)
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
            fmts_qpimage = ["SingleHdf5Qpimage", "GroupHdf5Qpimage"]
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
            msg = "Multiple qpimages per GroupFolder file not supported yet!"
            raise NotImplementedError(msg)
        return self._dataset[idx]

    @property
    def files(self):
        if self._files is None:
            fifo = GroupFolder._search_files(self.path)
            self._files = [ff[0] for ff in fifo]
            self._formats = [ff[1] for ff in fifo]
        return self._files

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        ds = self._get_dataset(idx)
        return ds.get_qpimage_raw(idx=0)

    def get_time(self, idx=0):
        ds = self._get_dataset(idx)
        return ds.get_time(idx=0)

    @staticmethod
    def verify(path):
        """Verify folder file format

        The folder file format is only valid when
        - there is only one file format present
        """
        fifo = GroupFolder._search_files(path)
        fifmts = [ff[1] for ff in fifo]
        return len(set(fifmts)) == 1


class UnknownFileFormatError(BaseException):
    pass


# the order is important for
formats = [GroupFolder,
           # GroupZipTifPhasics,
           # GroupHdf5Qpimage,
           SingleHdf5Qpimage,
           # SingleTifPhasics,
           ]

# convenience dictionary
formats_dict = {}
for fmt in formats:
    formats_dict[fmt.__name__] = fmt