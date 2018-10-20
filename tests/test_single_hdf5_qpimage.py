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
    qpi = qpimage.QPImage(h5file=path, h5mode="r").copy()
    qpi["identifier"] = "an extremely important string"
    qpi.copy(tf)

    ds1 = qpformat.load_data(path)
    ds2 = qpformat.load_data(tf)

    assert ds1.identifier != ds2.identifier
    # individual identifiers are not extracted anymore as of
    # qpformat version 0.3.4
    assert "an extremely important string" not in ds2.identifier
    assert ds1.identifier == ds1.get_identifier()
    assert ds2.identifier == ds2.get_identifier()

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_load_data():
    path = datapath / "single_qpimage.h5"
    ds = qpformat.load_data(path)
    assert ds.path == path.resolve()
    assert np.isnan(ds.get_time()), "original file has no time metadata"
    assert "SingleHdf5Qpimage" in ds.__repr__()
    qpd = ds.get_qpimage()
    qpi = qpimage.QPImage(h5file=path, h5mode="r").copy()
    qpi["identifier"] = "test"
    assert qpd["identifier"] != qpi["identifier"]
    assert qpd == qpi
    assert qpd.shape == qpi.shape
    assert np.allclose(qpd.amp, qpi.amp)
    assert np.allclose(qpd.pha, qpi.pha)


def test_meta_extraction():
    path = datapath / "single_qpimage.h5"
    tf = tempfile.mktemp(suffix=".h5", prefix="qpformat_test_")
    qpi = qpimage.QPImage(h5file=path, h5mode="r").copy()
    qpi["wavelength"] = 345e-9
    qpi["pixel size"] = .1e-6
    qpi["medium index"] = 1.336
    qpi.copy(tf)

    ds = qpformat.load_data(tf)

    assert ds.meta_data["wavelength"] == 345e-9
    assert ds.meta_data["pixel size"] == .1e-6
    assert ds.meta_data["medium index"] == 1.336

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_meta_override():
    path = datapath / "single_qpimage.h5"
    tf = tempfile.mktemp(suffix=".h5", prefix="qpformat_test_")
    qpi = qpimage.QPImage(h5file=path, h5mode="r").copy()
    qpi.copy(tf)

    wl = 333e-9
    px = .111
    ds = qpformat.load_data(tf, meta_data={"wavelength": wl,
                                           "pixel size": px})

    assert ds.meta_data["wavelength"] == wl
    assert ds.meta_data["pixel size"] == px

    qpi_ds = ds.get_qpimage(0)
    assert qpi_ds["wavelength"] == wl
    assert qpi_ds["pixel size"] == px

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_returned_identifier():
    path = datapath / "single_qpimage.h5"
    ds = qpformat.load_data(path)
    qpi = ds.get_qpimage(0)
    assert "identifier" in qpi
    qpiraw = ds.get_qpimage_raw(0)
    assert "identifier" in qpiraw


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
