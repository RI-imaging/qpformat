from os import fspath
import pathlib

import qpimage
import tifffile

from ..single_base import SingleData


class SingleRawOAHTif(SingleData):
    """Off-axis hologram image (TIFF format)"""
    storage_type = "raw-oah"

    @staticmethod
    def _get_tif(path):
        if hasattr(path, "seek"):  # opened file
            # Seek open file zero to avoid error in tifffile:
            # "ValueError: invalid TIFF file"
            path.seek(0)
        else:  # path
            path = fspath(path)
        return tifffile.TiffFile(path)

    def get_metadata(self, idx=0):
        """Get tiff file metadata

        Currently, only the file modification time is supported.
        Note that the modification time of the TIFF file is
        dependent on the file system and may have temporal
        resolution as low as 3 seconds.
        """
        meta_data = {}
        if isinstance(self.path, pathlib.Path):
            meta_data["time"] = self.path.stat().st_mtime

        smeta = super(SingleRawOAHTif, self).get_metadata(idx)
        meta_data.update(smeta)
        return meta_data

    def get_qpimage_raw(self, idx=0):
        """Return QPImage without background correction"""
        # Load experimental data
        with SingleRawOAHTif._get_tif(self.path) as tf:
            holo = tf.pages[0].asarray()
        qpi = qpimage.QPImage(data=holo,
                              which_data="raw-oah",
                              meta_data=self.get_metadata(idx),
                              qpretrieve_kw=self.qpretrieve_kw,
                              h5dtype=self.as_type)
        return qpi

    @staticmethod
    def verify(path):
        """Verify that `path` is a valid TIFF file"""
        valid = False
        try:
            tf = SingleRawOAHTif._get_tif(path)
        except (ValueError, IsADirectoryError, KeyError,
                tifffile.tifffile.TiffFileError):
            pass
        else:
            if len(tf.pages) == 1:
                valid = True
            if not hasattr(path, "seek"):
                tf.close()
        return valid
