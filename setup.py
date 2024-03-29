from os.path import dirname, realpath, exists
from setuptools import setup, find_packages
import sys


author = u"Paul Müller"
authors = [author]
description = 'library for opening quantitative phase imaging data'
name = 'qpformat'
year = "2017"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
from _version import version  # noqa: E402

setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/RI-imaging/qpformat',
    version=version,
    packages=find_packages(),
    package_dir={name: name},
    license="MIT",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=[
        "h5py>=3.5.0",  # no timestamps for datasets in 3.5
        "numpy>=1.12.0",
        "qpimage>=0.9.1",
        "qpretrieve>=0.3.0",
        "tifffile>=2020.5.25",
        ],
    python_requires='>=3.10, <4',
    entry_points={
       "console_scripts": [
           "qpinfo = qpformat.cli:qpinfo",
            ],
       },
    keywords=["data file format",
              "digital holographic microscopy",
              "quantitative phase imaging",
              ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL'],
    )
