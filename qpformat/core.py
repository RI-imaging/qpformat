import pathlib

import qpimage

from .file_formats import formats, formats_dict, UnknownFileFormatError


def guess_format(path):
    """Determine the file format of a folder or a file"""
    for fmt in formats:
        if fmt.verify(str(path)):
            return fmt.__name__
    else:
        raise UnknownFileFormatError(str(path))


def load_data(path, fmt=None, bg_data=None, bg_fmt=None,
              meta_data={}, holo_kw={}):
    """Load experimental data

    Parameters
    ----------
    path: str
        Path to experimental data file or folder
    fmt: str
        The file format to use (see `file_formats.formats`).
        If set to `None`, the file format is be guessed.
    bg_data: str
        Path to background data file or `qpimage.QPImage`
    bg_fmt: str
        The file format to use (see `file_formats.formats`)
        for the background. If set to `None`, the file format
        is be guessed.
    meta_data: dict
        Meta data (see `qpimage.meta.DATA_KEYS`)

    Returns
    -------
    dataobj: `file_formats.Group` or `file_formats.Single`
        A qpformat data object with unified access to the
        experimental data.
    """
    path = pathlib.Path(path).resolve()
    # sanity checks
    for kk in meta_data:
        if kk not in qpimage.meta.DATA_KEYS:
            msg = "Meta data key not allowed: {}".format(kk)
            raise ValueError(msg)

    if fmt is None:
        fmt = guess_format(path)

    dataobj = formats_dict[fmt](path=str(path),
                                meta_data=meta_data,
                                holo_kw=holo_kw)

    if bg_data is not None:
        if isinstance(bg_data, qpimage.QPImage):
            # qpimage instance
            dataobj.set_bg(bg_data)
        else:
            # actual data on disk
            bg_path = pathlib.Path(bg_data).resolve()
            if bg_fmt is None:
                bg_fmt = guess_format(bg_path)
                bgobj = formats_dict[bg_fmt](
                    path=str(bg_path), meta_data=meta_data)
                dataobj.set_bg(bgobj)

    return dataobj
