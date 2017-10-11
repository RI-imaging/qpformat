import abc
import copy


class DataSet(object):
    __meta__ = abs.ABCMeta

    def __init__(self, path, meta_data):
        self.path = path
        self.meta_data = copy.copy(meta_data)

    def __repr__(self):
        # class name
        # path
        # length
        # if present:
        #  - resolution
        #  - wavelength
        pass

    def __len__(self):
        return len(self.data)

    @abc.abstractmethod    
    def verify(path):
        """Verify that `path` has this file format

        Returns `True` if the file format matches.
        """
    
    def get_data(self, idx):
        pass
    
    def get_time(self, idx):
        return 0
    
    def set_bg(self, dataset):
        """Set background data
        
        Parameters
        ----------
        dataset: `DataSet` or `qpimage.QPImage`
        """
        pass
    
    