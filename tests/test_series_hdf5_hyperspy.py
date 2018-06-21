import os
import pathlib
import tempfile
import shutil

import h5py
from skimage.external import tifffile

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def make_hyperspy():
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
        sig.attrs["signal_type"] = "hologram"
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

    assert qpi["pixel size"] == 0.107e-6

    shutil.rmtree(path=tdir, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
