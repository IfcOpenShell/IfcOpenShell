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

import bpy
import blenderbim.tool as tool


def refresh():
    ContextData.is_loaded = False


class ContextData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"contexts": cls.get_contexts()}
        cls.is_loaded = True

    @classmethod
    def get_contexts(cls):
        results = []
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            results.append(
                {
                    "id": context.id(),
                    "context_type": context.ContextType,
                    "subcontexts": cls.get_subcontexts(context),
                    "is_editing": bpy.context.scene.BIMContextProperties.active_context_id == context.id(),
                    "props": bpy.context.scene.BIMContextProperties.context_attributes,
                }
            )
        return results

    @classmethod
    def get_subcontexts(cls, context):
        results = []
        for subcontext in context.HasSubContexts:
            results.append(
                {
                    "id": subcontext.id(),
                    "context_type": subcontext.ContextType,
                    "context_identifier": subcontext.ContextIdentifier,
                    "target_view": subcontext.TargetView,
                    "is_editing": bpy.context.scene.BIMContextProperties.active_context_id == subcontext.id(),
                    "props": bpy.context.scene.BIMContextProperties.context_attributes,
                }
            )
        return results
