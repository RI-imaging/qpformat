"""Hologram from tif file

This example illustrates how to retrieve phase and amplitude from a
hologram stored as a tif file. The experimental hologram is a
U.S. Air Force test target downloaded from the
`Submersible Holographic Astrobiology Microscope with
Ultraresolution (SHAMU) <https://github.com/bmorris3/shampoo>`_
project :cite:`Bedrossian2017`. The values for pixel resolution,
wavelength, and reconstruction distance are taken from the
corresponding `Python example <http://shampoo.readthedocs.io/en/latest
/getting_started.html#simple-numerical-reconstruction>`_.

The object returned by the
:func:`get_qpimage <qpformat.file_formats.dataset.SingleData.get_qpimage`
function is an instance of :class:`qpimage.QPImage <qpimage.core.QPImage>`
which allows for field refocusing. The refocused QPImage is
background-corrected using a polynomial fit to the phase data at locations
where the amplitude data is not attenuated (bright regions in the amplitude
image).
"""

import urllib.request
import os

import matplotlib.pylab as plt
import qpformat


# load the experimental data
dl_loc = "https://github.com/bmorris3/shampoo/raw/master/data/"
dl_name = "USAF_test.tif"
if not os.path.exists(dl_name):
    print("Downloading {} ...".format(dl_name))
    urllib.request.urlretrieve(dl_loc + dl_name, dl_name)


ds = qpformat.load_data(dl_name,
                        # manually set meta data
                        meta_data={"pixel size": 3.45e-6,
                                   "wavelength": 405e-9,
                                   "medium index": 1},
                        # set filter size to 1/2 (defaults to 1/3)
                        # which increases the image resolution
                        holo_kw={"filter_size": .5})

# retrieve the qpimage.QPImage instance
qpi = ds.get_qpimage()
# refocus `qpi` to 0.03685m
qpi_foc = qpi.refocus(0.03685)
# perform an offset-based amplitude correction
qpi_foc.compute_bg(which_data="amplitude",
                   fit_profile="offset",
                   fit_offset="mode",
                   border_px=10,
                   )
# perform a phase correction using
# - those pixels that are not dark in the amplitude image (amp_bin) and
# - a 2D second order polynomial fit to the phase data
amp_bin = qpi_foc.amp > 1  # bright regions
qpi_foc.compute_bg(which_data="phase",
                   fit_profile="poly2o",
                   from_mask=amp_bin,
                   )

# plot results
plt.figure(figsize=(8, 3.5))
# ampltitude
ax1 = plt.subplot(121, title="amplitude")
map1 = plt.imshow(qpi_foc.amp, cmap="gray")
plt.colorbar(map1, ax=ax1, fraction=.0455, pad=0.04)
# phase in interval [-1rad, 1rad]
ax2 = plt.subplot(122, title="phase [rad]")
map2 = plt.imshow(qpi_foc.pha, vmin=-1, vmax=1)
plt.colorbar(map2, ax=ax2, fraction=.0455, pad=0.04)
# disable axes
[ax.axis("off") for ax in [ax1, ax2]]
plt.tight_layout()
plt.show()
