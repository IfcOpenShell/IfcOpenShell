# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
# SPDX-License-Identifier: GPL-3.0-or-later
# This file was generated with the assistance of an AI coding tool.

"""Run directly with Python/unittest, or collect with pytest; Blender is not needed."""

import importlib.util
import unittest
from pathlib import Path

# Import the pure module without executing Bonsai's Blender-dependent package initializers.
BONSAI = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("svg_overlay", BONSAI / "bonsai/bim/module/drawing/svg_overlay.py")
subject = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subject)


def drawing(body, css=""):
    return subject.parse_svg(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
        f"<defs><style><![CDATA[{css}]]></style></defs>{body}</svg>"
    )


class TestSvgOverlay(unittest.TestCase):
    def test_final_stylesheet_inheritance_and_path_override(self):
        css = (BONSAI / "bonsai/bim/data/assets/default.css").read_text(encoding="utf-8")
        result = drawing(
            '<g class="projection"><g class="IfcWall">'
            '<path d="M0,0 L10,10"/><path class="sharp" d="M0,0 L20,20"/></g></g>'
            '<g class="cut"><path d="M0,0 L30,30"/></g>',
            css,
        )
        self.assertEqual([s.width for s in result.strokes], [0.25, 0.18, 0.35])
        self.assertEqual([s.color for s in result.strokes], [(0, 0, 0, 1), (0, 0, 0, 0.7), (0, 0, 0, 1)])

    def test_cascade_specificity_order_inline_and_important(self):
        result = drawing(
            '<g class="cut"><path class="IfcWall thick" stroke="green" style="stroke: blue; stroke-width: 2" '
            'd="M0 0 L1 1"/></g>',
            ".cut .IfcWall {stroke:red} .IfcWall.thick {stroke:#123 !important;stroke-width:3} "
            ".IfcWall.thick {stroke:#456 !important} path {stroke: white !important}",
        )
        self.assertEqual(result.strokes[0].color, (0x44 / 255, 0x55 / 255, 0x66 / 255, 1))
        self.assertEqual(result.strokes[0].width, 2)

    def test_child_style_beats_inherited_important(self):
        result = drawing(
            '<g class="cut"><line class="edge" x2="1"/></g>',
            ".cut {stroke:red !important} .edge {stroke:blue}",
        )
        self.assertEqual(result.strokes[0].color, (0, 0, 1, 1))

    def test_opacity_and_visibility(self):
        result = drawing(
            '<g stroke="red" opacity="0.5"><g opacity="0.5"><line x2="1" stroke-opacity="0.4"/></g>'
            '<g display="none"><line x2="1"/></g><line x2="1" visibility="hidden"/></g>'
        )
        self.assertEqual(len(result.strokes), 1)
        self.assertAlmostEqual(result.strokes[0].color[3], 0.1)

    def test_comments_selector_lists_and_unsupported_rules(self):
        result = drawing(
            '<line class="edge" x2="1"/>',
            "/* .edge {stroke:blue} */ @media print {.edge {stroke:red}} "
            "polygon, line.edge {stroke:rgb(12, 34, 56);stroke-width:0.2px} "
            ".edge:hover {stroke:green} g > .edge {stroke:purple}",
        )
        self.assertEqual(result.strokes[0].color, (12 / 255, 34 / 255, 56 / 255, 1))
        self.assertEqual(result.strokes[0].width, 0.2)

    def test_absolute_relative_repeated_and_closed_paths(self):
        self.assertEqual(
            subject.paths("M1 2 3 4 H5 V6 h-1 v-2 l2 1 z m10 0 2 3"),
            [[(1, 2), (3, 4), (5, 4), (5, 6), (4, 6), (4, 4), (6, 5), (1, 2)], [(11, 2), (13, 5)]],
        )

    def test_exponents_adjacent_signs_and_subpaths(self):
        result = subject.paths("M1e1-2.5L.5.6 M0 0L1 1")
        self.assertEqual(result, [[(10, -2.5), (0.5, 0.6)], [(0, 0), (1, 1)]])
        parsed = drawing('<path stroke="black" d="M0 0L1 1 M2 2L3 3"/>')
        self.assertEqual(len(parsed.strokes[0].segments), 2)

    def test_invalid_or_curved_path_is_skipped_whole(self):
        for path in ("M0 0L1 1Q2 2 3 3", "M0 0C1 1 2 2 3 3", "M0 0A1 1 0 0 0 2 2", "M0", "L1 2", "Z", "M0 0L"):
            with self.subTest(path=path):
                self.assertEqual(drawing(f'<path stroke="black" d="{path}"/>').strokes, [])

    def test_line_polygon_and_polyline(self):
        result = drawing(
            '<g stroke="black"><line x1="1" y1="2" x2="3" y2="4"/>'
            '<polygon points="0,0 1,0 1,1"/><polyline points="0,0 1,0 1,1"/></g>'
        )
        self.assertEqual([len(s.segments) for s in result.strokes], [1, 3, 2])
        self.assertEqual(result.strokes[0].segments, [((1, 2), (3, 4))])

    def test_dash_phase_continues_at_corners_and_resets_at_moveto(self):
        result = drawing('<path stroke="black" stroke-dasharray="3,2" d="M0 0H4V4 M10 0H14"/>')
        self.assertEqual(
            result.strokes[0].segments,
            [((0, 0), (3, 0)), ((4, 1), (4, 4)), ((10, 0), (13, 0))],
        )

    def test_odd_and_zero_dash_arrays(self):
        self.assertEqual(subject.segments([(0, 0), (5, 0)], [2]), [((0, 0), (2, 0)), ((4, 0), (5, 0))])
        self.assertEqual(subject.segments([(0, 0), (5, 0)], [0, 0]), [((0, 0), (5, 0))])
        self.assertEqual(subject.segments([(0, 0), (5, 0)], [0, 2]), [])

    def test_unsupported_elements_and_transformed_subtrees_are_skipped(self):
        result = drawing(
            '<g stroke="black"><defs><line x2="1"/></defs><text>Text</text><use href="#symbol"/>'
            '<g transform="translate(1,2)"><line x2="1"/></g>'
            '<g clip-path="url(#clip)"><line x2="1"/></g><line x2="1" stroke="url(#gradient)"/>'
            '<svg x="10" viewBox="0 0 1 1"><line x2="1"/></svg>'
            '<line x2="2"/><polygon fill="red" stroke="none" points="0 0 1 0 1 1"/></g>'
        )
        self.assertEqual(len(result.strokes), 1)

    def test_invalid_primitive_does_not_hide_siblings(self):
        result = drawing('<g stroke="black"><line x2="invalid"/><line x2="1"/><path d="M0 0L1e999 1"/></g>')
        self.assertEqual(len(result.strokes), 1)

    def test_camera_mapping_matches_writer_at_different_scales(self):
        for scale in (1 / 50, 1 / 100, 1 / 200):
            width, height = 20, 10
            view_box = (0, 0, width * scale * 1000, height * scale * 1000)
            self.assertEqual(subject.paper_to_camera((0, 0), view_box, width, height), (-10, 5))
            self.assertEqual(subject.paper_to_camera(view_box[2:], view_box, width, height), (10, -5))
            point = ((2 + width / 2) * scale * 1000, (height / 2 - 3) * scale * 1000)
            x, y = subject.paper_to_camera(point, view_box, width, height)
            self.assertAlmostEqual(x, 2)
            self.assertAlmostEqual(y, 3)

    def test_portrait_and_nonzero_viewbox_origin(self):
        self.assertEqual(subject.paper_to_camera((10, 20), (10, 20, 100, 200), 10, 20), (-5, 10))
        self.assertEqual(subject.paper_to_camera((60, 120), (10, 20, 100, 200), 10, 20), (0, 0))

    def test_invalid_viewbox(self):
        for box in ("", "0 0 0 1", "0 0 1 -1", "0 0 1e999 1"):
            with self.subTest(box=box), self.assertRaises(ValueError):
                subject.parse_svg(f'<svg viewBox="{box}"/>')


if __name__ == "__main__":
    unittest.main()
