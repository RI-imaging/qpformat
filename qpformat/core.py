from .file_formats import formats, formats_dict, UnknownFileFormatError


def guess_format(path):
    """Determine the file format of a folder or a file"""
    for fmt in formats:
        if fmt.verify(path):
            return fmt.__name__
    else:
        raise UnknownFileFormatError(path)


def load_data(path, fmt=None, bg_path=None, bg_fmt=None,
              meta_data={}, h5out=None):
    """Load experimental data

    Parameters
    ----------
    path: str
        Path to experimental data file or folder
    fmt: str
        The file format to use (see `file_formats.formats`).
        If set to `None`, the file format is be guessed.
    bg_path: str
        Path to background data file.
    bg_fmt: str
        The file format to use (see `file_formats.formats`)
        for the background. If set to `None`, the file format
        is be guessed.
    meta_data: dict
        Meta data (see `qpimage.meta.VALID_META_KEYS`)
    h5out: str
        Path to an hdf5 output file where all data
        is written in the :py:mod:`qpimage` data
        file format. If set to `None`, nothing
        is written to disk.

    Returns
    -------
    dataobj: `file_formats.Group` or `file_formats.Single`
        A qpformat data object with unified access to the
        experimental data.
    """
    if fmt is None:
        fmt = guess_format(path)

    dataobj = formats_dict[fmt](path=path, meta_data=meta_data)

    if bg_path is not None:
        if bg_fmt is None:
            bg_fmt = guess_format(bg_path)
        bgobj = formats_dict[bg_fmt](path=bg_path, meta_data=meta_data)
        dataobj.set_bg(bgobj)

    if h5out is not None:
        # TODO:
        # - store data in h5file using qimage
        pass

    return dataobj
