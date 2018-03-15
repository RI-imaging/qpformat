import abc
import copy
import functools
import hashlib

import numpy as np
import qpimage


class SeriesData(object):
    __meta__ = abc.ABCMeta
    is_series = True

    def __init__(self, path, meta_data={}, holo_kw={}):
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
        self.holo_kw = holo_kw
        self._bgdata = []
        #: Unique string that identifies the background data that
        #: was set using `set_bg`.
        self.background_identifier = None

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

    def _compute_bgid(self, bg=None):
        """Return a unique identifier for the background data"""
        if bg is None:
            bg = self._bgdata
        if isinstance(bg, qpimage.QPImage):
            # Single QPImage
            if "identifier" in bg:
                return bg["identifier"]
            else:
                data = [bg.amp, bg.pha]
                for key in sorted(list(bg.meta.keys())):
                    val = bg.meta[key]
                    data.append("{}={}".format(key, val))
                return hash_obj(data)
        elif (isinstance(bg, list) and
              isinstance(bg[0], qpimage.QPImage)):
            # List of QPImage
            data = []
            for bgii in bg:
                data.append(self._compute_bgid(bgii))
            return hash_obj(data)
        elif (isinstance(bg, SeriesData) and
              (len(bg) == 1 or
               len(bg) == len(self))):
            # DataSet
            return bg.identifier
        else:
            raise ValueError("Unknown background data type: {}".format(bg))

    @functools.lru_cache(maxsize=32)
    def _identifier_data(self):
        data = []
        # data
        with open(self.path, "rb") as fd:
            data.append(fd.read(50 * 1024))
        data += self._identifier_meta()
        return hash_obj(data)

    @functools.lru_cache(maxsize=32)
    def _identifier_meta(self):
        data = []
        # meta data
        for key in sorted(list(self.meta_data.keys())):
            value = self.meta_data[key]
            data.append("{}={}".format(key, value))
        # hologram info
        for key in sorted(list(self.holo_kw.keys())):
            value = self.holo_kw[key]
            data.append("{}={}".format(key, value))
        return hash_obj(data)

    @property
    def identifier(self):
        """Return a unique identifier for the given data set"""
        if self.background_identifier is None:
            return self._identifier_data()
        else:
            idsum = hash_obj([self._identifier_data(),
                              self.background_identifier])
            return idsum[:5]

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
                if ii == 0 or len(self._bgdata) != 1:
                    # initial image or series data where each image
                    # has a unique background image
                    qpi = self.get_qpimage(ii)
                    qps.add_qpimage(qpi)
                else:
                    # hard-link the background data
                    qpiraw = self.get_qpimage_raw(ii)
                    qps.add_qpimage(qpiraw, bg_from_idx=0)

    def set_bg(self, dataset):
        """Set background data

        Parameters
        ----------
        dataset: `DataSet`, `qpimage.QPImage`, or int
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

        self.background_identifier = self._compute_bgid()

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


def hash_obj(data, maxlen=5):
    hasher = hashlib.md5()
    for dd in data:
        tohash = obj2bytes(dd)
        hasher.update(tohash)
    return hasher.hexdigest()[:maxlen]


def obj2bytes(data):
    tohash = []
    if isinstance(data, (tuple, list)):
        for item in data:
            tohash.append(obj2bytes(item))
    elif isinstance(data, str):
        tohash.append(data.encode("utf-8"))
    elif isinstance(data, bytes):
        tohash.append(data)
    elif isinstance(data, np.ndarray):
        tohash.append(data.tobytes())
    else:
        msg = "No rule to convert to bytes: {}".format(data)
        raise NotImplementedError(msg)
    return b"".join(tohash)
