import abc

from .series_base import SeriesData


class SingleData(SeriesData):
    """Single data file format base class

    Parameters
    ----------
    path: str or pathlib.Path
        Path to the experimental data file.
    meta_data: dict
        Dictionary containing meta data.
        see :py:class:`qpimage.META_KEYS`.
    as_type: str
        Defines the data type that the input data is casted to.
        The default is "float32" which saves memory. If high
        numerical accuracy is required (does not apply for a
        simple 2D phase analysis), set this to double precision
        ("float64").
    """
    __meta__ = abc.ABCMeta
    is_series = False

    def __len__(self):
        return 1

    def get_identifier(self, idx=0):
        return self.identifier

    def get_name(self, idx=0):
        return super(SingleData, self).get_name(idx=0)

    def get_qpimage(self, idx=0):
        return super(SingleData, self).get_qpimage(idx=0)

    @abc.abstractmethod
    def get_qpimage_raw(self, idx=0):
        """QPImage without background correction"""

    def get_time(self, idx=0):
        """Time of the data

        Returns nan if the time is not defined
        """
        thetime = super(SingleData, self).get_time(idx=0)
        return thetime
