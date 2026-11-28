# This file was generated with the assistance of an AI coding tool.

import xml.etree.ElementTree as ET

from bonsai.bim.module.drawing.svgwriter import External

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
    '<image xlink:href="a.png" width="1"/></svg>'
)


class TestExternal:
    def test_xlink_attributes_do_not_redeclare_the_namespace(self):
        external = External(ET.fromstring(SVG))
        output = ET.tostring(external.get_xml(), encoding="unicode")
        assert "xmlns" not in output
        assert 'xlink:href="a.png"' in output
