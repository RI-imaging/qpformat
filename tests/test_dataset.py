import pathlib
import tempfile

import numpy as np
import qpimage

import qpformat.core


datapath = pathlib.Path(__file__).parent / "data"


def setup_test_data(radius_px=30, size=200, pxsize=1e-6, medium_index=1.335,
                    wavelength=550e-9, num=1):
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    pha = (r < radius_px) * 1.3
    amp = .5 + np.roll(pha, 10) / pha.max()
    qpi = qpimage.QPImage(data=(pha, amp),
                          which_data="phase,amplitude",
                          meta_data={"pixel size": pxsize,
                                     "medium index": medium_index,
                                     "wavelength": wavelength})
    path = tempfile.mktemp(suffix=".h5", prefix="drymass_test_convert")
    dout = tempfile.mkdtemp(prefix="drymass_test_sphere_")
    with qpimage.QPSeries(h5file=path, h5mode="w") as qps:
        for ii in range(num):
            qps.add_qpimage(qpi, identifier="test_{}".format(ii))
    return qpi, path, dout


def test_change_wavelength():
    _qpi, path, dout = setup_test_data()

    ds1 = qpformat.load_data(path, meta_data={"wavelength": 500e-9})
    ds2 = qpformat.load_data(path, meta_data={"wavelength": 333e-9})

    assert ds1.identifier != ds2.identifier, "should be different identifiers"


def test_identifier():
    path = datapath / "series_phasics.zip"

    ds1 = qpformat.load_data(path=path)
    assert ds1.identifier == "49bbc"

    bg_data = ds1.get_qpimage(0)
    ds2 = qpformat.load_data(path=path, bg_data=bg_data)
    assert ds2.background_identifier == "bf13f"
    assert ds2.identifier == "b6d1c"


def test_meta():
    data = np.ones((20, 20), dtype=float)
    tf = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(tf, data)

    ds = qpformat.load_data(path=tf, meta_data={"time": 47})
    assert ds.get_time() == 47
    # use `.name` because of short-hand paths on Windows
    assert pathlib.Path(tf).name in ds.get_name()


def test_meta_none():
    data = np.ones((20, 20), dtype=float)
    tf = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(tf, data)

    ds = qpformat.load_data(path=tf, meta_data={"time": 47,
                                                "medium index": None,
                                                "wavelength": np.nan})

    assert "time" in ds.meta_data
    assert "medium index" not in ds.meta_data
    assert "wavelength" not in ds.meta_data


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
    assert len(ds) == len(ds2)
    assert np.all(ds.get_qpimage(0).pha == ds2.get_qpimage(0).pha)


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


def test_save_identifier():
    """Test that identifier is saved only when full series was saved"""
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
    save_path1 = pathlib.Path(save_dir) / "savetest1.h5"
    save_path2 = pathlib.Path(save_dir) / "savetest2.h5"
    ds.saveh5(save_path1)
    ds.saveh5(save_path2, qpi_slice=(slice(0, 10), slice(0, 10)))

    # load h5
    with qpimage.QPSeries(h5file=save_path1) as qps1:
        assert qps1.identifier is not None
    with qpimage.QPSeries(h5file=save_path2) as qps2:
        assert qps2.identifier is None


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


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
