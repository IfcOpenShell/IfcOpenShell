# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import ifcopenshell.util.unit
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


class Project(blenderbim.core.tool.Project):
    @classmethod
    def append_all_types_from_template(cls, template):
        # TODO refactor
        filepath = os.path.join(bpy.context.scene.BIMProperties.data_dir, "libraries", template)
        bpy.ops.bim.select_library_file(filepath=filepath)
        for element in IfcStore.library_file.by_type("IfcTypeProduct"):
            bpy.ops.bim.append_library_element(definition=element.id())

    @classmethod
    def create_empty(cls, name):
        return bpy.data.objects.new(name, None)

    @classmethod
    def load_default_thumbnails(cls):
        if tool.Ifc.get().by_type("IfcElementType"):
            ifc_class = sorted(tool.Ifc.get().by_type("IfcElementType"), key=lambda e: e.is_a())[0].is_a()
            bpy.ops.bim.load_type_thumbnails(ifc_class=ifc_class)

    @classmethod
    def run_aggregate_assign_object(cls, relating_obj=None, related_obj=None):
        return blenderbim.core.aggregate.assign_object(
            tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=relating_obj, related_obj=related_obj
        )

    @classmethod
    def run_context_add_context(cls, context_type=None, context_identifier=None, target_view=None, parent=None):
        return blenderbim.core.context.add_context(
            tool.Ifc,
            context_type=context_type,
            context_identifier=context_identifier,
            target_view=target_view,
            parent=parent,
        )

    @classmethod
    def run_owner_add_organisation(cls):
        return blenderbim.core.owner.add_organisation(tool.Ifc)

    @classmethod
    def run_owner_add_person(cls):
        return blenderbim.core.owner.add_person(tool.Ifc)

    @classmethod
    def run_owner_add_person_and_organisation(cls, person=None, organisation=None):
        return blenderbim.core.owner.add_person_and_organisation(tool.Ifc, person=person, organisation=organisation)

    @classmethod
    def run_owner_set_user(cls, user=None):
        return blenderbim.core.owner.set_user(tool.Owner, user=user)

    @classmethod
    def run_root_assign_class(
        cls,
        obj=None,
        ifc_class=None,
        predefined_type=None,
        should_add_representation=True,
        context=None,
        ifc_representation_class=None,
    ):
        return blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            should_add_representation=should_add_representation,
            context=context,
            ifc_representation_class=ifc_representation_class,
        )

    @classmethod
    def run_unit_assign_scene_units(cls):
        return blenderbim.core.unit.assign_scene_units(tool.Ifc, tool.Unit)

    @classmethod
    def set_active_spatial_element(cls, obj):
        collection = obj.users_collection[0]
        queue = [bpy.context.view_layer.layer_collection]
        layer_collection = None

        while queue:
            layer = queue.pop()
            if layer.collection == collection:
                layer_collection = layer
                break
            queue.extend(list(layer.children))

        if layer_collection:
            bpy.context.view_layer.active_layer_collection = layer_collection

    @classmethod
    def set_context(cls, context):
        blenderbim.bim.handler.refresh_ui_data()
        bpy.context.scene.BIMRootProperties.contexts = str(context.id())

    @classmethod
    def set_default_context(cls):
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        if context:
            bpy.context.scene.BIMRootProperties.contexts = str(context.id())

    @classmethod
    def set_default_modeling_dimensions(cls):
        props = bpy.context.scene.BIMModelProperties
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props.extrusion_depth = 3 / unit_scale
        props.length = 1 / unit_scale
        props.rl1 = 0
        props.rl2 = 1 / unit_scale
        props.x = 0.5 / unit_scale
        props.y = 0.5 / unit_scale
        props.z = 0.5 / unit_scale
