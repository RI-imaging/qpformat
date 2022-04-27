import pathlib
import shutil

import h5py

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_series_raw_qlsi(tmp_path):
    # create a fake series file
    source = datapath / "single_hdf5_raw-qlsi.h5"
    dest = tmp_path / "series_hdf5_raw-qlsi.h5"
    shutil.copy2(source, dest)
    with h5py.File(dest, "a") as h5:
        h5["1"] = h5["0"][:]
        for key in h5["0"].attrs:
            value = h5["0"].attrs[key]
            if key == "time":
                value += 10
            h5["1"].attrs[key] = value

    ds = qpformat.load_data(dest)
    assert ds.format == "SeriesRawQLSIQpformatHDF5"
    assert len(ds) == 2
    qpi1 = ds.get_qpimage(0)
    qpi2 = ds.get_qpimage(1)
    assert qpi1.meta["wavelength"] == 550e-9
    assert qpi1.meta["identifier"] == "f846b:1"
    assert qpi1.meta["time"] == 948.64
    assert qpi2.meta["time"] == 958.64
