import pathlib

import qpimage

from .file_formats import formats, formats_dict, UnknownFileFormatError, \
    WrongFileFormatError


def guess_format(path):
    """Determine the file format of a folder or a file"""
    for fmt in formats:
        if fmt.verify(path):
            return fmt.__name__
    else:
        msg = "Undefined file format: '{}'".format(path)
        raise UnknownFileFormatError(msg)


def load_data(path, fmt=None, bg_data=None, bg_fmt=None,
              meta_data={}, holo_kw={}, as_type="float32"):
    """Load experimental data

    Parameters
    ----------
    path: str
        Path to experimental data file or folder
    fmt: str
        The file format to use (see `file_formats.formats`).
        If set to `None`, the file format is guessed.
    bg_data: str
        Path to background data file or `qpimage.QPImage`
    bg_fmt: str
        The file format to use (see `file_formats.formats`)
        for the background. If set to `None`, the file format
        is be guessed.
    meta_data: dict
        Meta data (see `qpimage.meta.DATA_KEYS`)
    as_type: str
        Defines the data type that the input data is casted to.
        The default is "float32" which saves memory. If high
        numerical accuracy is required (does not apply for a
        simple 2D phase analysis), set this to double precision
        ("float64").

    Returns
    -------
    dataobj: SeriesData or SingleData
        Object that gives lazy access to the experimental data.
    """
    path = pathlib.Path(path).resolve()
    # sanity checks
    for kk in meta_data:
        if kk not in qpimage.meta.DATA_KEYS:
            msg = "Meta data key not allowed: {}".format(kk)
            raise ValueError(msg)

    if fmt is None:
        fmt = guess_format(path)
    else:
        if not formats_dict[fmt].verify(path):
            msg = "Wrong file format '{}' for '{}'!".format(fmt, path)
            raise WrongFileFormatError(msg)

    dataobj = formats_dict[fmt](path=path,
                                meta_data=meta_data,
                                holo_kw=holo_kw,
                                as_type=as_type)

    if bg_data is not None:
        if isinstance(bg_data, qpimage.QPImage):
            # qpimage instance
            dataobj.set_bg(bg_data)
        else:
            # actual data on disk
            bg_path = pathlib.Path(bg_data).resolve()
            if bg_fmt is None:
                bg_fmt = guess_format(bg_path)
                bgobj = formats_dict[bg_fmt](path=bg_path,
                                             meta_data=meta_data,
                                             holo_kw=holo_kw,
                                             as_type=as_type)
                dataobj.set_bg(bgobj)

    return dataobj
