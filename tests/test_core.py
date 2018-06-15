import os
import tempfile

import numpy as np
import qpformat.core


def test_wrong_file_format():
    tf = tempfile.mktemp(prefix="qpformat_test_")
    with open(tf, "w") as fd:
        fd.write("test")
    try:
        qpformat.core.guess_format(tf)
    except qpformat.core.UnknownFileFormatError:
        pass
    else:
        assert False, "Unknown file format was loaded!"
    # cleanup
    try:
        os.remove(tf)
    except OSError:
        pass


def test_load_with_bg():
    data = np.ones((20, 20), dtype=float)
    data *= np.linspace(-.1, 3, 20).reshape(-1, 1)
    f_data = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(f_data, data)

    bg_data = np.ones((20, 20), dtype=float)
    bg_data *= np.linspace(0, 1.1, 20).reshape(1, -1)
    f_bg_data = tempfile.mktemp(prefix="qpformat_test_", suffix=".npy")
    np.save(f_bg_data, bg_data)

    ds = qpformat.core.load_data(path=f_data,
                                 bg_data=f_bg_data,
                                 as_type="float64")
    qpi = ds.get_qpimage()
    assert np.allclose(qpi.pha, data - bg_data, atol=1e-15, rtol=0)
    # cleanup
    try:
        os.remove(f_data)
        os.remove(f_bg_data)
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
