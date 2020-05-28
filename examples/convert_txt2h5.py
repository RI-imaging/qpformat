r"""Conversion of external file formats to qpimage .h5 files

Sometimes the data recorded are not in a file format supported
by qpformat or it is not feasible to implement a reader
class for a very unique data set. In this example, QPI data,
stored as a tuple of files ("\*_intensity.txt" and "\*_phase.txt")
with commas as decimal separators, are converted to the qpimage
file format which is supported by qpformat.

This example must be executed with a directory as an
command line argument, i.e.
``python convert_txt2npy.py /path/to/folder/``
"""
import pathlib
import sys

import numpy as np
import qpimage


def get_paths(folder):
    '''Return *_phase.txt files in `folder`'''
    folder = pathlib.Path(folder).resolve()
    files = folder.rglob("*_phase.txt")
    return sorted(files)


def load_file(path):
    '''Load a txt data file'''
    path = pathlib.Path(path)
    data = path.open().readlines()
    # remove comments and empty lines
    data = [ll for ll in data if len(ll.strip()) and not ll.startswith("#")]
    # determine data shape
    n = len(data)
    m = len(data[0].strip().split())
    res = np.zeros((n, m), dtype=np.dtype(float))
    # write data to array, replacing comma with point decimal separator
    for ii in range(n):
        res[ii] = np.array(data[ii].strip().replace(",", ".").split(),
                           dtype=float)
    return res


def convert_qpi(path_in, path_out, meta):
    '''Load QPI data using *_phase.txt files and write qpimage .h5 file'''
    path = pathlib.Path(path_in)
    phase = load_file(path)
    inten = load_file(path.parent / (path.name[:-10] + "_intensity.txt"))
    ampli = np.sqrt(inten)
    with qpimage.QPImage(data=(phase, ampli),
                         which_data="phase,amplitude",
                         h5file=path_out,
                         meta_data=meta,
                         h5mode="w"):
        pass


if __name__ == "__main__":
    path = pathlib.Path(sys.argv[-1])
    meta = {"medium index": float(input("medium index: ")),
            "wavelength": float(input("wavelength [nm]: ")) * 1e-9,
            "pixel size": float(input("pixel size [µm]: ")) * 1e-6,
            }
    path = pathlib.Path(sys.argv[-1])
    if not path.is_dir():
        raise ValueError("Command line argument must be directory!")
    # output directory
    pout = path.parent / (path.name + "_h5")
    pout.mkdir(exist_ok=True)
    # get input *_phase.txt files
    files = get_paths(path)
    # conversion
    for ff in files:
        field = convert_qpi(ff, pout / (ff.name[:-10] + ".h5"), meta)
