# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_context(
    ifc: tool.Ifc,
    context_type: Optional[str] = None,
    context_identifier: Optional[str] = None,
    target_view: Optional[str] = None,
    parent: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    return ifc.run(
        "context.add_context",
        context_type=context_type,
        context_identifier=context_identifier,
        target_view=target_view,
        parent=parent,
    )


def remove_context(ifc: tool.Ifc, context: ifcopenshell.entity_instance) -> None:
    ifc.run("context.remove_context", context=context)


def enable_editing_context(context_tool: tool.Context, context: ifcopenshell.entity_instance) -> None:
    context_tool.set_context(context)
    context_tool.import_attributes()


def disable_editing_context(context: tool.Context) -> None:
    context.clear_context()


def edit_context(ifc: tool.Ifc, context: tool.Context) -> None:
    ifc.run("context.edit_context", context=context.get_context(), attributes=context.export_attributes())
    disable_editing_context(context)
