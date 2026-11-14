# This file was generated with the assistance of an AI coding tool.

from bonsai.bim.module.drawing.svgwriter import strip_css_comments


def test_strip_css_comments_removes_single_and_multi_line_comments():
    css = "/* header */\n.a { fill: red; } /* trailing */\n/* multi\nline */\n.b { fill: blue; }"
    assert strip_css_comments(css) == "\n.a { fill: red; } \n\n.b { fill: blue; }"


def test_strip_css_comments_leaves_css_without_comments_untouched():
    css = ".a { fill: red; }\n.b { fill: blue; }"
    assert strip_css_comments(css) == css
