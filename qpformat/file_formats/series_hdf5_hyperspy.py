import functools
import warnings

import h5py
import qpimage

from .dataset import SeriesData


class HyperSpyNoDataFoundError(BaseException):
    pass


class WrongSignalTypeWarnging(UserWarning):
    pass


class SeriesHdf5HyperSpy(SeriesData):
    """HyperSpy hologram series (HDF5 format)

    HyperSpy has its :ref:`own implementation
    <hyperspy:electron-holography-label>` to read this file format.
    """
    storage_type = "hologram"

    def __len__(self):
        return len(self._get_experiments())

    def _check_experiment(self, name):
        """Check the signal type of the experiment

        Returns
        -------
        True, if the signal type is supported, False otherwise

        Raises
        ------
        Warning if the signal type is not supported
        """
        with h5py.File(name=self.path, mode="r") as h5:
            sigpath = "/Experiments/{}/metadata/Signal".format(name)
            signal_type = h5[sigpath].attrs["signal_type"]
        if signal_type != "hologram":
            msg = "Signal type '{}' not supported: {}[{}]".format(signal_type,
                                                                  self.path,
                                                                  name)
            warnings.warn(msg, WrongSignalTypeWarnging)
        return signal_type == "hologram"

    @functools.lru_cache(maxsize=5)
    def _get_experiments(self):
        """Get all experiments from the hdf5 file"""
        explist = []
        with h5py.File(name=self.path, mode="r") as h5:
            if "Experiments" not in h5:
                msg = "Group 'Experiments' not found in {}.".format(self.path)
                raise HyperSpyNoDataFoundError(msg)
            for name in h5["Experiments"]:
                # check experiment
                if self._check_experiment(name):
                    explist.append(name)
        explist.sort()
        if not explist:
            # if this error is raised, the signal_type is probably not
            # set to "hologram".
            msg = "No supported data found: {}".format(self.path)
            raise HyperSpyNoDataFoundError(msg)
        return explist

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        name = self._get_experiments()[idx]
        with h5py.File(name=self.path, mode="r") as h5:
            exp = h5["Experiments"][name]
            # hologram data
            data = exp["data"].value
            # resolution
            rx = exp["axis-0"].attrs["scale"]
            ry = exp["axis-1"].attrs["scale"]
            if rx != ry:
                raise NotImplementedError("Only square pixels supported!")
            runit = exp["axis-0"].attrs["units"]
            if runit == "nm":
                pixel_size = rx * 1e-9
            else:
                raise NotImplementedError("Units '{}' not implemented!")

        meta_data = {"pixel size": pixel_size}
        meta_data.update(self.meta_data)

        qpi = qpimage.QPImage(data=data,
                              which_data="hologram",
                              meta_data=meta_data,
                              holo_kw=self.holo_kw,
                              h5dtype=self.as_type)
        # set identifier
        qpi["identifier"] = self.get_identifier(idx)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has the HyperSpy file format"""
        valid = False
        try:
            h5 = h5py.File(path, mode="r")
        except (OSError, IsADirectoryError):
            pass
        else:
            if ("file_format" in h5.attrs and
                h5.attrs["file_format"].lower() == "hyperspy" and
                    "Experiments" in h5):
                valid = True
        return valid
