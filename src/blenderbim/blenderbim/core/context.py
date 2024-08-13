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


def add_context(ifc, context_type=None, context_identifier=None, target_view=None, parent=None):
    return ifc.run(
        "context.add_context",
        context_type=context_type,
        context_identifier=context_identifier,
        target_view=target_view,
        parent=parent,
    )


def remove_context(ifc, context=None):
    ifc.run("context.remove_context", context=context)


def enable_editing_context(context_tool, context=None):
    context_tool.set_context(context)
    context_tool.import_attributes()


def disable_editing_context(context):
    context.clear_context()


def edit_context(ifc, context):
    ifc.run("context.edit_context", context=context.get_context(), attributes=context.export_attributes())
    disable_editing_context(context)
