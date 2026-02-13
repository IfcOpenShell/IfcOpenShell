# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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

import bpy
from bpy.props import BoolProperty, CollectionProperty, StringProperty
from bpy.types import PropertyGroup


class ClipboardSection(PropertyGroup):
    name: StringProperty(name="Name")
    is_expanded: BoolProperty(name="Is Expanded", default=False)


class BIMClipboardProperties(PropertyGroup):
    sections: CollectionProperty(type=ClipboardSection, name="Sections")
    
    def ensure_sections(self):
        """Ensure all required sections exist in the collection."""
        section_names = ["products", "product_types", "materials", "surface_styles"]
        existing_names = {s.name for s in self.sections}
        
        for name in section_names:
            if name not in existing_names:
                section = self.sections.add()
                section.name = name
    
    def get_section(self, name):
        """Get a section by name, returns None if not found."""
        for section in self.sections:
            if section.name == name:
                return section
        return None
