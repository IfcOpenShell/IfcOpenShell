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

from blenderbim.bim.module.drawing.svgwriter import SvgWriter
import svgwrite

from odf.opendocument import load
from odf.table import Table, TableRow, TableColumn, TableCell
from odf.text import P
from odf.style import Style
from textwrap import wrap

FONT_SIZE = 4.13
FONT_WIDTH = FONT_SIZE * 0.45


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
            styles[name] = {}

            # NOTE: there are also styles that inherit from parent styles that we do not process atm
            if not style.firstChild:
                continue

            if style.firstChild.tagName in ["style:table-column-properties", "style:table-row-properties"]:
                style_children = [style.firstChild]
            else:
                # for style:table-cell-properties we need to collect also text and paragraph properties
                style_children = style.childNodes

            for child in style_children:
                child_params = {key[1]: value for key, value in child.attributes.items()}
                styles[name].update(child_params)

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

                # figuring text alignment
                style_name = td.getAttribute("stylename")
                style = styles[style_name] if style_name else {}
                if style_name and "vertical-align" in style and style["vertical-align"] != "automatic":
                    vertical_align = style["vertical-align"]
                else:
                    vertical_align = "bottom"

                alignment_translation = {
                    "center": "middle",
                    "end": "right",
                    "start": "left",
                }

                if style_name and "text-align" in style and style["text-align"] != "automatic":
                    horizontal_align = style["text-align"]
                    horizontal_align = alignment_translation.get(horizontal_align, horizontal_align)
                else:
                    horizontal_align = "left"

                if vertical_align == "middle" and horizontal_align == "middle":
                    box_alignment = "center"
                else:
                    box_alignment = f"{vertical_align}-{horizontal_align}"

                # for future use
                wrap_text = style.get("wrap-option", None) == "wrap"

                # drawing cells and text
                for i in range(0, repeat):
                    width = sum(column_widths[tdi : tdi + int(column_span)])
                    self.svg.add(
                        self.svg.rect(
                            insert=(x, y),
                            size=(width, height),
                            style="fill: #ffffff; stroke-width:.125; stroke: #000000;",
                        )
                    )
                    p_tags = td.getElementsByType(P)

                    if p_tags:
                        # figuring text position based on alignment
                        text_position = [0.0, 0.0]
                        if box_alignment.endswith("left"):
                            text_position[0] = x + self.padding
                        elif box_alignment.endswith("middle") or box_alignment == "center":
                            text_position[0] = x + width / 2
                        elif box_alignment.endswith("right"):
                            text_position[0] = x + width - self.padding

                        if box_alignment.startswith("top"):
                            text_position[1] = y + self.padding
                        elif box_alignment.startswith("middle") or box_alignment == "center":
                            text_position[1] = y + height / 2
                        elif box_alignment.startswith("bottom"):
                            text_position[1] = y + height - self.padding

                        self.add_text(
                            p_tags, *text_position, box_alignment=box_alignment, wrap_text=wrap_text, cell_width=width
                        )
                    x += width
                    tdi += column_span

            y += height
        total_width = sum(column_widths) + (self.margin * 2)
        self.svg["width"] = "{}mm".format(total_width)
        self.svg["height"] = "{}mm".format(y)
        self.svg["viewBox"] = "0 0 {} {}".format(total_width, y)
        self.svg.save(pretty=True)

    def add_text(self, p_tags, x, y, box_alignment="bottom-left", wrap_text=False, cell_width=100):
        """
        Adds text to svg.

        Args:
            p_tags: list of cell's P tags from odt file
            box_alignment: alignment of text in box
            wrap_text: if True, text will be wrapped to fit in cell
            cell_width: width of cell, used for wrapping text
        """
        text_lines = [str(p).upper() for p in p_tags]
        box_alignment_params = SvgWriter.get_box_alignment_parameters(box_alignment)
        text_params = {
            "font-size": FONT_SIZE,
            "font-family": "OpenGost Type B TT",
        }
        if len(text_lines) == 1 and not wrap_text:
            text_params.update(box_alignment_params)
            text_tag = self.svg.text(text_lines[0], insert=(x, y), **text_params)
            self.svg.add(text_tag)
            return

        text_tag = self.svg.text("", **({"style": "font-size: 0;"} | box_alignment_params))

        # TODO: should be done in less naive way
        # without using magic number for FONT_WIDTH
        # currently it might not work for all fonts and font sizes
        if wrap_text:
            wrapped_lines = []
            for line in text_lines:
                wrapped_line = wrap(line, width=int(cell_width // FONT_WIDTH), break_long_words=False)
                wrapped_lines.extend(wrapped_line)
        else:
            wrapped_lines = text_lines

        for line_number, text_line in enumerate(wrapped_lines[::-1]):
            # position has to be inserted at tspan to avoid x offset between tspans
            tspan = self.svg.tspan(text_line, insert=(x, y), **text_params)
            # doing it here and not in tspan constructor because constructor adds unnecessary spaces
            tspan.update({"dy": f"-{line_number}em"})
            text_tag.add(tspan)
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
