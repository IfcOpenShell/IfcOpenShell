
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
    operator.NewBcfProject,
    operator.LoadBcfProject,
    operator.LoadBcfTopics,
    operator.LoadBcfTopic,
    operator.LoadBcfComments,
    operator.EditBcfProjectName,
    operator.EditBcfAuthor,
    operator.EditBcfTopicName,
    operator.EditBcfTopic,
    operator.SaveBcfProject,
    operator.AddBcfTopic,
    operator.AddBcfHeaderFile,
    operator.AddBcfBimSnippet,
    operator.AddBcfReferenceLink,
    operator.AddBcfDocumentReference,
    operator.AddBcfLabel,
    operator.AddBcfRelatedTopic,
    operator.ViewBcfTopic,
    operator.RemoveBcfComment,
    operator.RemoveBcfBimSnippet,
    operator.RemoveBcfReferenceLink,
    operator.RemoveBcfDocumentReference,
    operator.RemoveBcfRelatedTopic,
    operator.EditBcfReferenceLinks,
    operator.EditBcfLabels,
    operator.RemoveBcfLabel,
    operator.EditBcfComment,
    operator.AddBcfComment,
    operator.ActivateBcfViewpoint,
    operator.AddBcfViewpoint,
    operator.RemoveBcfViewpoint,
    operator.RemoveBcfFile,
    operator.OpenBcfReferenceLink,
    operator.SelectBcfHeaderFile,
    operator.SelectBcfBimSnippetReference,
    operator.SelectBcfDocumentReference,
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
