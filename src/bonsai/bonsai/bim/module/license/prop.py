# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# AI-assisted development tool was used in writing this file.

from typing import TYPE_CHECKING

from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import PropertyGroup

from bonsai.tool.license import SPDX_ENUM_ITEMS


class BIMLicenseProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    spdx_license_identifier: EnumProperty(
        name="License",
        items=SPDX_ENUM_ITEMS,
        description="SPDX license identifier",
    )
    copyright_notice: StringProperty(name="Copyright Notice", description='e.g. "© 2026 Acme Architecture Ltd"')
    attribution_text: StringProperty(name="Attribution Text", description="Text to use when crediting this work")
    source_url: StringProperty(name="Source URL", description="URL to the original source or license text")

    if TYPE_CHECKING:
        is_editing: bool
        spdx_license_identifier: str
        copyright_notice: str
        attribution_text: str
        source_url: str
