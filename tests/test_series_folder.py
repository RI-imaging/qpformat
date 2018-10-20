import pathlib
import shutil
import tempfile
import zipfile

import numpy as np
import qpformat

datapath = pathlib.Path(__file__).parent / "data"


def setup_folder_single_h5(size=2, tdir=None):
    path = datapath / "single_qpimage.h5"
    if tdir is None:
        tdir = tempfile.mkdtemp(prefix="qpformat_test_")
    tdir = pathlib.Path(tdir)
    files = []
    for ss in range(size):
        tpath = tdir / "data{:04d}.h5".format(ss)
        files.append(tpath)
        shutil.copy(path, tpath)
    return tdir, files


def setup_folder_single_holo(size=2, tdir=None):
    path = datapath / "single_holo.tif"
    if tdir is None:
        tdir = tempfile.mkdtemp(prefix="qpformat_test_")
    tdir = pathlib.Path(tdir)
    files = []
    for ss in range(size):
        tpath = tdir / "data{:04d}.h5".format(ss)
        files.append(tpath)
        shutil.copy(path, tpath)
    return tdir, files


def setup_folder_single_phasics_tif(tdir=None):
    path = datapath / "series_phasics.zip"
    if tdir is None:
        tdir = tempfile.mkdtemp(prefix="qpformat_test_")

    files = []
    with zipfile.ZipFile(path) as arc:
        for fn in arc.namelist():
            arc.extract(fn, path=tdir)
            if fn.startswith("SID PHA") and fn.endswith(".tif"):
                files.append(pathlib.Path(tdir) / fn)
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
    qpi0 = ds.get_qpimage(0)
    qpi1 = ds.get_qpimage(1)
    assert qpi0 == qpi1
    assert qpi0["identifier"] != qpi1["identifier"]
    assert qpi0 == qpi1
    assert ds.get_qpimage_raw(0) == ds.get_qpimage_raw(1)
    assert ds.get_qpimage(0).shape == (50, 50)
    assert np.isnan(ds.get_time(0)), "no time defined in original file"
    # format should be right
    assert ds.verify(ds.path)
    assert ds.__class__.__name__ == "SeriesFolder"
    shutil.rmtree(path, ignore_errors=True)


def test_multiple_formats_phasics_tif():
    """
    Folders with phasics tif files sometimes contain raw tif files.
    This test makes sure the raw files are ignored
    """
    path, files = setup_folder_single_phasics_tif()
    ds = qpformat.load_data(path)
    for ff in ds.files:
        assert ff in files
    assert ds.verify(ds.path)
    assert ds.__class__.__name__ == "SeriesFolder"
    shutil.rmtree(path, ignore_errors=True)


def test_multiple_formats_phasics_tif_ignore_h5():
    """
    In folders that contain h5 files and another formats, the
    h5 files are ignored.
    """
    path, files1 = setup_folder_single_phasics_tif()
    path, _files2 = setup_folder_single_h5(tdir=path)
    ds = qpformat.load_data(path)
    for ff in ds.files:
        assert ff in files1
    shutil.rmtree(path, ignore_errors=True)


def test_multiple_formats_error():
    """
    Folders containing two different formats that are not handled
    by test_multiple_formats_phasics_tif_ignore_h5
    and test_multiple_formats_phasics_tif
    should not be supported.
    """
    path, _files2 = setup_folder_single_holo()
    other_fmt_path = path / "single_holo.npy"
    np.save(other_fmt_path, np.zeros((10, 10)))
    try:
        qpformat.load_data(path)
    except qpformat.file_formats.MultipleFormatsNotSupportedError:
        pass
    else:
        assert False, "multiple formats should not be supported"
    shutil.rmtree(path, ignore_errors=True)


def test_series_format_ignored():
    """Series file formats are ignored in SeriesFolder"""
    # combine a zip file with a regular hologram file
    path, _files2 = setup_folder_single_holo()
    bad_path = datapath / "series_phasics.zip"
    shutil.copy2(bad_path, path)
    ds = qpformat.load_data(path)
    assert len(ds) == 2
    assert bad_path not in ds.files
    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    test_multiple_formats_error()
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
