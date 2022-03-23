# flake8: noqa: F401
from .errors import (
    BadFileFormatError, UnknownFileFormatError, WrongFileFormatError)
from .registry import get_format_classes, get_format_dict
from .series_base import SeriesData
from .single_base import SingleData
from .util import hash_obj

# This registers all formats imported in those modules:
from . import fmts_ready, fmts_raw_oah, fmts_raw_qlsi
from . import fmt_series_folder

# sort the formats according to priority
formats = get_format_classes()

# convenience dictionary
formats_dict = get_format_dict()
