"""visualization of dclab definitions

Usage
-----
Directives:

Run autodoc on all supported formats:

   .. autodoc_qpformats::

Create table of all supported formats

   .. qpformats::
"""
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles
from docutils import nodes

from qpformat.file_formats import formats_dict, SeriesData


class Base(Directive):
    required_arguments = 0
    optional_arguments = 0

    def generate_rst(self):
        pass        

    def run(self):
        rst = self.generate_rst()

        vl = ViewList(rst, "fakefile.rst")
        # Create a node.
        node = nodes.section()
        node.document = self.state.document
        # Parse the rst.
        nested_parse_with_titles(self.state, vl, node)
        return node.children


class AutodocFormats(Base):
    def generate_rst(self):
        rst = []

        refdir = [a for a in dir(SeriesData) if not a.startswith("_")]

        for key in sorted(formats_dict.keys()):
            # get any public methods that are not in the base class
            cdir = [a for a in dir(formats_dict[key]) if not a.startswith("_")]
            cdir = [a for a in cdir if not a in refdir]
            # get important public attributes
            udcand = ["is_series", "storage_type"]
            udir = [a for a in udcand if hasattr(formats_dict[key], a)]
            # remove attributes from cdir to avoid redundant docs
            [cdir.remove(a) for a in udir if a in cdir]
            rst.append("")
            # headint
            rst.append(key)
            rst.append("-"*len(key))
            # autodoc
            rst.append(".. autoclass:: qpformat.file_formats.{}".format(key))
            if cdir:
                rst.append("    :members: {}".format(", ".join(cdir)))
            if udir:
                rst.append("")
                for u in udir:
                    rst.append("    .. autoattribute:: {}".format(u))
            rst.append("")

        return rst


class Formats(Base):
    def generate_rst(self):
        rst = []

        rst.append(".. csv-table::")
        rst.append("    :header: Class, Storage type, Description".format())
        rst.append("    :widths: 2, 2, 6")
        rst.append("    :delim: tab")
        rst.append("")

        for key in sorted(formats_dict.keys()):
            cl = formats_dict[key]
            datatype = cl.storage_type
            if not isinstance(datatype, str):
                datatype = "*multiple*"
            rst.append("    :class:`{key}<qpformat.file_formats.{key}>`\t {type}\t {doc}".format(
                key=key, type=datatype, doc=cl.__doc__.split("\n", 1)[0]))
        
        rst.append("")

        return rst


def setup(app):
    app.add_directive('autodoc_qpformats', AutodocFormats)
    app.add_directive('qpformats', Formats)
    return {'version': '0.1'}   # identifies the version of our extension
