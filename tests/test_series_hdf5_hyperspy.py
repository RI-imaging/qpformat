import os
import pathlib
import tempfile
import shutil
import warnings

import h5py
from skimage.external import tifffile

import qpformat
from qpformat.file_formats import WrongFileFormatError
from qpformat.file_formats.series_hdf5_hyperspy import (
    HyperSpyNoDataFoundError, WrongSignalTypeWarnging)

datapath = pathlib.Path(__file__).parent / "data"


def make_hyperspy(signal_type="hologram"):
    """Create a basic hyperspy file"""
    tifin = datapath / "single_holo.tif"
    with tifffile.TiffFile(os.fspath(tifin)) as tf:
        data = tf.pages[0].asarray()
    tdir = pathlib.Path(tempfile.mkdtemp(prefix="qpformat_test_hyperspy"))
    hspyf = tdir / "test.h5"
    with h5py.File(hspyf, mode="w") as h5:
        h5.attrs["file_format"] = "hyperspy"
        exp = h5.create_group("Experiments")
        hol = exp.create_group("Hologram of an HL60 cell")
        hol.create_dataset(name="data", data=data)
        # signal
        sig = hol.create_group("metadata/Signal")
        sig.attrs["signal_type"] = signal_type
        # set pixel size
        for name in ["axis-0", "axis-1"]:
            axi = hol.create_group(name)
            axi.attrs["scale"] = 107
            axi.attrs["units"] = "nm"

    return tdir, hspyf


def test_basic():
    tdir, hspyf = make_hyperspy()
    ds = qpformat.load_data(hspyf)
    qpi = ds.get_qpimage(0)

    assert len(ds) == 1
    assert qpi["pixel size"] == 0.107e-6

    shutil.rmtree(path=tdir, ignore_errors=True)


def test_returned_identifier():
    tdir, hspyf = make_hyperspy()
    ds = qpformat.load_data(hspyf)
    qpi = ds.get_qpimage(0)
    assert "identifier" in qpi
    qpiraw = ds.get_qpimage_raw(0)
    assert "identifier" in qpiraw
    shutil.rmtree(path=tdir, ignore_errors=True)


def test_wrong_format():
    path = datapath / "single_qpimage.h5"
    try:
        qpformat.load_data(path, fmt="SeriesHdf5HyperSpy")
    except WrongFileFormatError:
        pass
    else:
        raise ValueError("qpimage data is not hyperspy data")


def test_wrong_signal_type():
    tdir, hspyf = make_hyperspy(signal_type="unknown")
    ds = qpformat.load_data(hspyf)

    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        # Trigger a warning.
        try:
            ds.get_qpimage(0)
        except HyperSpyNoDataFoundError:
            pass
        else:
            raise ValueError("Error due to wrong signal type")

        # Verify some things
        assert len(w) == 1
        assert issubclass(w[-1].category, WrongSignalTypeWarnging)
        assert "unknown" in str(w[-1].message)

    shutil.rmtree(path=tdir, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
