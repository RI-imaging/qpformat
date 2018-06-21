"""
This test uses a cropped version of an original phasics tif file
(data/single_phasics.tif), which was created using this script
(the tags are important):

    import tifffile

    a = tifffile.TiffFile("in.tif")

    x1 = 100
    x2 = 180
    y1 = 140
    y2 = 260

    for ii in range(3):
        data = a.pages[ii].asarray()[x1:x2, y1:y2]

        extratags = []
        for tag in ["61237",
                    "61238",
                    "61239",
                    "61240",
                    "61241",
                    "61242",
                    "61243",
                    "max_sample_value",
                    "min_sample_value",
                    ]:
            tag = a.pages[ii].tags[tag]
            extratags.append((tag.code,
                              tag.dtype.strip("1234567890"),
                              1,
                              tag.value,
                              False))

        tifffile.imsave(file="single_phasics.tif",
                        data=data,
                        extratags=extratags,
                        append=True)
"""
import pathlib

import numpy as np

import qpformat


datapath = pathlib.Path(__file__).parent / "data"


def test_load_data():
    path = datapath / "single_phasics.tif"
    ds = qpformat.load_data(path)
    assert pathlib.Path(ds.path) == path.resolve()
    assert "SingleTifPhasics" in ds.__repr__()


def test_data_content():
    path = datapath / "single_phasics.tif"
    ds = qpformat.load_data(path)
    assert ds.get_time() == 1461951095.00827
    qpi = ds.get_qpimage()
    assert qpi.meta["wavelength"] == 550e-9
    assert np.allclose(qpi.amp.max(), 188.57930365845519)
    assert np.allclose(qpi.pha.max() - qpi.pha.min(), 4.1683941115690617)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
