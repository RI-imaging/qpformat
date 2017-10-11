import abc

class Group(object):
    __meta__ = abs.ABCMeta

    @abc.abstractmethod    
    def verify(path):
        """Verify that `path` has this file format

        Returns `True` if the file format matches.
        """

