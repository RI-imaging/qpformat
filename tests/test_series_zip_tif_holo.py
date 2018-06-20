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


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
