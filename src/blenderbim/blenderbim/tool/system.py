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

import bpy
import ifcopenshell.util.system
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.bim import import_ifc
import re
from mathutils import Matrix, Vector


class System(blenderbim.core.tool.System):
    @classmethod
    def add_ports(cls, obj, add_start_port=True, add_end_port=True, offset_end_port=None):
        def add_port(mep_element, matrix):
            port = tool.Ifc.run("system.add_port", element=mep_element)
            port.FlowDirection = "NOTDEFINED"
            port.PredefinedType = tool.System.get_port_predefined_type(mep_element)
            tool.Ifc.run("geometry.edit_object_placement", product=port, matrix=matrix, is_si=True)
            return port

        # make sure obj.dimensions and .matrix_world has valid data
        bpy.context.view_layer.update()
        # need to make sure .ObjectPlacement is also updated when we're going to add ports
        if tool.Ifc.is_moved(obj):
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        mep_element = tool.Ifc.get_entity(obj)
        length = obj.dimensions.z
        ports = []
        if add_start_port:
            ports.append(add_port(mep_element, obj.matrix_world @ Matrix()))
        if add_end_port:
            m = obj.matrix_world @ Matrix.Translation((0, 0, length))
            if offset_end_port:
                m.translation += offset_end_port
            ports.append(add_port(mep_element, m))
        return ports

    @classmethod
    def create_empty_at_cursor_with_element_orientation(cls, element):
        element_obj = tool.Ifc.get_object(element)
        obj = bpy.data.objects.new("Port", None)
        obj.matrix_world = element_obj.matrix_world
        obj.matrix_world.translation = bpy.context.scene.cursor.matrix.translation
        bpy.context.scene.collection.objects.link(obj)
        return obj

    @classmethod
    def delete_element_objects(cls, elements):
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                bpy.data.objects.remove(obj)

    @classmethod
    def disable_editing_system(cls):
        bpy.context.scene.BIMSystemProperties.active_system_id = 0

    @classmethod
    def disable_system_editing_ui(cls):
        bpy.context.scene.BIMSystemProperties.is_editing = False

    @classmethod
    def enable_system_editing_ui(cls):
        bpy.context.scene.BIMSystemProperties.is_editing = True

    @classmethod
    def export_system_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMSystemProperties.system_attributes)

    @classmethod
    def get_connected_port(cls, port):
        return ifcopenshell.util.system.get_connected_port(port)

    @classmethod
    def get_ports(cls, element):
        return ifcopenshell.util.system.get_ports(element)

    @classmethod
    def get_port_relating_element(cls, port):
        if tool.Ifc.get_schema() == "IFC2X3":
            element = port.ContainedIn[0].RelatedElement
        else:
            element = port.Nests[0].RelatingObject
        return element

    @classmethod
    def get_port_predefined_type(cls, mep_element):
        split_camel_case = lambda x: re.findall("[A-Z][^A-Z]*", x)
        class_name = "".join(split_camel_case(mep_element.is_a())[1:-1]).upper()
        if class_name == "CONVEYOR":
            return "NOTDEFINED"
        return class_name

    @classmethod
    def import_system_attributes(cls, system):
        props = bpy.context.scene.BIMSystemProperties
        props.system_attributes.clear()
        blenderbim.bim.helper.import_attributes2(system, props.system_attributes)

    @classmethod
    def import_systems(cls):
        props = bpy.context.scene.BIMSystemProperties
        props.systems.clear()
        for system in tool.Ifc.get().by_type("IfcSystem"):
            if system.is_a() in ["IfcStructuralAnalysisModel"]:
                continue
            new = props.systems.add()
            new.ifc_definition_id = system.id()
            new.name = system.Name or "Unnamed"
            new.ifc_class = system.is_a()

    @classmethod
    def load_ports(cls, element, ports):
        if not ports:
            return
        obj = tool.Ifc.get_object(element)
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ports = set(ports)
        ports -= ifc_importer.create_products(ports)
        for port in ports or []:
            if tool.Ifc.get_object(port):
                continue
            port_obj = ifc_importer.create_product(port)
            if obj:
                port_obj.parent = obj
                port_obj.matrix_parent_inverse = obj.matrix_world.inverted()
        ifc_importer.place_objects_in_collections()

    @classmethod
    def run_geometry_edit_object_placement(cls, obj=None):
        return blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

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
    def select_system_products(cls, system):
        tool.Spatial.select_products(ifcopenshell.util.system.get_system_elements(system))

    @classmethod
    def set_active_system(cls, system):
        bpy.context.scene.BIMSystemProperties.active_system_id = system.id()
