# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import svgwrite

from odf.opendocument import load
from odf.table import Table, TableRow, TableColumn, TableCell
from odf.text import P
from odf.style import Style

FONT_SIZE = 4.13

class Scheduler:
    def schedule(self, infile, outfile):
        self.svg = svgwrite.Drawing(
            outfile,
            debug=False,
            id="root",
        )
        self.padding = 1
        self.margin = 1
        doc = load(infile)
        styles = {}
        for style in doc.getElementsByType(Style):
            name = style.getAttribute("name")
            # looking for table-column-properties or table-row-properties
            if not style.firstChild:
                continue
            styles[name] = {key[1]: value for key, value in style.firstChild.attributes.items()}

        table = doc.getElementsByType(Table)[0]

        # collect columns width
        column_widths = []
        for col in table.getElementsByType(TableColumn):
            style_name = col.getAttribute("stylename")
            repeat = col.getAttribute("numbercolumnsrepeated")
            repeat = int(repeat) if repeat else 1
            for i in range(repeat):
                if not style_name or "column-width" not in styles[style_name]:
                    column_width = 50
                else:
                    column_width = self.convert_to_mm(styles[style_name]["column-width"])
                column_widths.append(column_width)

        # collect rows height
        row_heights = []
        for col in table.getElementsByType(TableRow):
            style_name = col.getAttribute("stylename")
            repeat = col.getAttribute("numberrowsrepeated")
            repeat = int(repeat) if repeat else 1
            for i in range(repeat):
                if not style_name or "row-height" not in styles[style_name]:
                    row_height = 6
                else:
                    row_height = self.convert_to_mm(styles[style_name]["row-height"])
                row_heights.append(row_height)

        # draw table
        y = self.margin
        for tri, tr in enumerate(table.getElementsByType(TableRow)):
            x = self.margin
            height = row_heights[tri]
            tdi = 0
            
            for td in tr.getElementsByType(TableCell):
                column_span = td.getAttribute("numbercolumnsspanned")
                column_span = int(column_span) if column_span else 1

                repeat = td.getAttribute("numbercolumnsrepeated")
                repeat = int(repeat) if repeat else 1

                for i in range(0, repeat):
                    width = sum(column_widths[tdi:tdi + int(column_span)])
                    self.svg.add(
                        self.svg.rect(
                            insert=(x, y),
                            size=(width, height),
                            style="fill: #ffffff; stroke-width:.125; stroke: #000000;",
                        )
                    )
                    value = td.getElementsByType(P)
                    if value:
                        self.add_text(value[0], x + self.padding, y + height - self.padding)
                    x += width
                    tdi += column_span

            y += height
        total_width = sum(column_widths) + (self.margin * 2)
        self.svg["width"] = "{}mm".format(total_width)
        self.svg["height"] = "{}mm".format(y)
        self.svg["viewBox"] = "0 0 {} {}".format(total_width, y)
        self.svg.save(pretty=True)

    def add_text(self, text, x, y):
        bottom_left_alignment = {
            "alignment-baseline": "baseline",
            "dominant-baseline": "baseline",
        }
        text_tag = self.svg.text(
            str(text).upper(),
            insert=tuple((x, y)),
            **({
                "font-size": FONT_SIZE,
                "font-family": "OpenGost Type B TT",
                "text-anchor": "start",
            } | bottom_left_alignment)
        )
        self.svg.add(text_tag)            

    def convert_to_mm(self, value):
        # XSL is what defines the units of measurements in ODF
        # https://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#datatype-positiveLength
        # https://www.w3.org/TR/2001/REC-xsl-20011015/slice5.html#section-N8185-Definitions-of-Units-of-Measure
        if "cm" in value:
            return float(value[0:-2]) * 10
        elif "mm" in value:
            return float(value[0:-2])
        elif "in" in value:
            return float(value[0:-2]) * 25.4
        elif "pt" in value:
            return float(value[0:-2]) * (1 / 72) * 25.4
        elif "pc" in value:
            return float(value[0:-2]) * 12 * (1 / 72) * 25.4
        elif "px" in value:
            # implementors may instead simply pick a fixed conversion factor,
            # treating 'px' as an absolute unit of measurement (such as 1/92" or
            # 1/72"). <-- We're picking 1/96 to match SVG. Let me know if it
            # breaks anything.
            return float(value[0:-2]) * (1 / 96) * 2.54 * 10
        elif "em" in value:
            # This is a funny one. Since the scheduler at the moment enforces a
            # font size of 2.5mm (vertically, FWIW), I'm writing this. Hopefully
            # this code doesn't hurt anybody.
            return float(value[0:-2]) * (1 / 96) * 2.54 * 10
