import functools
import warnings

import h5py
import numpy as np
import qpimage

from ..dataset import SeriesData


class NoSinogramDataFoundError(BaseException):
    pass


class SeriesHDF5GenericWarning(UserWarning):
    pass


class SeriesHDF5SinogramGeneric(SeriesData):
    """Base class for HDF5-based raw sinogram QPI data
    """
    priority = -9  # higher priority, because it's fast

    def __len__(self):
        return len(self._get_data_indices())

    @functools.lru_cache()
    def _get_data_indices(self):
        """Get all experiments from the hdf5 file"""
        with h5py.File(name=self.path, mode="r") as h5:
            if "sinogram" not in h5:
                raise NoSinogramDataFoundError(
                    f"Group 'sinogram' not found in '{self.path}'!")
            indices = sorted(h5["sinogram"].keys(), key=lambda x: int(x))

        if not indices:
            raise NoSinogramDataFoundError(
                f"No sinogram data found in '{self.path}'!")
        return indices

    def _get_metadata(self, dataset):
        """Return the metadata of the specified `h5py.Dataset`"""
        meta = qpimage.meta.MetaDict()
        for key in qpimage.META_KEYS:
            if key in dataset.attrs:
                meta[key] = dataset.attrs[key]
        return meta

    @staticmethod
    def verify(path):
        """Verify that `path` has generic sinogram data"""
        valid = False
        try:
            h5 = h5py.File(path, mode="r")
        except (OSError, IsADirectoryError):
            pass
        else:
            if ("file_format" in h5.attrs
                and "qpformat" in h5.attrs["file_format"].lower()
                    and "sinogram" in h5):
                valid = True
            h5.close()
        return valid

    @property
    @functools.lru_cache()
    def shape(self):
        with h5py.File(name=self.path, mode="r") as h5:
            group = h5["sinogram"]["0"]
            for key in ["field", "phase", "amplitude", "intensity"]:
                if key in group:
                    return len(self), group[key].shape[0], group[key].shape[1]
            else:
                # Fallback to expensive shape computation
                warnings.warn(f"Using fallback `shape` for '{self.path}'!",
                              SeriesHDF5GenericWarning)
                return super(SeriesHDF5SinogramGeneric, self).shape


class SeriesHDF5SinogramMeep(SeriesHDF5SinogramGeneric):
    """sinograms extracted from Meep/FDTD simulations

    I introduced this format in 2022 as part of my efforts to make
    the finite-difference time domain simulations from the ODTbrain
    manuscript :cite:`Mueller2015` publicly available.

    The HDF5 file contains a "background" and a "sinogram" group.
    The subgroups of "sinogram" are enumerated starting with "0".
    Each of them contain the complex "field" at a plane behind the
    scattering phantom as an HDF5 Dataset. The location of the plane
    (and all other relevant metadata) is stored in the attributes
    of this Dataset. In the same group, there are also the C++
    "simulation_code" and the log "simulation_output" which can
    be used to reproduce the simulation.
    """
    storage_type = "field"

    def __init__(self, path, meta_data=None, *args, **kwargs):
        """Initialize with default wavelength of 500nm"""
        if meta_data is None:
            meta_data = {}
        if "wavelength" not in meta_data:
            meta_data["wavelength"] = 500e-9
        super(SeriesHDF5SinogramMeep, self).__init__(
            path=path, meta_data=meta_data, *args, **kwargs)

        # set background data
        with h5py.File(path, "r") as h5:
            if "background" in h5:
                bgds = h5["background"]["field"]
                meta_data = self._get_metadata(bgds)
                qpi_bg = qpimage.QPImage(data=bgds[:],
                                         which_data="field",
                                         meta_data=meta_data,
                                         h5dtype=self.as_type)
                self.set_bg(qpi_bg)

    def _get_metadata(self, dataset):
        """Return simulation-specific metadata

        This uses the metadata previously extracted
        from the simulation and set in `dataset.attrs`
        to populate the QPI metadata.
        """
        meta = super(SeriesHDF5SinogramMeep, self)._get_metadata(dataset)
        meta.update(self.meta_data)
        if "ACQUISITION_PHI" in dataset.attrs:
            meta["angle"] = dataset.attrs["ACQUISITION_PHI"]

        if "MEDIUM_RI" in dataset.attrs:
            meta["medium index"] = dataset.attrs["MEDIUM_RI"]

        if "SAMPLING" in dataset.attrs:
            meta["pixel size"] = meta["wavelength"] / dataset.attrs["SAMPLING"]

            if "extraction focus distance [px]" in dataset.attrs:
                focus_px = dataset.attrs["extraction focus distance [px]"]
                meta["focus"] = focus_px * meta["pixel size"]

        meta["sim center"] = np.array(dataset.shape) / 2
        meta["sim model"] = "fdtd"

        return meta

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        name = self._get_data_indices()[idx]
        with h5py.File(name=self.path, mode="r") as h5:
            dataset = h5["sinogram"][name]["field"]
            meta_data = self._get_metadata(dataset)
            meta_data["time"] = float(idx)
            qpi = qpimage.QPImage(data=dataset[:],
                                  which_data="field",
                                  meta_data=meta_data,
                                  h5dtype=self.as_type)
        # set identifier
        qpi["identifier"] = self.get_identifier(idx)
        return qpi

    @staticmethod
    def verify(path):
        """Verify the file format

        The "file_format" attribute of the HDF5 file must contain
        the strings "qpformat" and "meep".
        """
        valid = SeriesHDF5SinogramGeneric.verify(path)
        if valid:
            with h5py.File(path, "r") as h5:
                valid = "meep" in h5.attrs["file_format"].lower()
        return valid
