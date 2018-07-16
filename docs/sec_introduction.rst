============
Introduction
============

.. toctree::
  :maxdepth: 2


Why qpformat?
=============
There is a multitude of phase-imaging techniques that inevitably comes
with a broad range of quantitative phase imaging (QPI) file formats.
In addition, raw data, such as digital holographic microscopy (DHM) images,
must be preprocessed to access the phase encoded in the interference pattern. 
Qpformat provides a unified and user-friendly interface for loading QPI data.
It is based on the :ref:`qpimage <qpimage:index>` library and thus benefits
from its hdf5-based data structure (e.g. elaborate background correction,
meta data management, and transparent data storage). Furthermore, qpformat
can manage large datasets (e.g. many holograms in one folder) without running
out of memory by means of its lazily-evaluated
:class:`SeriesData <qpformat.file_formats.SeriesData>` class.


.. _supported_formats:

Supported file formats
======================
.. qpformats::
