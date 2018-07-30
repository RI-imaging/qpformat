import os
import pathlib
import tempfile

import numpy as np

import qpimage
import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_identifier():
    path = datapath / "single_qpimage.h5"
    tf = tempfile.mktemp(suffix=".h5", prefix="qpformat_test_")
    qpi1 = qpimage.QPImage(h5file=path, h5mode="r")
    qpi2 = qpi1.copy()
    qpi2["identifier"] = "an important string"
    # generate qpseries hdf5 file
    with qpimage.QPSeries(qpimage_list=[qpi1, qpi2],
                          h5file=tf,
                          h5mode="a"):
        pass

    ds = qpformat.load_data(tf)
    # individual identifiers are not extracted anymore as of
    # qpformat version 0.3.4
    assert ds.get_identifier(0) != "an important string"
    assert ds.get_identifier(1) != "an important string"
    assert ds.identifier in ds.get_identifier(0)

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_load_data():
    path = datapath / "single_qpimage.h5"
    tf = tempfile.mktemp(suffix=".h5", prefix="qpformat_test_")
    qpi = qpimage.QPImage(h5file=path, h5mode="r")
    # generate qpseries hdf5 file
    with qpimage.QPSeries(qpimage_list=[qpi, qpi],
                          h5file=tf,
                          h5mode="a"):
        pass

    ds = qpformat.load_data(tf)
    assert len(ds) == 2
    assert ds.path == pathlib.Path(tf)
    assert ds.get_time(1) == 0
    assert "SeriesHdf5Qpimage" in ds.__repr__()
    # individual identifiers are not extracted anymore as of
    # qpformat version 0.3.4
    qpd = ds.get_qpimage(1)
    assert qpd != qpi
    assert qpd.shape == qpi.shape
    assert np.allclose(qpd.amp, qpi.amp)
    assert np.allclose(qpd.pha, qpi.pha)

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_meta_override():
    path = datapath / "single_qpimage.h5"
    tf = tempfile.mktemp(suffix=".h5", prefix="qpformat_test_")
    qpi = qpimage.QPImage(h5file=path, h5mode="r")
    # generate qpseries hdf5 file
    with qpimage.QPSeries(qpimage_list=[qpi, qpi],
                          h5file=tf,
                          h5mode="a",
                          meta_data={"wavelength": 111e-9,
                                     "pixel size": .12}):
        pass

    wl = 333e-9
    px = .111
    ds = qpformat.load_data(tf, meta_data={"wavelength": wl,
                                           "pixel size": px})

    assert ds.meta_data["wavelength"] == wl
    assert ds.meta_data["pixel size"] == px

    qpi_ds = ds.get_qpimage(0)
    assert qpi_ds["wavelength"] == wl
    assert qpi_ds["pixel size"] == px

    qpi_ds = ds.get_qpimage(1)
    assert qpi_ds["wavelength"] == wl
    assert qpi_ds["pixel size"] == px

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
