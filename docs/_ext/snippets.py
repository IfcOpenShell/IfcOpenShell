# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell Contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Code blocks with a tab per language, cut from the tested example programs.

``.. snippet:: hello_world/by_guid`` includes the ``tag::example`` region of
``hello_world/by_guid.cpp``, ``.py``, and ``.mjs`` under
``ifcopenshell/examples``. A language whose file does not exist gets a greyed
out tab. ``.. snippet-parity::`` renders the table of which snippet exists in
which language.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)

EXAMPLES = "ifcopenshell/examples"
PARITY_DOC = "ifcopenshell/parity"


@dataclass(frozen=True)
class Language:
    key: str
    label: str
    suffix: str
    comment: str
    pygments: str


LANGUAGES = (
    Language("cpp", "C++", ".cpp", "//", "cpp"),
    Language("python", "Python", ".py", "#", "python"),
    Language("js", "JavaScript", ".mjs", "//", "javascript"),
)
LANGUAGE_KEYS = tuple(language.key for language in LANGUAGES)

YES, TODO, NA = "yes", "todo", "na"


def language_list(argument: str) -> list[str]:
    keys = [key.strip() for key in argument.replace(",", " ").split()]
    for key in keys:
        if key not in LANGUAGE_KEYS:
            raise ValueError(f"unknown language {key!r}, expected one of {', '.join(LANGUAGE_KEYS)}")
    return keys


class LangNoteDirective(SphinxDirective):
    """Content inside a snippet that is only shown in the tab of one language."""

    required_arguments = 1
    has_content = True

    def run(self):
        language = self.arguments[0]
        if language not in LANGUAGE_KEYS:
            raise self.error(f"unknown language {language!r}")
        node = nodes.container(classes=["ios-lang-note"], ios_language=language)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def find_region(lines: list[str], comment: str, tag: str) -> tuple[int, int] | None:
    """Return the 1-based, inclusive line range between the tag markers."""
    start = end = None
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == f"{comment} tag::{tag}":
            start = number + 1
        elif stripped == f"{comment} end::{tag}" and start is not None:
            end = number - 1
            break
    if start is None or end is None or end < start:
        return None
    return start, end


MARKER = re.compile(r"^\s*(#|//) (tag|end)::\S+\s*$")


def visible_ranges(lines: list[str], first: int, last: int) -> str:
    """Line ranges for ``:lines:`` which leave out nested tag markers."""
    ranges = []
    for number in range(first, last + 1):
        if MARKER.match(lines[number - 1]):
            continue
        if ranges and ranges[-1][1] == number - 1:
            ranges[-1][1] = number
        else:
            ranges.append([number, number])
    return ",".join(f"{start}-{end}" for start, end in ranges)


def indentation(lines: list[str]) -> int:
    widths = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip() and not MARKER.match(line)]
    return min(widths, default=0)


