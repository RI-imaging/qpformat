"""Conversion of external file formats to .npy files

Sometimes the data recorded are not in a file format supported
by qpformat or it is not feasible to implement a reader
class for a very unique data set. In this example, QPI data,
stored as a tuple of files ("\*_intensity.txt" and "\*_phase.txt")
with commas as decimal separators, are converted to the numpy
file format which is supported by qpformat.

This example must be executed with a directory as an
command line argument, i.e.
``python convert_txt2npy.py /path/to/folder/``
"""
import pathlib
import sys

import numpy as np


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
    data = [l for l in data if len(l.strip()) and not l.startswith("#")]
    # determine data shape
    n = len(data)
    m = len(data[0].strip().split())
    res = np.zeros((n, m), dtype=np.dtype(float))
    # write data to array, replacing comma with point decimal separator
    for ii in range(n):
        res[ii] = np.array(data[ii].strip().replace(",", ".").split(),
                           dtype=float)
    return res


def load_field(path):
    '''Load QPI data using *_phase.txt files'''
    path = pathlib.Path(path)
    phase = load_file(path)
    inten = load_file(path.parent / (path.name[:-10] + "_intensity.txt"))
    ampli = np.sqrt(inten)
    return ampli * np.exp(1j * phase)


if __name__ == "__main__":
    path = pathlib.Path(sys.argv[-1])
    if not path.is_dir():
        raise ValueError("Command line argument must be directory!")
    # output directory
    pout = path.parent / (path.name + "_npy")
    pout.mkdir(exist_ok=True)
    # get input *_phase.txt files
    files = get_paths(path)
    # conversion
    for ff in files:
        field = load_field(ff)
        np.save(str(pout / (ff.name[:-10] + ".npy")), field)
