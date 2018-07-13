"""Conversion of external holograms to .tif files

Qpformat can load hologram data from .tif image files. If your
experimental hologram data are stored in a different file format,
you can either request its implementation in qpformat by
`creating an issue <https://github.com/RI-imaging/qpformat/issues/new>`__
or you can modify this example script to your needs.

This example must be executed with a directory as an
command line argument, i.e.
``python convert_txt2tif.py /path/to/folder/``
"""
import pathlib
import sys

import numpy as np
from skimage.external import tifffile

# File names ending with these strings are ignored
ignore_endswith = ['.bmp', '.npy', '.opj', '.png', '.pptx', '.py', '.svg',
                   '.tif', '.txt', '_RIdist', '_parameter', '_parameter_old',
                   '_phase', 'n_array', 'n_array_real', '~']
# uncomment this line to keep background hologram files
ignore_endswith += ['_bg']


def get_paths(folder, ignore_endswith=ignore_endswith):
    '''Return hologram file paths

    Parameters
    ----------
    folder: str or pathlib.Path
        Path to search folder
    ignore_endswith: list
        List of filename ending strings indicating which
        files should be ignored.
    '''
    folder = pathlib.Path(folder).resolve()
    files = folder.rglob("*")
    for ie in ignore_endswith:
        files = [ff for ff in files if not ff.name.endswith(ie)]
    return sorted(files)


if __name__ == "__main__":
    path = pathlib.Path(sys.argv[-1])
    if not path.is_dir():
        raise ValueError("Command line argument must be directory!")
    # output directory
    pout = path.parent / (path.name + "_tif")
    pout.mkdir(exist_ok=True)
    # get input hologram files
    files = get_paths(path)
    # conversion
    for ff in files:
        # convert image data to uint8 (most image sensors)
        hol = np.loadtxt(str(ff), dtype=np.uint8)
        tifout = str(pout / (ff.name + ".tif"))
        # compress image data
        tifffile.imsave(tifout, hol, compress=9)
