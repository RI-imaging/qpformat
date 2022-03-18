import os
import pathlib
import tempfile
import time
import zipfile

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


DATATIME = 1529500484
# We need this due to a peculiarity of the zip file format
UTCOFFSET = time.mktime(time.gmtime(0))


def setup_test_zip(num=5):
    _fd, name = tempfile.mkstemp(suffix=".zip", prefix="qpformat_test_holo_")
    tifname = datapath / "single_holo.tif"
    # We can safely change the time, because git does not synchronize times.
    os.utime(tifname, times=(DATATIME, DATATIME))
    with zipfile.ZipFile(name, mode="w") as arc:
        for ii in range(num):
            arc.write(tifname, arcname="test_{:04d}.tif".format(ii))
    return pathlib.Path(name)


def test_basic():
    num = 5
    path = setup_test_zip(num)
    ds = qpformat.load_data(path)
    # basic tests
    assert ds.storage_type == "raw-oah"
    assert len(ds) == num
    assert ds.is_series
    assert ds.path.samefile(path)
    assert "SeriesZipTifHolo" in ds.__repr__()


def test_time():
    path = setup_test_zip(2)
    ds = qpformat.load_data(path)
    ds.get_time(0)
    # this is the creation date of "single_holo.tif"
    assert ds.get_time(0) == DATATIME - UTCOFFSET


def test_load_data():
    num = 5
    path = setup_test_zip(num)
    ds = qpformat.load_data(path)
    # basic tests
    qpi = ds.get_qpimage(0)
    assert qpi.shape == (238, 267)


def test_returned_identifier():
    path = setup_test_zip()
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
