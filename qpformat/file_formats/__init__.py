from .group_folder import GroupFolder
from .group_hdf5_qpimage import GroupHdf5Qimage
from .group_zip_tif_phasics import GroupZipTifPhasics
from .single_hdf5_qimage import SingleHdf5Qimage
from .single_tif_phasics import SingleTifPhasics


def guess_format(path):
    """Determine the file format of a folder or a file"""
    for fmt in formats:
        if fmt.verify(path):
            return path


# the order is important for 
formats = [GroupFolder,
           GroupZipTifPhasics,
           GroupHdf5Qimage,
           SingleHdf5Qimage,
           SingleTifPhasics,
          ]


# convenience dictionary
formats_dict = {}
for _fmt in formats:
    formats_dict[_fmt.name] = _fmt
