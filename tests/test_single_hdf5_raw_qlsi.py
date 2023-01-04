import pathlib
import numpy as np

import qpformat


data_path = pathlib.Path(__file__).parent / "data"


def test_series_raw_oah():
    ds = qpformat.load_data(data_path / "single_hdf5_raw-qlsi.h5")
    assert len(ds) == 1
    assert ds.format == "SingleRawQLSIQpformatHDF5"
    assert ds.meta_data["wavelength"] == 550e-9
    assert ds.get_qpimage().meta["identifier"] == "3134c"
    qpi = ds.get_qpimage(0)
    assert np.allclose(
        qpi.pha[100:104, 140:142].flatten(),
        [[4.22381783, 4.25115347, 4.27171421, 4.30390024,
          4.29087162, 4.31994677, 4.34381723, 4.36178589]],
        rtol=0,
        atol=1e-7
    )
