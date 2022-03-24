import abc
import copy
import functools
import io
import pathlib
import warnings

import numpy as np
import qpimage

from .util import hash_obj


class SeriesData(object):
    """Series data file format base class
    """
    __meta__ = abc.ABCMeta
    is_series = True
    priority = 0  # decrease to get higher priority

    def __init__(self, path, meta_data=None, holo_kw=None, qpretrieve_kw=None,
                 as_type="float32"):
        """
        Parameters
        ----------
        path: str or pathlib.Path
            Path to the experimental data file.
        meta_data: dict
            Dictionary containing meta data.
            see :py:class:`qpimage.META_KEYS`.
        holo_kw: dict
            Deprecated, please use `qpretrieve_kw` instead!
        qpretrieve_kw: dict
            Keyword arguments passed to
            :ref:`qpretrieve <qpretrieve:index>` for
            phase retrieval from interferometric data.
        as_type: str
            Defines the data type that the input data is casted to.
            The default is "float32" which saves memory. If high
            numerical accuracy is required (does not apply for a
            simple 2D phase analysis), set this to double precision
            ("float64").
        """
        if qpretrieve_kw is None:
            qpretrieve_kw = {}

        if holo_kw is not None:
            warnings.warn(
                "`holo_kw` is deprecated! Please use `qpretrieve_kw` instead",
                DeprecationWarning)
            # map deprecated parameters to `qpretrieve_kw`
            for key in holo_kw:
                if key == "sideband":
                    if holo_kw[key] in [-1, 1]:
                        qpretrieve_kw["invert_phase"] = holo_kw[key] == -1
                    else:
                        qpretrieve_kw["sideband_freq"] = tuple(holo_kw[key])
                        qpretrieve_kw["invert_phase"] = False
                elif key == "zero_pad":
                    qpretrieve_kw["padding"] = holo_kw["zero_pad"]
                else:
                    qpretrieve_kw[key] = holo_kw[key]

        if meta_data is None:
            meta_data = {}

        #: Enforced dtype via keyword arguments
        self.as_type = as_type
        if isinstance(path, io.IOBase):
            # io.IOBase
            self.path = path
        else:
            #: pathlib.Path to data file or io.IOBase
            self.path = pathlib.Path(path).resolve()

        # check for valid metadata keys
        for key in meta_data:
            if key not in qpimage.meta.META_KEYS:
                msg = "Invalid metadata key `{}`!".format(key) \
                      + "Valid keys: {}".format(sorted(qpimage.meta.META_KEYS))
                raise ValueError(msg)
        #: Enforced metadata via keyword arguments
        self.meta_data = copy.copy(meta_data)
        #: Keyword arguments for interferometric phase retrieval
        self.qpretrieve_kw = qpretrieve_kw
        self._bgdata = []
        #: Unique string that identifies the background data that
        #: was set using `set_bg`.
        self.background_identifier = None
        #: the file format name
        self.format = self.__class__.__name__

    def __repr__(self):
        rep = f"<qpformat {self.format} '{self.path}'" \
              + f", {len(self)} image" \
              + ("s " if len(self) > 1 else " ") \
              + f"at {hex(id(self))}>"

        meta = []
        if "wavelength" in self.meta_data:
            wl = self.meta_data["wavelength"]
            if 2000e-9 > wl > 10e-9:
                # convenience for light microscopy
                meta.append(f"λ={wl * 1e9:.1f}nm")
            else:
                meta.append(f"λ={wl:.2e}m")
        if "pixel size" in self.meta_data:
            pxm = self.meta_data["pixel size"]
            if 1e-3 > pxm > 1e-8:
                # convenience for light microscopy
                meta.append(f"1px={pxm * 1e6}µm")
            else:
                meta.append(f"1px={pxm}m")
        rep = ", ".join([rep] + meta)
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
        if isinstance(self.path, io.IOBase):
            self.path.seek(0)
            data.append(self.path.read(50 * 1024))
        else:
            with self.path.open("rb") as fd:
                data.append(fd.read(50 * 1024))
            data.append(self.path.stat().st_size)
        data += self._identifier_meta()
        return hash_obj(data)

    @functools.lru_cache(maxsize=32)
    def _identifier_meta(self):
        data = []
        # meta data
        for key in sorted(list(self.meta_data.keys())):
            value = self.meta_data[key]
            data.append("{}={}".format(key, value))
        # qpretrieve keywords
        for key in sorted(list(self.qpretrieve_kw.keys())):
            data.append(f"{key}={self.qpretrieve_kw[key]}")
        return hash_obj(data)

    @property
    def identifier(self):
        """Return a unique identifier for the given data set"""
        if self.background_identifier is None:
            idsum = self._identifier_data()
        else:
            idsum = hash_obj([self._identifier_data(),
                              self.background_identifier])
        return idsum

    @property
    @functools.lru_cache()
    def shape(self):
        """Return dataset shape (lenght, image0, image1).

        This should be overridden by the subclass, because by default
        the first qpimage is used for that.
        """
        qpi0 = self.get_qpimage_raw(0)
        return len(self), qpi0.shape[0], qpi0.shape[1]

    def get_identifier(self, idx):
        """Return an identifier for the data at index `idx`

        .. versionchanged:: 0.4.2
            indexing starts at 1 instead of 0
        """
        return "{}:{}".format(self.identifier, idx + 1)

    def get_name(self, idx):
        """Return name of data at index `idx`

        .. versionchanged:: 0.4.2
            indexing starts at 1 instead of 0
        """
        return "{}:{}".format(self.path, idx + 1)

    def get_time(self, idx):
        """Return time of data at index `idx`

        Returns nan if the time is not defined"""
        # raw data
        qpi = self.get_qpimage_raw(idx)
        if "time" in qpi.meta:
            thetime = qpi.meta["time"]
        else:
            thetime = np.nan
        return thetime

    def get_qpimage(self, idx):
        """Return background-corrected QPImage of data at index `idx`"""
        # raw data
        qpi = self.get_qpimage_raw(idx)
        if "identifier" not in qpi:
            msg = "`get_qpimage_raw` does not set 'identifier' " \
                  + "in class '{}'!".format(self.__class__)
            raise KeyError(msg)
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
        return qpi

    @abc.abstractmethod
    def get_qpimage_raw(self, idx):
        """Return QPImage without background correction

        Note that this method must always return a QPImage instance with
        the "identifier" metadata key set!
        """

    def saveh5(self, h5file, qpi_slice=None, series_slice=None,
               time_interval=None, count=None, max_count=None):
        """Save the data set as an HDF5 file (qpimage.QPSeries format)

        Parameters
        ----------
        h5file: str, pathlib.Path, or h5py.Group
            Where to store the series data
        qpi_slice: tuple of (slice, slice)
            If not None, only store a slice of each QPImage
            in `h5file`. A value of None is equivalent to
            ``(slice(0, -1), slice(0, -1))``.
        series_slice: slice
            If None, save the entire series, otherwise only save
            the images specified by this slice.
        time_interval: tuple of (float, float)
            If not None, only stores QPImages that were recorded
            within the given time interval.
        count, max_count: multiprocessing.Value
            Can be used to monitor the progress of the algorithm.
            Initially, the value of `max_count.value` is incremented
            by the total number of steps. At each step, the value
            of `count.value` is incremented.

        Notes
        -----
        The series "identifier" meta data is only set when all
        of `qpi_slice`, `series_slice`, and `time_interval`
        are None.
        """
        # set up slice to export
        if series_slice is None:
            sl = range(len(self))
        else:
            sl = range(series_slice.start, series_slice.stop)
        # set up time interval
        if time_interval is None:
            ta = -np.inf
            tb = np.inf
        else:
            ta, tb = time_interval
        # set max_count according to slice
        if max_count is not None:
            max_count.value += len(sl)

        qpskw = {"h5file": h5file,
                 "h5mode": "w",
                 }

        if (qpi_slice is None and
            series_slice is None and
                time_interval is None):
            # Only add series identifier if series complete.
            # (We assume that if any of the above kwargs is set,
            # the series data is somehow modified)
            qpskw["identifier"] = self.identifier

        with qpimage.QPSeries(**qpskw) as qps:
            increment = 0
            for ii in sl:
                ti = self.get_time(ii)
                if ti < ta or ti > tb:
                    # Not part of the series
                    pass
                else:
                    increment += 1
                    if increment == 1 or len(self._bgdata) != 1:
                        # initial image or series data where each image
                        # has a unique background image
                        qpi = self.get_qpimage(ii)
                        if qpi_slice is not None:
                            qpi = qpi[qpi_slice]
                        qps.add_qpimage(qpi)
                    else:
                        # hard-link the background data
                        qpiraw = self.get_qpimage_raw(ii)
                        if qpi_slice is not None:
                            qpiraw = qpiraw[qpi_slice]
                        qps.add_qpimage(qpiraw, bg_from_idx=0)
                if count is not None:
                    count.value += 1

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
