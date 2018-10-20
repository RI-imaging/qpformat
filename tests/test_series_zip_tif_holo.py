import pathlib
import tempfile
import zipfile

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def setup_test_zip(num=5):
    _fd, name = tempfile.mkstemp(suffix=".zip", prefix="qpformat_test_holo_")
    tifname = datapath / "single_holo.tif"
    with zipfile.ZipFile(name, mode="w") as arc:
        for ii in range(num):
            arc.write(tifname, arcname="test_{:04d}.tif".format(ii))
    return pathlib.Path(name)


def test_basic():
    num = 5
    path = setup_test_zip(num)
    ds = qpformat.load_data(path)
    # basic tests
    assert ds.storage_type == "hologram"
    assert len(ds) == num
    assert ds.is_series
    assert ds.path == path
    assert "SeriesZipTifHolo" in ds.__repr__()

    try:
        path.unlink()
    except OSError:
        pass


def test_time():
    path = setup_test_zip(2)
    ds = qpformat.load_data(path)
    ds.get_time(0)
    # this is the creation date of "singel_holo.tif"
    assert ds.get_time(0) == 1529500484

    try:
        path.unlink()
    except OSError:
        pass


def test_load_data():
    num = 5
    path = setup_test_zip(num)
    ds = qpformat.load_data(path)
    # basic tests
    qpi = ds.get_qpimage(0)
    assert qpi.shape == (238, 267)

    try:
        path.unlink()
    except OSError:
        pass


def test_returned_identifier():
    path = setup_test_zip()
    ds = qpformat.load_data(path)
    qpi = ds.get_qpimage(0)
    assert "identifier" in qpi
    qpiraw = ds.get_qpimage_raw(0)
    assert "identifier" in qpiraw

    try:
        path.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
