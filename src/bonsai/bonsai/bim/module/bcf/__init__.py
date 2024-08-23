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
from . import ui, prop, operator

classes = (
    operator.ActivateBcfViewpoint,
    operator.AddBcfBimSnippet,
    operator.AddBcfComment,
    operator.AddBcfDocumentReference,
    operator.AddBcfHeaderFile,
    operator.AddBcfLabel,
    operator.AddBcfReferenceLink,
    operator.AddBcfRelatedTopic,
    operator.AddBcfTopic,
    operator.AddBcfViewpoint,
    operator.BCFFileHandlerOperator,
    operator.BIM_FH_import_bcf,
    operator.EditBcfComment,
    operator.EditBcfLabels,
    operator.EditBcfProjectName,
    operator.EditBcfReferenceLinks,
    operator.EditBcfTopic,
    operator.EditBcfTopicName,
    operator.ExtractBcfFile,
    operator.LoadBcfComments,
    operator.LoadBcfHeaderIfcFile,
    operator.LoadBcfProject,
    operator.LoadBcfTopic,
    operator.LoadBcfTopics,
    operator.NewBcfProject,
    operator.OpenBcfReferenceLink,
    operator.RemoveBcfBimSnippet,
    operator.RemoveBcfComment,
    operator.RemoveBcfDocumentReference,
    operator.RemoveBcfFile,
    operator.RemoveBcfLabel,
    operator.RemoveBcfReferenceLink,
    operator.RemoveBcfRelatedTopic,
    operator.RemoveBcfTopic,
    operator.RemoveBcfViewpoint,
    operator.SaveBcfProject,
    operator.SelectBcfBimSnippetReference,
    operator.SelectBcfDocumentReference,
    operator.SelectBcfHeaderFile,
    operator.UnloadBcfProject,
    operator.ViewBcfTopic,
    prop.BcfReferenceLink,
    prop.BcfLabel,
    prop.BcfBimSnippet,
    prop.BcfDocumentReference,
    prop.BcfComment,
    prop.BcfTopic,
    prop.BCFProperties,
    ui.BIM_PT_bcf,
    ui.BIM_PT_bcf_metadata,
    ui.BIM_PT_bcf_comments,
)


def register():
    bpy.types.Scene.BCFProperties = bpy.props.PointerProperty(type=prop.BCFProperties)


def unregister():
    del bpy.types.Scene.BCFProperties
