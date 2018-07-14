==============
Code reference
==============

.. toctree::
  :maxdepth: 2


module-level
============
.. autofunction:: qpformat.load_data


file format base classes
========================
SeriesData
----------
.. autoclass:: qpformat.file_formats.dataset.SeriesData
    :members:

SingleData
----------
.. autoclass:: qpformat.file_formats.dataset.SingleData
    :inherited-members:



file format readers
===================
All file formats inherit from :class:`qpformat.file_formats.dataset.SeriesData`
(and/or :class:`qpformat.file_formats.dataset.SingleData`).

.. autodoc_qpformats::


exceptions
==========
.. autoexception:: qpformat.file_formats.MultipleFormatsNotSupportedError

.. autoexception:: qpformat.file_formats.UnknownFileFormatError