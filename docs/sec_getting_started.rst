===============
Getting started
===============


Installing qpformat
===================

qpformat is written in pure Python and supports Python version 3.6
and higher.

To install qpformat, use one of the following methods
(package dependencies will be installed automatically):

* from `PyPI <https://pypi.python.org/pypi/qpformat>`_:
    ``pip install qpformat``
* from `sources <https://github.com/RI-imaging/qpformat>`_:
    ``pip install -e .``


User API
========
Qpformat supports :ref:`several file formats <supported_formats>` that are
categorized into :class:`qpformat.file_formats.SingleData`
(the experimental data file format contains only one phase image)
and :class:`qpformat.file_formats.SeriesData` (the experimental
data file format supports multiple phase images).
From these base classes, all data file formats are derived. The idea
is that experimental data is not loaded into memory until the
`get_qpimage` method is called which returns a
:class:`qpimage.QPImage <qpimage.core.QPImage>` object.


Basic Usage
-----------
To extract the (unwrapped) phase from a DHM image, use the
:func:`qpformat.load_data` method. The file format type is
determined automatically by qpformat.

.. code:: python

    import qpformat
    # The data are not loaded into memory, only the meta data is read
    dataset = qpformat.load_data("/path/to/hologram_image.tif")
    # Get the quantitative phase data (a qpimage.QPImage is returned)
    qpi = dataset.get_qpimage()
    # Get the 2D phase image data as a numpy array
    phase = qpi.pha

The object ``qpi`` is an instance of
:class:`qpimage.QPImage <qpimage.core.QPImage>` which
comes with an elaborate set of background correction methods. Note
that :func:`qpformat.load_data` accepts keyword arguments that allow
to define the setup metadata as well as the hologram reconstruction
parameters.


Command-line program "qpinfo"
=============================
This command-line program allows checking whether a file (or directory)
contains quantitative phase data with a file format supported by qpformat.

.. code::

  usage: qpinfo [-h] path

The command yields the type of the format, the corresponding class name
in qpformat, as well as the meta data associated with the dataset
(e.g. wavelength, pixel size).
