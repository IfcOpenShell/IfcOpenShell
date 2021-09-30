# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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


def enable_editing_context(context_editor, context=None):
    context_editor.set_context(context)
    context_editor.import_attributes()


def disable_editing_context(context_editor):
    context_editor.clear_context()


def edit_context(ifc, context_editor):
    ifc.run("context.edit_context", context=context_editor.get_context(), attributes=context_editor.export_attributes())
    disable_editing_context(context_editor)
