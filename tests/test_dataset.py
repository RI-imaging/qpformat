import os
import pathlib
import shutil
import tempfile

import numpy as np
import qpimage

import qpformat.core


datapath = pathlib.Path(__file__).parent / "data"


def test_identifier():
    path = datapath / "series_phasics.zip"

    ds1 = qpformat.load_data(path=path)
    assert ds1.identifier == "7fc65"

    bg_data = ds1.get_qpimage(0)
    ds2 = qpformat.load_data(path=path, bg_data=bg_data)
    assert ds2.background_identifier == "3f328"
    assert ds2.identifier == "1e92f"


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


def test_save():
    data_dir = tempfile.mkdtemp(prefix="qpformat_test_data_")
    data_dir = pathlib.Path(data_dir)

    data1 = np.ones((20, 20), dtype=float)
    data1 *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    np.save(data_dir / "data1.npy", data1)

    data2 = data1 * np.linspace(1.33, 1.04, 20).reshape(1, -1)
    np.save(data_dir / "data2.npy", data2)

    # save as h5
    ds = qpformat.load_data(path=data_dir)
    save_dir = tempfile.mkdtemp(prefix="qpformat_test_data_save_")
    save_path = pathlib.Path(save_dir) / "savetest.h5"
    ds.saveh5(save_path)

    # load h5
    ds2 = qpformat.load_data(path=save_path)

    assert ds.identifier is not None
    # Qpformat generates a new identifier that also depends on the given
    # keyword arguments. Thus, the identifiers are not identical.
    assert ds.identifier in ds2.identifier
    assert len(ds) == len(ds2)
    assert np.all(ds.get_qpimage(0).pha == ds2.get_qpimage(0).pha)

    shutil.rmtree(data_dir, ignore_errors=True)
    shutil.rmtree(save_dir, ignore_errors=True)


def test_save_one_bg():
    """Test that if there is a single bg, it is stored somehow
    in the output file"""
    data_dir = tempfile.mkdtemp(prefix="qpformat_test_data_")
    data_dir = pathlib.Path(data_dir)

    data1 = np.ones((20, 20), dtype=float)
    data1 *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    np.save(data_dir / "data1.npy", data1)

    data2 = data1 * np.linspace(1.33, 1.04, 20).reshape(1, -1)
    np.save(data_dir / "data2.npy", data2)

    # save as h5
    bg = qpimage.QPImage(data=data1, which_data="phase")
    ds = qpformat.load_data(path=data_dir, bg_data=bg)
    save_dir = tempfile.mkdtemp(prefix="qpformat_test_data_save_")
    save_path = pathlib.Path(save_dir) / "savetest.h5"
    ds.saveh5(save_path)

    # load h5
    ds2 = qpformat.load_data(path=save_path)
    assert np.all(ds.get_qpimage(0).pha == ds2.get_qpimage(0).pha)
    assert np.all(ds2.get_qpimage(0).pha == 0)
    assert not np.all(ds2.get_qpimage(1).pha == 0)

    shutil.rmtree(data_dir, ignore_errors=True)
    shutil.rmtree(save_dir, ignore_errors=True)


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
    data_dir = tempfile.mkdtemp(prefix="qpformat_test_data_")
    data_dir = pathlib.Path(data_dir)

    data1 = np.ones((20, 20), dtype=float)
    data1 *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    np.save(data_dir / "data1.npy", data1)

    data2 = data1 * np.linspace(1.33, 1.04, 20).reshape(1, -1)
    np.save(data_dir / "data2.npy", data2)

    # bg data
    bg_data_dir = tempfile.mkdtemp(prefix="qpformat_test_bg_data_")
    bg_data_dir = pathlib.Path(bg_data_dir)

    bg_data1 = data1 * np.linspace(1.0, 1.02, 20).reshape(1, -1)
    np.save(bg_data_dir / "bg_data1.npy", bg_data1)

    bg_data2 = data1 * np.linspace(.9, 0.87, 20).reshape(-1, 1)
    np.save(bg_data_dir / "bg_data2.npy", bg_data2)

    # tests
    ds1 = qpformat.core.load_data(path=data_dir, as_type="float64")
    bg1 = qpformat.core.load_data(path=bg_data_dir, as_type="float64")
    assert len(ds1) == 2
    ds1.set_bg(bg1)

    assert np.allclose(ds1.get_qpimage(0).pha, data1 - bg_data1)
    assert np.allclose(ds1.get_qpimage(1).pha, data2 - bg_data2)
    assert not np.allclose(ds1.get_qpimage(0).pha, data2 - bg_data2)

    shutil.rmtree(data_dir, ignore_errors=True)
    shutil.rmtree(bg_data_dir, ignore_errors=True)


def test_set_bg_qpimage():
    data = np.ones((20, 20), dtype=float)
    data *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    f_data = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(f_data, data)

    bg_data = np.ones((20, 20), dtype=float)
    bg_data *= np.linspace(0, 1.1, 20).reshape(1, -1)
    qpi = qpimage.QPImage(data=bg_data, which_data="phase")

    # set bg with dataset
    ds1 = qpformat.core.load_data(path=f_data, bg_data=qpi)
    assert np.allclose(ds1.get_qpimage().pha, data - bg_data)

    # cleanup
    try:
        os.remove(f_data)
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
