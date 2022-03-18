from .series_hdf5_meep import SeriesHDF5SinogramMeep
from .series_hdf5_qpimage import SeriesHdf5Qpimage, SeriesHdf5QpimageSubjoined
from .series_zip_tif_phasics import SeriesZipTifPhasics
from .single_hdf5_qpimage import SingleHdf5Qpimage
from .single_npy_numpy import SingleNpyNumpy
from .single_tif_phasics import SingleTifPhasics


registered_formats = [
    SeriesHDF5SinogramMeep,
    SeriesHdf5Qpimage,
    SeriesHdf5QpimageSubjoined,
    SeriesZipTifPhasics,
    SingleHdf5Qpimage,
    SingleNpyNumpy,
    SingleTifPhasics,
]
