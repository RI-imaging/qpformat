import pathlib

import numpy as np

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_series_raw_oah():
    ds = qpformat.load_data(datapath / "series_hdf5_raw-oah.h5")
    assert ds.format == "SeriesHDF5RawOAH"
    assert len(ds) == 2
    qpi1 = ds.get_qpimage(0)
    qpi2 = ds.get_qpimage(1)
    assert qpi1.meta["wavelength"] == 532e-9
    assert qpi1.meta["numerical aperture"] == 1.0
    assert np.allclose(qpi1.meta["pos x"], -0.0002045580000000009)
    assert qpi1.meta["identifier"] == "a66ad:1"
    assert qpi1.meta["time"] == 2.5
    assert qpi2.meta["time"] == 2.8
