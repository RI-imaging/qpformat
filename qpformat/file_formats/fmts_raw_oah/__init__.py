from .series_hdf5_hyperspy import SeriesHdf5HyperSpy
from .series_hdf5_raw_oah import SeriesHDF5RawOAH
from .series_zip_tif_holo import SeriesZipTifHolo
from .single_hdf5_raw_oah import SingleHDF5RawOAH
from .single_tif_holo import SingleTifHolo


registered_formats = [
    SeriesHDF5RawOAH,
    SeriesHdf5HyperSpy,
    SeriesZipTifHolo,
    SingleHDF5RawOAH,
    SingleTifHolo,
]
