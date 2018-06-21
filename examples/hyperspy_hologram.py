"""HyperSpy hologram file format

This example demonstrates the import of hologram images in
the `HyperSpy <https://hyperspy.org/>`_ hdf5 file format.
The off-axis electron hologram shows an electrically biased Fe
needle :cite:`Migunov2015`. The corresponding HyperSpy demo
can be found `here <http://nbviewer.jupyter.org/github/hyperspy/hypersp
y-demos/blob/master/electron_microscopy/Holography/Holography.ipynb>`_.
"""

import urllib.request
import os

import matplotlib.pylab as plt
import qpformat

# load the experimental data
dl_loc = "https://github.com/hyperspy/hyperspy/raw/RELEASE_next_major/" \
         + "hyperspy/misc/holography/example_signals/"
dl_name = "01_holo_Vbp_130V_0V_bin2_crop.hdf5"
if not os.path.exists(dl_name):
    print("Downloading {} ...".format(dl_name))
    urllib.request.urlretrieve(dl_loc + dl_name, dl_name)

ds = qpformat.load_data(dl_name,
                        holo_kw={
                            # reduces ringing artifacts in the amplitude image
                            "filter_name": "smooth disk",
                            # select correct sideband
                            "sideband": -1,
                            })

# retrieve the qpimage.QPImage instance
qpi = ds.get_qpimage(0)

# plot results
plt.figure(figsize=(8, 3.5))
# ampltitude
ax1 = plt.subplot(121, title="amplitude")
map1 = plt.imshow(qpi.amp, cmap="gray")
plt.colorbar(map1, ax=ax1, fraction=.0455, pad=0.04)
# phase in interval [-1rad, 1rad]
ax2 = plt.subplot(122, title="phase [rad]")
map2 = plt.imshow(qpi.pha)
plt.colorbar(map2, ax=ax2, fraction=.0455, pad=0.04)
# disable axes
[ax.axis("off") for ax in [ax1, ax2]]
plt.tight_layout()
plt.show()
