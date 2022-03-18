import pathlib
import numpy as np

import qpformat


data_path = pathlib.Path(__file__).parent / "data"


def test_series_raw_oah():
    ds = qpformat.load_data(data_path / "single_hdf5_raw-oah.h5")
    assert len(ds) == 1
    assert ds.format == "SingleHDF5RawOAH"
    assert ds.meta_data["wavelength"] == 532e-9
    assert ds.meta_data["numerical aperture"] == 1.0
    assert np.allclose(ds.meta_data["pos x"],
                       -0.0002045580000000009)
    assert ds.get_qpimage().meta["identifier"] == "d94c8"