class SnippetDirective(SphinxDirective):
    required_arguments = 1
    has_content = True
    option_spec = {
        "tag": directives.unchanged_required,
        "na": language_list,
        "title": directives.unchanged_required,
        **{key: directives.unchanged_required for key in LANGUAGE_KEYS},
        **{f"caption-{key}": directives.unchanged_required for key in LANGUAGE_KEYS},
    }

    def run(self):
        name = self.arguments[0]
        default_tag = self.options.get("tag", "example")
        not_available = set(self.options.get("na", []))
        examples = Path(self.env.srcdir) / EXAMPLES

        included = {}
        status = {}
        for language in LANGUAGES:
            path, _, tag = self.options.get(language.key, name).partition("#")
            tag = tag or default_tag
            if not path.endswith(language.suffix):
                path += language.suffix
            source = examples / path
            if not source.is_file():
                status[language.key] = NA if language.key in not_available else TODO
                if language.key in self.options:
                    logger.warning(f"snippet file {EXAMPLES}/{path} does not exist", location=self.get_location())
                continue
            lines = source.read_text(encoding="utf-8").splitlines()
            region = find_region(lines, language.comment, tag)
            if region is None:
                if language.key in not_available:
                    status[language.key] = NA
                    continue
                if language.key in self.options or tag == "example":
                    logger.warning(f"no '{language.comment} tag::{tag}' region in {EXAMPLES}/{path}", location=self.get_location())
                status[language.key] = TODO
                continue
            if language.key in not_available:
                logger.warning(f"{path} has the snippet, but {language.key} is marked as not available", location=self.get_location())
            included[language.key] = (
                path,
                visible_ranges(lines, *region),
                indentation(lines[region[0] - 1 : region[1]]),
            )
            status[language.key] = YES

        notes = {key: [] for key in LANGUAGE_KEYS}
        shared = nodes.container()
        if self.content:
            parsed = nodes.container()
            self.state.nested_parse(self.content, self.content_offset, parsed)
            for child in parsed.children:
                if isinstance(child, nodes.container) and child.get("ios_language"):
                    notes[child["ios_language"]].append(child)
                else:
                    shared += child

        self.record(name if default_tag == "example" else f"{name}#{default_tag}", status)

        available = [language for language in LANGUAGES if language.key in included]
        if not available:
            raise self.error(f"snippet {name!r} has no program in any language")
        single = len(available) == 1 and all(status[language.key] == NA for language in LANGUAGES if language not in available)

        rst = StringList()
        source = self.get_source_info()[0]

        def add(line: str, indent: int):
            rst.append(" " * indent + line, source)

        def add_body(language: Language, indent: int):
            if language.key in included:
                path, lines, dedent = included[language.key]
                add(f".. literalinclude:: /{EXAMPLES}/{path}", indent)
                add(f":language: {language.pygments}", indent + 3)
                add(f":lines: {lines}", indent + 3)
                if dedent:
                    add(f":dedent: {dedent}", indent + 3)
                add(f":caption: {path}", indent + 3)
                add("", indent)
            elif status[language.key] == NA:
                add(".. container:: ios-snippet-missing", indent)
                add("", indent)
                add(f"{language.label} has no equivalent of this example.", indent + 3)
                add("", indent)
            else:
                add(".. container:: ios-snippet-missing", indent)
                add("", indent)
                add(
                    f"This example has not been written in {language.label} yet. "
                    f"See :doc:`/{PARITY_DOC}` for what exists in each language.",
                    indent + 3,
                )
                add("", indent)
            caption = self.options.get(f"caption-{language.key}")
            if caption:
                add(".. container:: ios-snippet-caption", indent)
                add("", indent)
                for line in caption.splitlines():
                    add(line.strip(), indent + 3)
                add("", indent)
            add(f".. container:: ios-note-slot ios-note-slot-{language.key}", indent)
            add("", indent)
            add("..", indent + 3)
            add("", indent)

        if single:
            language = available[0]
            add(f".. container:: ios-snippet ios-snippet-single ios-lang-{language.key}", 0)
            add("", 0)
            add(f".. container:: ios-only-badge", 3)
            add("", 0)
            add(f"{language.label} only", 6)
            add("", 0)
            add_body(language, 3)
        else:
            add(".. tab-set::", 0)
            add(":class: ios-snippet", 3)
            add("", 0)
            for language in LANGUAGES:
                classes = f"ios-lang ios-lang-{language.key}"
                if language.key not in included:
                    classes += " ios-lang-missing"
                add(f".. tab-item:: {language.label}", 3)
                add(f":class-label: {classes}", 6)
                if language is available[0]:
                    add(":selected:", 6)
                add("", 0)
                add_body(language, 6)

        container = nodes.container()
        self.state.nested_parse(rst, 0, container)
        for slot in list(container.findall(nodes.container)):
            slot_classes = slot.get("classes", [])
            if "ios-note-slot" not in slot_classes:
                continue
            language = next(cls.removeprefix("ios-note-slot-") for cls in slot_classes if cls.startswith("ios-note-slot-"))
            if notes[language]:
                slot.replace_self(notes[language])
            else:
                slot.parent.remove(slot)
        return [*container.children, *shared.children]

    def record(self, name: str, status: dict[str, str]):
        section = self.state.parent
        while section is not None and not isinstance(section, nodes.section):
            section = section.parent
        title = self.options.get("title")
        anchor = ""
        if section is not None:
            title = title or section[0].astext()
            anchor = section["ids"][0] if section["ids"] else ""
        if not hasattr(self.env, "ios_snippets"):
            self.env.ios_snippets = {}
        self.env.ios_snippets.setdefault(self.env.docname, []).append(
            {"name": name, "title": title or name, "anchor": anchor, "status": status}
        )


