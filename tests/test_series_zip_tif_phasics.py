"""
The test file "series_phasics.zip" was created from an original
Phasics zip file. The "ConfigStack.txt" was adapted to reflect
only three measured images. All data files that are not relevant
for qpformat are included as empty files to reflect the original
zip file structure. The "SID PHA*.tif" files were created with
the script given in the doc string of "test_single_tif_phasics.py".
"""
import pathlib

import numpy as np

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_load_data():
    path = datapath / "series_phasics.zip"
    ds = qpformat.load_data(path)
    assert ds.path == path.resolve()
    assert "SeriesZipTifPhasics" in ds.__repr__()


def test_data_content():
    path = datapath / "series_phasics.zip"
    ds = qpformat.load_data(path)
    assert len(ds) == 3
    assert ds.get_time(0) == 1461949418.29027
    assert ds.get_time(1) == 1461949418.62727
    assert ds.get_time(2) == 1461949419.11427
    qpi = ds.get_qpimage(0)
    assert qpi.meta["wavelength"] == 550e-9
    assert np.allclose(qpi.amp.max(), 183.96992660669972)
    assert np.allclose(qpi.pha.max() - qpi.pha.min(), 0.18902349472045898)


def test_returned_identifier():
    path = datapath / "series_phasics.zip"
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
