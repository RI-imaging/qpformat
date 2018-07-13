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

from qpformat.file_formats import formats_dict


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

        for key in sorted(formats_dict.keys()):
            rst.append("")
            rst.append(".. autoclass:: qpformat.file_formats.{}".format(key))
            rst.append("")

        return rst


class Formats(Base):
    def generate_rst(self):
        rst = []

        rst.append(".. csv-table::")
        rst.append("    :header: Class, Data type, Description".format())
        rst.append("    :widths: 2, 2, 6")
        rst.append("    :delim: tab")
        rst.append("")

        for key in sorted(formats_dict.keys()):
            cl = formats_dict[key]
            datatype = cl.storage_type
            if not isinstance(datatype, str):
                datatype = "multiple"
            rst.append("    :class:`{key}<qpformat.file_formats.{key}>`\t {type}\t {doc}".format(
                key=key, type=datatype, doc=cl.__doc__.split("\n", 1)[0]))
        
        rst.append("")

        return rst


def setup(app):
    app.add_directive('autodoc_qpformats', AutodocFormats)
    app.add_directive('qpformats', Formats)
    return {'version': '0.1'}   # identifies the version of our extension
