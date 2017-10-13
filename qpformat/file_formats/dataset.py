import abc
import copy

import qpimage


class DataSet(object):
    __meta__ = abc.ABCMeta

    def __init__(self, path, meta_data={}):
        self.path = path
        self.meta_data = copy.copy(meta_data)
        self._bgdata = []

    def __repr__(self):
        rep = "QPFormat '{}'".format(self.__class__.__name__) \
              + ", {} event(s)".format(len(self)) \
              + "\nfile: {}".format(self.path)

        meta = []
        if "wavelength" in self.meta_data:
            wl = self.meta_data["wavelength"]
            if wl < 2000e-9 and wl > 10e-9:
                # convenience for light microscopy
                meta.append("λ={:.1f}nm".format(wl * 1e9))
            else:
                meta.append("λ={:.2e}m".format(wl))
        if "pixel size" in self.meta_data:
            pxm = self.meta_data["pixel size"]
            if pxm < 1e-3 and pxm > 1e-8:
                # convenience for light microscopy
                meta.append("1px={}µm".format(pxm * 1e6))
            else:
                meta.append("1px={}m".format(pxm))
        rep += ", ".join(meta)
        return rep

    @abc.abstractmethod
    def __len__(self):
        """Return number of samples of a data set"""

    def get_name(self, idx):
        """Return name of data at index `idx`"""
        return "{} [{}]".format(self.path, idx)

    def get_qpimage(self, idx):
        """Return background-corrected QPImage of data at index `idx`"""
        # raw data
        qpi = self.get_qpimage_raw(idx)
        # bg data
        if len(self._bgdata) == 1:
            # One background for all
            bgidx = 0
        else:
            bgidx = idx

        if isinstance(self._bgdata, DataSet):
            bg = self._bgdata.get_qpimage_raw(bgidx)
        else:
            bg = self._bgdata[bgidx]
        qpi.set_bg(bg_data=bg)
        return qpi

    @abc.abstractmethod
    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""

    def get_time(self, idx):
        """Return time of data at in dex `idx`

        By default, this returns zero and must be
        overridden if the file format supports timing.
        """
        return 0

    def saveh5(self, h5file):
        """Save the data set as an hdf5 file (QPImage format)"""

    def set_bg(self, dataset):
        """Set background data

        Parameters
        ----------
        dataset: `DataSet` or `qpimage.QPImage`
            If the ``len(dataset)`` matches ``len(self)``,
            then background correction is performed
            element-wise. Otherwise, ``len(dataset)``
            must be one and is used for all data of ``self``.

        See Also
        --------
        get_qpimage: obtain the background corrected QPImage
        """

        if isinstance(dataset, qpimage.QPImage):
            # Single QPImage
            self._bgdata = [dataset]
        elif (isinstance(dataset, list) and
              len(dataset) == len(self) and
              isinstance(dataset[0], qpimage.QPImage)):
            # List of QPImage
            self.bgdata = dataset
        elif (isinstance(dataset, DataSet) and
              (len(dataset) == 1 or
               len(dataset) == len(self))):
            # DataSet
            self.bgdata = dataset
        else:
            raise ValueError("Bad length or type for bg: {}".format(dataset))
        self._bgdata = dataset

    @staticmethod
    @abc.abstractmethod
    def verify(path):
        """Verify that `path` has this file format

        Returns `True` if the file format matches.
        """
