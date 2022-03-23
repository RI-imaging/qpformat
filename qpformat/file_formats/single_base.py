import abc

from .series_base import SeriesData


class SingleData(SeriesData, abc.ABC):
    """Single data file format base class
    """
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
