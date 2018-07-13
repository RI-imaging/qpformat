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
SingleData
----------
.. autoclass:: qpformat.file_formats.dataset.SingleData
    :inherited-members:

SeriesData
----------
.. autoclass:: qpformat.file_formats.dataset.SeriesData
    :members:


file format readers
===================
.. autodoc_qpformats::


exceptions
==========
.. autoexception:: qpformat.file_formats.MultipleFormatsNotSupportedError

.. autoexception:: qpformat.file_formats.UnknownFileFormatError