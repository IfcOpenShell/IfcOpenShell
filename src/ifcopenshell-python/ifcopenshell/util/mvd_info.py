# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

try:
    from lark import Lark, Transformer
    from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken

    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False

from typing import Callable, Union
import re

if LARK_AVAILABLE:
    mvd_grammar = r"""
        start: entry+

        entry: "ViewDefinition" "[" simple_value_list "]"   -> view_definition
            | "Comment" "[" simple_value_list "]" -> comment
            | "ExchangeRequirement" "[" other_keyword "]" -> exchangerequirement
            | "Option" "[" other_keyword "]" -> option
            | GENERIC_KEYWORD "[" dynamic_option_word "]" -> dynamic_option

        GENERIC_KEYWORD: /[A-Za-z0-9_]+/

        simple_value_list: value ("," value)*

        value_list_set: value_set (";" value_set)*

        value_set: set_name ":" simple_value_list

        set_name: /[A-Za-z0-9_]+/

        value: /[A-Za-z0-9 _\.-]+/

        other_keyword: /[^\[\]]+/  
        
        dynamic_option_word: /[^\[\]]+/ 

        %import common.WS
        %ignore WS
    """

    parser = Lark(mvd_grammar, parser="lalr")

    class DescriptionTransform(Transformer):
        def __init__(self):
            self.view_definitions = []
            self.keywords = set()
            self.comments = ""
            self.exchange_requirements = ""
            self.options = ""
            self._dynamic = {}

        def view_definition(self, args):
            self.keywords.add("view_definitions")
            self.view_definitions.extend(args[0])

        def store_text_attribute(self, args, keyword):
            self.keywords.add(keyword)
            setattr(self, keyword, " ".join(" ".join(str(child) for child in args[0].children).split()))

        def comment(self, args):
            self.keywords.add("comments")
            self.comments = args[0] if len(args[0]) > 1 else args[0][0]

        def exchangerequirement(self, args):
            self.store_text_attribute(args, "exchange_requirements")

        def option(self, args):
            if v := parse_semicolon_separated_kv(" ".join(" ".join(str(child) for child in args[0].children).split())):
                setattr(self, "options", v)
            else:
                self.store_text_attribute(args, "options")

        def dynamic_option(self, args):
            try:
                original_keyword = str(args[0])
                key = original_keyword.lower()
                raw_text = args[1].children[0].value
                parsed_value = parse_semicolon_separated_kv(raw_text)
                self._dynamic[key] = (parsed_value, original_keyword)
                self.keywords.add(key)
                setattr(self, key, parsed_value)
            except Exception:
                setattr(self, key, None)

        def simple_value_list(self, args):
            return [str(arg) for arg in args]

        def value_list_set(self, args):
            return args

        def value_set(self, args):
            return [str(args[0])] + args[1]

        def value(self, args):
            return str(args[0])

        def set_name(self, args):
            return str(args[0])

    def parse_mvd(description):
        text = " ".join(description)
        parsed_description = DescriptionTransform()
        try:
            if not text:
                parsed_description.view_definitions = None
                return parsed_description
            parse_tree = parser.parse(text)
            parsed_description.transform(parse_tree)
        except (UnexpectedCharacters, UnexpectedEOF, UnexpectedToken):
            parsed_description.view_definitions = None
        return parsed_description

    def parse_semicolon_separated_kv(text: str) -> dict[str, str | list[str]] | None:
        if not re.search(r"\w+\s*:\s*[^:]+", text):
            return None
        result = {}
        try:
            pairs = text.split(";")
            for pair in pairs:
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    key = key.strip()
                    values = [v.strip() for v in value.split(",")]
                    result[key] = values[0] if len(values) == 1 else values
            return result
        except Exception:
            return None

else:

    def parse_mvd(description):
        return None