class parity_placeholder(nodes.General, nodes.Element):
    pass


class ParityDirective(SphinxDirective):
    def run(self):
        return [parity_placeholder()]


def document_order(env) -> list[str]:
    order = []

    def visit(docname: str):
        if docname in order:
            return
        order.append(docname)
        for child in env.toctree_includes.get(docname, []):
            visit(child)

    visit(env.config.root_doc)
    return order


STATUS_TEXT = {YES: "✓", TODO: "to do", NA: "n/a"}


def build_parity_table(app: Sphinx, fromdocname: str) -> list[nodes.Node]:
    env = app.env
    snippets = getattr(env, "ios_snippets", {})
    order = {docname: index for index, docname in enumerate(document_order(env))}
    docnames = sorted(snippets, key=lambda docname: order.get(docname, len(order)))

    totals = {key: 0 for key in LANGUAGE_KEYS}
    count = 0
    for docname in docnames:
        for snippet in snippets[docname]:
            count += 1
            for key in LANGUAGE_KEYS:
                totals[key] += snippet["status"][key] == YES

    summary = nodes.bullet_list()
    for language in LANGUAGES:
        todo = sum(snippet["status"][language.key] == TODO for docname in docnames for snippet in snippets[docname])
        item = nodes.list_item()
        item += nodes.paragraph(text=f"{language.label}: {totals[language.key]} of {count} snippets, {todo} to do.")
        summary += item

    result = [summary]
    for docname in docnames:
        title = env.titles[docname].astext() if docname in env.titles else docname
        uri = app.builder.get_relative_uri(fromdocname, docname)
        heading = nodes.rubric()
        heading += nodes.reference("", title, refuri=uri, internal=True)
        result.append(heading)

        table = nodes.table(classes=["ios-parity"])
        group = nodes.tgroup(cols=1 + len(LANGUAGES))
        table += group
        group += nodes.colspec(colwidth=55)
        for _ in LANGUAGES:
            group += nodes.colspec(colwidth=15)
        head = nodes.thead()
        group += head
        row = nodes.row()
        for text in ("Section", *(language.label for language in LANGUAGES)):
            entry = nodes.entry()
            entry += nodes.paragraph(text=text)
            row += entry
        head += row
        body = nodes.tbody()
        group += body
        for snippet in snippets[docname]:
            row = nodes.row()
            entry = nodes.entry()
            paragraph = nodes.paragraph()
            refuri = f"{uri}#{snippet['anchor']}" if snippet["anchor"] else uri
            paragraph += nodes.reference("", snippet["title"], refuri=refuri, internal=True)
            paragraph += nodes.Text(" ")
            paragraph += nodes.literal(text=snippet["name"])
            entry += paragraph
            row += entry
            for language in LANGUAGES:
                state = snippet["status"][language.key]
                entry = nodes.entry(classes=[f"ios-parity-{state}"])
                entry += nodes.paragraph(text=STATUS_TEXT[state])
                row += entry
            body += row
        result.append(table)
    return result


def resolve_parity(app: Sphinx, doctree: nodes.document, docname: str):
    for placeholder in list(doctree.findall(parity_placeholder)):
        placeholder.replace_self(build_parity_table(app, docname))


def purge(app: Sphinx, env, docname: str):
    getattr(env, "ios_snippets", {}).pop(docname, None)


def merge(app: Sphinx, env, docnames, other):
    if not hasattr(env, "ios_snippets"):
        env.ios_snippets = {}
    for docname, snippets in getattr(other, "ios_snippets", {}).items():
        if docname in docnames:
            env.ios_snippets[docname] = snippets


def always_rebuild_parity(app: Sphinx, env, added, changed, removed):
    return [PARITY_DOC] if PARITY_DOC in env.found_docs else []


def setup(app: Sphinx):
    app.add_node(parity_placeholder)
    app.add_directive("snippet", SnippetDirective)
    app.add_directive("lang-note", LangNoteDirective)
    app.add_directive("snippet-parity", ParityDirective)
    app.connect("doctree-resolved", resolve_parity)
    app.connect("env-purge-doc", purge)
    app.connect("env-merge-info", merge)
    app.connect("env-get-outdated", always_rebuild_parity)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
