from os.path import abspath, dirname, join
import shutil
import sys
import tempfile

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpformat  # noqa: E402


def setup_folder_single_h5(size=2):
    path = join(dirname(abspath(__file__)), "data/single_qpimage.h5")
    tdir = tempfile.mkdtemp(prefix="qpformat_test_")
    files = []
    for ss in range(size):
        tpath = join(tdir, "data{:04d}.h5".format(ss))
        files.append(tpath)
        shutil.copy(path, tpath)
    return tdir, files


def test_load_data():
    path, files = setup_folder_single_h5(size=2)
    ds = qpformat.load_data(path)
    # check files in folder
    assert len(ds) == 2
    for ff in ds.files:
        assert ff in files
    # names should be different
    assert ds.get_name(0) != ds.get_name(1)
    # data should be the same
    assert ds.get_qpimage(0) == ds.get_qpimage(1)
    assert ds.get_qpimage_raw(0) == ds.get_qpimage_raw(1)
    assert ds.get_qpimage(0).shape == (50, 50)
    assert ds.get_time(0) == 0
    # format should be right
    assert ds.verify(ds.path)
    assert ds.__class__.__name__ == "SeriesFolder"
    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
