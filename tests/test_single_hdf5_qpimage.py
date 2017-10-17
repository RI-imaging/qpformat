from os.path import abspath, dirname, join
import sys

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpformat  # noqa: E402


def test_load_data():
    path = join(dirname(abspath(__file__)), "data/single_qpimage.h5")
    ds = qpformat.load_data(path)
    assert ds.path == path
    assert ds.get_time() == 0
    assert "SingleHdf5Qpimage" in ds.__repr__()


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
