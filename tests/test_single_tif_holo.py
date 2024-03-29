import pathlib

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_basic():
    path = datapath / "single_holo.tif"
    ds = qpformat.load_data(path)
    # basic tests
    assert ds.storage_type == "raw-oah"
    assert not ds.is_series
    assert ds.path == path.resolve()
    assert "SingleRawOAHTif" in ds.__repr__()


def test_identifier():
    path = datapath / "single_holo.tif"
    ds = qpformat.load_data(path, qpretrieve_kw={"invert_phase": False})
    assert ds.identifier == "9e409"


def test_load_data():
    path = datapath / "single_holo.tif"
    ds = qpformat.load_data(path)
    # basic tests
    qpi = ds.get_qpimage(0)
    assert qpi.shape == (238, 267)


def test_returned_identifier():
    path = datapath / "single_holo.tif"
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
