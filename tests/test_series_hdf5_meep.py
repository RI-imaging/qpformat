import pathlib

import numpy as np
import qpformat
from qpformat.file_formats import WrongFileFormatError


data_dir = pathlib.Path(__file__).parent / "data"


def test_basic():
    ds = qpformat.load_data(data_dir / "series_hdf5_meep.h5")
    qpi = ds.get_qpimage(0)

    assert len(ds) == 18
    # - default wavelength is 500nm
    # - original sampling was 13 px / wavelength
    # - data were shrinked by taking every 8th pixel
    assert np.allclose(qpi["pixel size"], 500e-9 / 13 * 8,
                       rtol=0, atol=1e-9)
    assert qpi.meta["medium index"] == 1.333
    assert qpi.meta["wavelength"] == 500e-9
    assert qpi.meta["focus"] == 500e-9 * 111 / 13
    assert ds.shape == (18, 47, 47)
    assert qpi.meta["angle"] == 0

    qpi2 = ds.get_qpimage(11)
    assert np.allclose(
        qpi2.meta["angle"],
        2 * np.pi / len(ds) * 11,
        atol=1e-6,
        rtol=0)

    assert qpi2.meta["time"] == 11


def test_returned_identifier():
    ds = qpformat.load_data(data_dir / "series_hdf5_meep.h5")
    qpi = ds.get_qpimage(0)
    assert "identifier" in qpi
    qpiraw = ds.get_qpimage_raw(0)
    assert "identifier" in qpiraw


def test_user_defined_wavelength():
    """Special for FDTD data, because it is actually unit-less"""
    ds = qpformat.load_data(data_dir / "series_hdf5_meep.h5",
                            meta_data={"wavelength": 550e-9})
    qpi = ds.get_qpimage(0)

    # - custom wavelength is 550nm
    # - original sampling was 13 px / wavelength
    # - data were shrinked by taking every 8th pixel
    assert np.allclose(qpi["pixel size"], 550e-9 / 13 * 8,
                       rtol=0, atol=1e-9)
    assert qpi.meta["focus"] == 550e-9 * 111 / 13


def test_wrong_format():
    path = data_dir / "single_qpimage.h5"
    try:
        qpformat.load_data(path, fmt="SeriesHDF5SinogramMeep")
    except WrongFileFormatError:
        pass
    else:
        raise ValueError("qpimage data is not meep sinogram data")
