# from .group_folder import GroupFolder
# from .group_hdf5_qpimage import GroupHdf5Qpimage
# from .group_zip_tif_phasics import GroupZipTifPhasics
from .single_hdf5_qimage import SingleHdf5Qpimage
# from .single_tif_phasics import SingleTifPhasics


class UnknownFileFormatError(BaseException):
    pass


# the order is important for
formats = [  # GroupFolder,
    # GroupZipTifPhasics,
    # GroupHdf5Qpimage,
    SingleHdf5Qpimage,
    # SingleTifPhasics,
]

# convenience dictionary
formats_dict = {}
for fmt in formats:
    formats_dict[fmt.__name__] = fmt
