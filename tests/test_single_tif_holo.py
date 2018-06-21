import pathlib

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_basic():
    path = datapath / "single_holo.tif"
    ds = qpformat.load_data(path)
    # basic tests
    assert ds.storage_type == "hologram"
    assert not ds.is_series
    assert ds.path == path.resolve()
    assert "SingleTifHolo" in ds.__repr__()


def test_identifier():
    path = datapath / "single_holo.tif"
    ds = qpformat.load_data(path, holo_kw={"sideband": 1})
    assert ds.identifier == "e9d9d"


def test_load_data():
    path = datapath / "single_holo.tif"
    ds = qpformat.load_data(path)
    # basic tests
    qpi = ds.get_qpimage(0)
    assert qpi.shape == (238, 267)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
