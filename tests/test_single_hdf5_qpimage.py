import os
from os.path import abspath, dirname, join
import tempfile

import qpimage
import qpformat


def test_identifier():
    path = join(dirname(abspath(__file__)), "data/single_qpimage.h5")
    tf = tempfile.mktemp(suffix=".h5", prefix="qpformat_test_")
    qpi = qpimage.QPImage(h5file=path, h5mode="r").copy()
    qpi["identifier"] = "an extremely important string"
    qpi.copy(tf)

    ds1 = qpformat.load_data(path)
    ds2 = qpformat.load_data(tf)

    assert ds1.identifier != ds2.identifier
    assert ds2.identifier == "an extremely important string"
    assert ds1.identifier == ds1.get_identifier()
    assert ds2.identifier == ds2.get_identifier()

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_load_data():
    path = join(dirname(abspath(__file__)), "data/single_qpimage.h5")
    ds = qpformat.load_data(path)
    assert ds.path == path
    assert ds.get_time() == 0
    assert "SingleHdf5Qpimage" in ds.__repr__()
    assert ds.get_qpimage() == qpimage.QPImage(h5file=path, h5mode="r")


def test_meta_override():
    path = join(dirname(abspath(__file__)), "data/single_qpimage.h5")
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


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
