import pathlib
import tempfile
import shutil

import qpformat

data_path = pathlib.Path(__file__).parent / "data"


def test_good_folder():
    dpath = pathlib.Path(tempfile.mkdtemp(prefix="qpformat_test_"))
    shutil.copy(data_path / "single_qpimage.h5", dpath / "1.h5")
    shutil.copy(data_path / "single_qpimage.h5", dpath / "2.h5")
    ds = qpformat.load_data(dpath)
    assert ds.storage_type == "phase,amplitude"


def test_phasics():
    path = data_path / "single_phasics.tif"
    ds = qpformat.load_data(path)
    assert ds.storage_type == "phase,intensity"


def test_phasics_zip():
    path = data_path / "series_phasics.zip"
    ds = qpformat.load_data(path)
    assert ds.storage_type == "phase,intensity"


def test_qpimage():
    path = data_path / "single_qpimage.h5"
    ds = qpformat.load_data(path)
    assert ds.storage_type == "phase,amplitude"
