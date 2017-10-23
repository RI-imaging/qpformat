import os
from os.path import abspath, dirname, join
import sys
import tempfile

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpformat.core  # noqa: E402


def test_repr():
    data = np.ones((20, 20), dtype=float)
    tf = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(tf, data)

    ds1 = qpformat.load_data(path=tf, meta_data={"wavelength": 500e-9,
                                                 "pixel size": .15e-6})
    assert "λ=500" in ds1.__repr__()
    assert "1px=0.15" in ds1.__repr__()

    ds2 = qpformat.load_data(path=tf, meta_data={"wavelength": 1e-9,
                                                 "pixel size": 15})
    assert "λ=1" in ds2.__repr__()
    assert "1px=15" in ds2.__repr__()
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_meta():
    data = np.ones((20, 20), dtype=float)
    tf = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(tf, data)

    ds = qpformat.load_data(path=tf, meta_data={"time": 47})
    assert ds.get_time() == 47
    assert tf in ds.get_name()

    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_set_bg():
    data = np.ones((20, 20), dtype=float)
    data *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    f_data = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(f_data, data)

    bg_data = np.ones((20, 20), dtype=float)
    bg_data *= np.linspace(0, 1.1, 20).reshape(1, -1)
    f_bg_data = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(f_bg_data, bg_data)

    # set bg with dataset
    ds1 = qpformat.core.load_data(path=f_data)
    bg1 = qpformat.core.load_data(path=f_bg_data)
    ds1.set_bg(bg1)
    assert np.allclose(ds1.get_qpimage().pha, data - bg_data)

    # set with QPImage
    ds2 = qpformat.core.load_data(path=f_data)
    bg2 = qpformat.core.load_data(path=f_bg_data)
    ds2.set_bg(bg2.get_qpimage())
    assert np.allclose(ds2.get_qpimage().pha, data - bg_data)

    # set with list
    ds3 = qpformat.core.load_data(path=f_data)
    bg3 = qpformat.core.load_data(path=f_bg_data)
    ds3.set_bg([bg3.get_qpimage()])
    assert np.allclose(ds3.get_qpimage().pha, data - bg_data)

    # set with bad value
    ds4 = qpformat.core.load_data(path=f_data)
    try:
        ds4.set_bg(data)
    except ValueError:
        pass
    else:
        assert False, "ndarray cannot be used to set bg data"

    # cleanup
    try:
        os.remove(f_data)
        os.remove(f_bg_data)
    except OSError:
        pass


def test_set_bg_series():
    # data
    data_dir = tempfile.mkdtemp(prefix="qpformat_test_data_")

    data1 = np.ones((20, 20), dtype=float)
    data1 *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    f_data1 = join(data_dir, "data1.npy")
    np.save(f_data1, data1)

    data2 = data1 * np.linspace(1.33, 1.04, 20).reshape(1, -1)
    f_data2 = join(data_dir, "data2.npy")
    np.save(f_data2, data2)

    # bg data
    bg_data_dir = tempfile.mkdtemp(prefix="qpformat_test_bg_data_")

    bg_data1 = data1 * np.linspace(1.0, 1.02, 20).reshape(1, -1)
    f_bg_data1 = join(bg_data_dir, "bg_data1.npy")
    np.save(f_bg_data1, bg_data1)

    bg_data2 = data1 * np.linspace(.9, 0.87, 20).reshape(-1, 1)
    f_bg_data2 = join(bg_data_dir, "bg_data2.npy")
    np.save(f_bg_data2, bg_data2)

    # tests
    ds1 = qpformat.core.load_data(path=data_dir)
    bg1 = qpformat.core.load_data(path=bg_data_dir)
    assert len(ds1) == 2
    ds1.set_bg(bg1)

    assert np.allclose(ds1.get_qpimage(0).pha, data1 - bg_data1)
    assert np.allclose(ds1.get_qpimage(1).pha, data2 - bg_data2)
    assert not np.allclose(ds1.get_qpimage(0).pha, data2 - bg_data2)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
