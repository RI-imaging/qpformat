import pathlib
import tempfile
import shutil

import qpformat


def test_phasics():
    path = pathlib.Path(__file__).parent / "data" / "single_phasics.tif"
    ds = qpformat.load_data(path)
    assert ds.storage_type == "phase,intensity"


def test_phasics_zip():
    path = pathlib.Path(__file__).parent / "data" / "series_phasics.zip"
    ds = qpformat.load_data(path)
    assert ds.storage_type == "phase,intensity"


def test_qpimage():
    path = pathlib.Path(__file__).parent / "data" / "single_qpimage.h5"
    ds = qpformat.load_data(path)
    assert ds.storage_type == "phase,amplitude"


def test_bad_folder():
    path = pathlib.Path(__file__).parent / "data"
    try:
        qpformat.load_data(path)
    except qpformat.file_formats.MultipleFormatsNotSupportedError:
        pass
    else:
        raise ValueError("Multiple formats not supported")


def test_good_folder():
    path = pathlib.Path(__file__).parent / "data"
    dpath = pathlib.Path(tempfile.mkdtemp(prefix="qpformat_test_"))
    shutil.copy(str(path / "single_qpimage.h5"), str(dpath / "1.h5"))
    shutil.copy(str(path / "single_qpimage.h5"), str(dpath / "2.h5"))
    ds = qpformat.load_data(dpath)
    assert ds.storage_type == "phase,amplitude"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
