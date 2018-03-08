import copy

import qpimage
from skimage.external import tifffile

from .dataset import SingleData


class SingleTifHolo(SingleData):
    """DataSet for single hologram images"""
    storage_type = "hologram"

    @staticmethod
    def _get_tif(path):
        if not isinstance(path, str):
            # Seek open file zero to avoid error in tifffile:
            # "ValueError: invalid TIFF file"
            path.seek(0)
        return tifffile.TiffFile(path)

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with SingleTifHolo._get_tif(self.path) as tf:
            holo = tf.pages[0].asarray()
        meta_data = copy.copy(self.meta_data)
        qpi = qpimage.QPImage(data=(holo),
                              which_data="hologram",
                              meta_data=meta_data,
                              holo_kw=self.holo_kw)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` has the qpimage file format

        Returns `True` if the file format matches.
        """
        valid = False
        try:
            tf = SingleTifHolo._get_tif(path)
        except (ValueError, IsADirectoryError):
            pass
        else:
            if len(tf) == 1:
                valid = True
        return valid
