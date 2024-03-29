import pathlib
import shutil
import tempfile
import zipfile

import numpy as np
import qpformat

data_path = pathlib.Path(__file__).parent / "data"


def assert_path_in_list(path, path_list):
    for ff in path_list:
        if path.samefile(ff):
            break
    else:
        assert False, "{} not in {}".format(path, path_list)


def setup_folder_single_h5(size=2, tdir=None):
    path = data_path / "single_qpimage.h5"
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
    path = data_path / "single_holo.tif"
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
    path = data_path / "series_phasics.zip"
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
    for f1 in ds.files:
        assert_path_in_list(f1, files)
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
    assert np.isnan(ds.get_metadata(0).get('time', np.nan)
                    ), "no time defined in original file"
    # format should be right
    assert ds.verify(ds.path)
    assert ds.__class__.__name__ == "SeriesFolder"


def test_multiple_formats_phasics_tif():
    """
    Folders with phasics tif files sometimes contain raw tif files.
    This test makes sure the raw files are ignored
    """
    path, files = setup_folder_single_phasics_tif()
    ds = qpformat.load_data(path)
    for ff in ds.files:
        assert_path_in_list(ff, files)
    assert ds.verify(ds.path)
    assert ds.__class__.__name__ == "SeriesFolder"


def test_multiple_formats_phasics_tif_ignore_h5():
    """
    In folders that contain h5 files and another formats, the
    h5 files are ignored.
    """
    path, files1 = setup_folder_single_phasics_tif()
    path, _files2 = setup_folder_single_h5(tdir=path)
    ds = qpformat.load_data(path)
    for ff in ds.files:
        assert_path_in_list(ff, files1)


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
    except qpformat.file_formats.fmt_series_folder.\
            MultipleFormatsNotSupportedError:
        pass
    else:
        assert False, "multiple formats should not be supported"


def test_series_format_qpretrieve_kw():
    """Siedband kwarg should be passed to subformats"""
    path, _files2 = setup_folder_single_holo()
    ds1 = qpformat.load_data(path, qpretrieve_kw={"invert_phase": False})
    ds2 = qpformat.load_data(path, qpretrieve_kw={"invert_phase": True})
    p1 = ds1.get_qpimage(0)
    p2 = ds2.get_qpimage(0)
    assert np.all(p1.pha + p2.pha == 0)


def test_series_in_folder_format():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="qpformat_"))
    path = data_path / "series_phasics.zip"
    shutil.copy2(path, tmp / "1.zip")
    shutil.copy2(path, tmp / "2.zip")
    ds1 = qpformat.load_data(tmp / "1.zip")
    ds_d = qpformat.load_data(tmp)
    assert len(ds1) * 2 == len(ds_d)
    for ii in range(len(ds1)):
        print(ii)
        assert np.all(ds1.get_qpimage(ii).pha == ds_d.get_qpimage(ii).pha)
        assert np.all(ds1.get_qpimage(ii).pha
                      == ds_d.get_qpimage(ii + len(ds1)).pha)
