
# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from . import ui, prop, operator

classes = (
    operator.LoadInformation,
    operator.LoadDocumentReferences,
    operator.DisableDocumentEditingUI,
    operator.EnableEditingDocument,
    operator.DisableEditingDocument,
    operator.AddInformation,
    operator.AddDocumentReference,
    operator.EditInformation,
    operator.EditDocumentReference,
    operator.RemoveDocument,
    operator.EnableAssigningDocument,
    operator.DisableAssigningDocument,
    operator.AssignDocument,
    operator.UnassignDocument,
    prop.Document,
    prop.BIMDocumentProperties,
    prop.BIMObjectDocumentProperties,
    ui.BIM_PT_documents,
    ui.BIM_PT_object_documents,
    ui.BIM_UL_documents,
    ui.BIM_UL_object_documents,
)


def register():
    bpy.types.Scene.BIMDocumentProperties = bpy.props.PointerProperty(type=prop.BIMDocumentProperties)
    bpy.types.Object.BIMObjectDocumentProperties = bpy.props.PointerProperty(type=prop.BIMObjectDocumentProperties)


def unregister():
    del bpy.types.Scene.BIMDocumentProperties
    del bpy.types.Object.BIMObjectDocumentProperties
