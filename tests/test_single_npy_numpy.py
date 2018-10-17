import pathlib
import tempfile

import numpy as np

import qpformat


def test_load_phase():
    # generate test data
    tf = pathlib.Path(tempfile.mktemp(suffix=".npy", prefix="qpformat_test_"))
    phase = np.ones((20, 20), dtype=float)
    phase *= np.linspace(0, .3, 20).reshape(-1, 1)
    np.save(tf, phase)

    ds = qpformat.load_data(tf, as_type="float64")
    assert np.allclose(ds.get_qpimage().pha, phase, atol=1e-15, rtol=0)
    assert ds.path == tf
    assert "SingleNpyNumpy" in ds.__repr__()

    try:
        tf.unlink()
    except OSError:
        pass


def test_load_field():
    # generate test data
    tf = pathlib.Path(tempfile.mktemp(suffix=".npy", prefix="qpformat_test_"))
    phase = np.ones((20, 20), dtype=float)
    phase *= np.linspace(0, .3, 20).reshape(-1, 1)
    amplitude = np.ones((20, 20), dtype=float)
    amplitude += np.linspace(-.1, .12, 20).reshape(1, -1)
    field = amplitude * np.exp(1j * phase)
    np.save(tf, field)

    ds = qpformat.load_data(tf, as_type="float64")
    assert np.allclose(ds.get_qpimage().pha, phase, atol=1e-15, rtol=0)
    assert np.allclose(ds.get_qpimage().amp, amplitude, atol=1e-15, rtol=0)

    try:
        tf.unlink()
    except OSError:
        pass


def test_returned_identifier():
    # generate test data
    tf = pathlib.Path(tempfile.mktemp(suffix=".npy", prefix="qpformat_test_"))
    phase = np.ones((20, 20), dtype=float)
    phase *= np.linspace(0, .3, 20).reshape(-1, 1)
    np.save(tf, phase)

    ds = qpformat.load_data(tf, as_type="float64")
    qpi = ds.get_qpimage(0)
    assert "identifier" in qpi
    qpiraw = ds.get_qpimage_raw(0)
    assert "identifier" in qpiraw

    try:
        tf.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