class MvdInfo:
    def __init__(self, header):
        self._header = header
        self._parsed = None

    def _ensure_parsed(self):
        if not LARK_AVAILABLE:
            return
        if self._parsed is None:
            self._parsed = parse_mvd(self._header.file_description.description)

    @property
    def description(self) -> list[str]:
        return self._header.file_description.description

    @description.setter
    def description(self, new_description: list[str]):
        self._header.file_description.description = tuple(new_description)
        self._parsed = None

    @property
    def view_definitions(self):
        self._ensure_parsed()
        if not self._parsed or self._parsed.view_definitions is None:
            return None  #

        vd = self._parsed.view_definitions
        vd_list = vd if isinstance(vd, list) else [vd] if vd else []
        return AutoCommitList(
            vd_list,
            callback=lambda val: (self._update_keyword("ViewDefinition", val), setattr(self, "_parsed", None)),
            formatter=lambda lst: ",".join(str(i) for i in lst),
        )

    @view_definitions.setter
    def view_definitions(self, new_value: Union[str, list[str]]):
        if isinstance(new_value, list):
            value = ", ".join(new_value)
        else:
            value = str(new_value)
        self._update_keyword("ViewDefinition", value)

    @property
    def comments(self):
        self._ensure_parsed()
        comments = self._parsed.comments
        comment_list = comments if isinstance(comments, list) else [comments] if comments else []
        return AutoCommitList(
            comment_list,
            callback=lambda val: self._update_keyword("Comment", val),
            formatter=lambda lst: ", ".join(str(i) for i in lst),
        )

    @comments.setter
    def comments(self, new_value: Union[str, list[str]]):
        if isinstance(new_value, list):
            value = ", ".join(new_value)
        else:
            value = str(new_value)
        self._update_keyword("Comment", value)

    @property
    def exchange_requirements(self):
        self._ensure_parsed()
        return self._parsed.exchange_requirements if self._parsed else None

    @exchange_requirements.setter
    def exchange_requirements(self, new_value: str):
        self._update_keyword("ExchangeRequirement", new_value)

    @property
    def options(self):
        self._ensure_parsed()
        if isinstance(self._parsed.options, dict):
            return DictionaryHandler(self._parsed.options, self, "Option")
        return self._parsed.options if self._parsed else None

    @options.setter
    def options(self, new_value: str):
        self._update_keyword("Option", new_value)

    @property
    def keywords(self):
        self._ensure_parsed()
        return self._parsed.keywords if self._parsed else set()

    def _update_keyword(self, keyword: str, new_value: str):
        updated = False
        new_line = f"{keyword} [{new_value}]"
        lines = []
        for line in self.description:
            if line.strip().startswith(f"{keyword} ["):
                lines.append(new_line)
                updated = True
            else:
                lines.append(line)
        if not updated:
            lines.append(new_line)
        self.description = lines

    def __getattr__(self, name):
        self._ensure_parsed()
        if hasattr(self._parsed, "_dynamic"):
            name_lc = name.lower()
            if name_lc in self._parsed._dynamic:
                value, original_keyword = self._parsed._dynamic[name_lc]
                return DictionaryHandler(value, self, original_keyword)
        raise AttributeError(f"'MvdInfo' object has no attribute '{name}'")

    def __dir__(self):
        base = super().__dir__()
        if self._parsed and hasattr(self._parsed, "_dynamic"):
            return base + [kw for _, kw in self._parsed._dynamic.values()]
        return base


class DictionaryHandler(dict):
    def __init__(self, initial_data, mvdinfo, keyword):
        super().__init__()
        self._mvdinfo = mvdinfo
        self._keyword = keyword
        for k, v in initial_data.items():
            if isinstance(v, list):
                super().__setitem__(k, AutoCommitList(v, self._commit))
            else:
                super().__setitem__(k, v)

    def _commit(self):
        new_value = "; ".join(f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in self.items())
        self._mvdinfo._update_keyword(self._keyword, new_value)

    def __setitem__(self, key, value):
        if isinstance(value, list):
            value = AutoCommitList(value, self._commit)
        super().__setitem__(key, value)
        self._commit()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._commit()


class AutoCommitList(list):
    "ensures keyword attributes are written back to ifcopenshell.file.header"

    def __init__(self, iterable, callback, formatter=None):
        super().__init__(iterable)
        self._callback = callback
        self._formatter = formatter

    def _commit(self):
        if self._formatter:
            self._callback(self._formatter(self))
        else:
            self._callback()

    def append(self, item):
        super().append(item)
        self._commit()

    def extend(self, iterable):
        super().extend(iterable)
        self._commit()

    def insert(self, index, item):
        super().insert(index, item)
        self._commit()

    def remove(self, item):
        super().remove(item)
        self._commit()

    def pop(self, index=-1):
        item = super().pop(index)
        self._commit()
        return item

    def clear(self):
        super().clear()
        self._commit()

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._commit()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._commit()
