from . import file_formats


def load_data(path, fmt=None, h5out=None)
    """Load experimental data
    
    Parameters
    ----------
    path: str
        Path to experimental data file or folder
    fmt: str
        The file format to use (see `file_formats.formats`).
        If set to `None`, the file format will be guessed.
    h5out: str
        Path to an hdf5 output file where all data
        will be written. If set to `None`, nothing
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

    dataobj = file_formats.formats_dict[fmt](path)

    if h5out is not None:
        # TODO:
        # - store data in h5file using qimage
        pass

    return dataobj
