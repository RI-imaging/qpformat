========
User API
========
Qpformat supports several file formats
(:py:class:`qpformat.file_formats.formats`), which are
divided into :py:class:`qpformat.file_formats.SingleData`
(the experimental data file format contains only one phase image)
and :py:class:`qpformat.file_formats.SeriesData` (the experimental
data file format supports multiple phase images).
From these base classes, all data file formats are derived. The idea
is that experimental data is not loaded into memory until the
`get_qpimage` method is called which returns a
:py:class:`qpimage.QPImage` object.

Basic Usage
-----------
The file format type is determined automatically by qpformat.
If the file format is implemented in qpformat, experimental
data can be loaded with the :py:func:`qpformat.load_data` method.

.. code-block:: python

   # Obtain a qpformat.file_formats.SingleData object
   # (the data is not loaded into memory, only the meta data is read)
   ds = qpformat.load_data(path="/path/to/SID PHA_xxx.tif")
   # Get the quantitative phase data (a qpimage.QPImage is returned)
   qpi = ds.get_qpimage()


SingleData
----------
.. autoclass:: qpformat.file_formats.SeriesData
    :inherited-members:

SeriesData
----------
.. autoclass:: qpformat.file_formats.SeriesData
    :members:

Constants
---------
.. autodata:: qpformat.file_formats.formats