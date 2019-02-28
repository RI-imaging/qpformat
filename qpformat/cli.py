"""command line interface"""
import argparse
import pathlib

from .core import load_data
from .file_formats import UnknownFileFormatError


def qpinfo():
    """Print information of a quantitative phase imaging dataset"""
    parser = qpinfo_parser()
    args = parser.parse_args()

    path = pathlib.Path(args.path).resolve()
    try:
        ds = load_data(path)
    except UnknownFileFormatError:
        print("Unknown file format: {}".format(path))
        return

    print("{} ({})".format(ds.__class__.__doc__, ds.__class__.__name__))
    print("- number of images: {}".format(len(ds)))
    for key in ds.meta_data:
        print("- {}: {}".format(key, ds.meta_data[key]))


def qpinfo_parser():
    descr = "Show information about a quantitative phase imaging dataset"
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('path', metavar='path', type=str,
                        help='Data path')
    return parser
