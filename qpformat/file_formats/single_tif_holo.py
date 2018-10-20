import copy
from os import fspath
import pathlib

import numpy as np
import qpimage
from skimage.external import tifffile

from .dataset import SingleData


class SingleTifHolo(SingleData):
    """Off-axis hologram image (TIFF format)"""
    storage_type = "hologram"

    @staticmethod
    def _get_tif(path):
        if hasattr(path, "seek"):  # opened file
            # Seek open file zero to avoid error in tifffile:
            # "ValueError: invalid TIFF file"
            path.seek(0)
        else:  # path
            path = fspath(path)
        return tifffile.TiffFile(path)

    def get_time(self):
        """Time of the TIFF file

        Currently, only the file modification time is supported.
        Note that the modification time of the TIFF file is
        dependent on the file system and may have temporal
        resolution as low as 3 seconds.
        """
        if isinstance(self.path, pathlib.Path):
            thetime = self.path.stat().st_mtime
        else:
            thetime = np.nan
        return thetime

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with SingleTifHolo._get_tif(self.path) as tf:
            holo = tf.pages[0].asarray()
        meta_data = copy.copy(self.meta_data)
        qpi = qpimage.QPImage(data=(holo),
                              which_data="hologram",
                              meta_data=meta_data,
                              holo_kw=self.holo_kw,
                              h5dtype=self.as_type)
        # set identifier
        qpi["identifier"] = self.get_identifier()
        qpi["time"] = self.get_time()
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` is a valid TIFF file"""
        valid = False
        try:
            tf = SingleTifHolo._get_tif(path)
        except (ValueError, IsADirectoryError):
            pass
        else:
            if len(tf) == 1:
                valid = True
        return valid
