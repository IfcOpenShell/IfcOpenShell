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

import bpy

from . import operator, prop, ui

classes = (
    operator.AddDocumentReference,
    operator.AddInformation,
    operator.AssignDocument,
    operator.DisableDocumentEditingUI,
    operator.DisableObjectDocumentEditingUI,
    operator.DisableEditingDocument,
    operator.EditDocument,
    operator.EnableEditingDocument,
    operator.LoadObjectDocuments,
    operator.LoadProjectDocuments,
    operator.RemoveDocument,
    operator.SelectDocumentObjects,
    operator.ToggleDocument,
    operator.UnassignDocument,
    operator.OpenIFCDocument,
    prop.Document,
    prop.DocumentObject,
    prop.BIMDocumentProperties,
    ui.BIM_PT_documents,
    ui.BIM_PT_object_documents,
    ui.BIM_UL_documents,
    ui.BIM_UL_document_objects,
)


def register():
    bpy.types.Scene.BIMDocumentProperties = bpy.props.PointerProperty(type=prop.BIMDocumentProperties)


def unregister():
    del bpy.types.Scene.BIMDocumentProperties
