from . import file_formats


def load_data(path, fmt=None, bg_path=None, bg_fmt=None,
              h5out=None):
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
    h5out: str
        Path to an hdf5 output file where all data
        is written in the :py:mod:`qpimage` data
        file format. If set to `None`, nothing
        is written to disk.
    meta_data: dict
        Meta data (see `qpimage.meta.VALID_META_KEYS`)
    
    Returns
    -------
    dataobj: `file_formats.Group` or `file_formats.Single`
        A qpformat data object with unified access to the
        experimental data.
    """
    if fmt is None:
        fmt = file_formats.guess_format(path)
    if bg_fmt is None and bg_path is not None:
        bg_fmt = file_formats.guess_format(bg_path)

    dataobj = file_formats.formats_dict[fmt](path)
    bgobj = file_formats.formats_dict[bg_fmt](bg_path)
    dataobj.set_bg(bgobj)

    if h5out is not None:
        # TODO:
        # - store data in h5file using qimage
        pass

    return dataobj
