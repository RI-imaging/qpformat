import inspect

from .series_base import SeriesData


def get_format_classes(base_class=SeriesData):
    """Recursively get all subclasses that are not abstract"""
    # get a list of formats
    formats_unsrt = []
    for cls in base_class.__subclasses__():
        if not inspect.isabstract(cls):
            formats_unsrt.append(cls)
        formats_unsrt += get_format_classes(base_class=cls)
    # sort according to priority
    return sorted(formats_unsrt, key=lambda x: x.priority)


def get_format_dict():
    formats_dict = {}
    for fmt in get_format_classes():
        formats_dict[fmt.__name__] = fmt
    return formats_dict
