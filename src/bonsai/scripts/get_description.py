# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import html
import json
from pathlib import Path
import ifcopenshell


class Describer:
    def describe(self):
        # BuildingSMART does not provide a computer interpretable set of
        # descriptions. They provide HTML docs, which contained malformed /
        # invalid HTML. Therefore, this dodgy hack was written.
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")

        self.html_sources = {}
        self.get_html_sources()

        self.entity_descriptions = {}
        self.enum_descriptions = {}
        for entity in schema.entities():
            name = entity.name()
            self.get_entity_description(name)
            for attribute in entity.attributes():
                try:
                    attribute = attribute.type_of_attribute().declared_type()
                except:
                    continue
                if isinstance(attribute, str):
                    continue
                if "Enum" in attribute.name() and "Enumeration" not in attribute.name():
                    self.get_enum_descriptions(attribute)

        with open("entity_descriptions.json", "w") as f:
            f.write(json.dumps(self.entity_descriptions, indent=4))
        with open("enum_descriptions.json", "w") as f:
            f.write(json.dumps(self.enum_descriptions, indent=4))

    def get_html_sources(self):
        html_dir = "/home/dion/Projects/IfcOpenShell/src/bonsai/descriptions/IFC4_3/RC1/HTML"
        for filename in Path(html_dir).rglob("*.htm"):
            if "lexical" not in str(filename):
                continue
            name = os.path.basename(filename)[0:-4]
            self.html_sources[name] = filename

    def get_entity_description(self, name):
        if name.lower() not in self.html_sources:
            return
        with open(self.html_sources[name.lower()]) as f:
            for line in f:
                if "Entity definition" in line:
                    self.entity_descriptions[name] = html.unescape(
                        re.sub("<.*?>", "", line.strip().replace("Entity definition", ""))
                    )

    def get_enum_descriptions(self, enum):
        if enum.name().lower() not in self.html_sources:
            return
        print(enum.name())
        print(dir(enum))
        for item in enum.enumeration_items():
            with open(self.html_sources[enum.name().lower()]) as f:
                for line in f:
                    if "<td>" + item + "</td>" in line:
                        self.enum_descriptions.setdefault(enum.name(), {})[item] = html.unescape(
                            re.sub("<.*?>", "", line.strip().replace(item, ""))
                        )


describer = Describer()
describer.describe()
