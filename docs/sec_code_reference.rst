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
.. autoclass:: qpformat.file_formats.SeriesData
    :members:

SingleData
----------
.. autoclass:: qpformat.file_formats.SingleData
    :inherited-members:


file format readers
===================
All file formats inherit from :class:`qpformat.file_formats.SeriesData`
(and/or :class:`qpformat.file_formats.SingleData`).

.. autodoc_qpformats::


exceptions
==========
.. autoexception:: qpformat.file_formats.MultipleFormatsNotSupportedError

.. autoexception:: qpformat.file_formats.UnknownFileFormatError
