import abc
import copy
import functools
import hashlib

import qpimage


class SeriesData(object):
    __meta__ = abc.ABCMeta
    is_series = True

    def __init__(self, path, meta_data={}):
        """Experimental data set

        Parameters
        ----------
        path: str
            path to the experimental data file.
        meta_data: dict
            dictionary containing meta data.
            see :py:class:`qpimage.META_KEYS`.
        """
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

    @property
    @functools.lru_cache(maxsize=32)
    def identifier(self):
        """Return a unique identifier for the given data set"""
        data = []
        with open(self.path, "rb") as fd:
            data.append(fd.read(50 * 1024))
        for key in sorted(list(self.meta_data.keys())):
            value = self.meta_data[key]
            data.append("{}={}".format(key, value).encode("utf-8"))
        idsum = hashlib.md5(b"".join(data)).hexdigest()[:5]
        return idsum

    def get_identifier(self, idx):
        """Return an identifier for the data at index `idx`"""
        return "{}:{}".format(self.identifier, idx)

    def get_name(self, idx):
        """Return name of data at index `idx`"""
        return "{}:{}".format(self.path, idx)

    def get_qpimage(self, idx):
        """Return background-corrected QPImage of data at index `idx`"""
        # raw data
        qpi = self.get_qpimage_raw(idx)
        # bg data
        if self._bgdata:
            if len(self._bgdata) == 1:
                # One background for all
                bgidx = 0
            else:
                bgidx = idx

            if isinstance(self._bgdata, SeriesData):
                # `get_qpimage` does take `idx`
                bg = self._bgdata.get_qpimage_raw(bgidx)
            else:
                # `self._bgdata` is a QPImage
                bg = self._bgdata[bgidx]
            qpi.set_bg_data(bg_data=bg)
        # set identifier
        qpi["identifier"] = self.get_identifier(idx)
        return qpi

    @abc.abstractmethod
    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction"""

    def get_time(self, idx):
        """Return time of data at index `idx`

        """
        # raw data
        qpi = self.get_qpimage_raw(idx)
        if "time" in qpi.meta:
            thetime = qpi.meta["time"]
        else:
            thetime = 0
        return thetime

    def saveh5(self, h5file):
        """Save the data set as an hdf5 file (QPImage format)"""
        with qpimage.QPSeries(h5file=h5file,
                              h5mode="w",
                              identifier=self.identifier) as qps:
            for ii in range(len(self)):
                qpi = self.get_qpimage(ii)
                qps.add_qpimage(qpi)

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
            self._bgdata = dataset
        elif (isinstance(dataset, SeriesData) and
              (len(dataset) == 1 or
               len(dataset) == len(self))):
            # DataSet
            self._bgdata = dataset
        else:
            raise ValueError("Bad length or type for bg: {}".format(dataset))

    @staticmethod
    @abc.abstractmethod
    def verify(path):
        """Verify that `path` has this file format

        Returns `True` if the file format matches.
        The implementation of this method should be fast and
        memory efficient, because e.g. the "GroupFolder" file
        format depends on it.
        """


class SingleData(SeriesData):
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
        """Time of QPImage"""
        return super(SingleData, self).get_time(idx=0)
