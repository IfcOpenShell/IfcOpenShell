# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.api
import bonsai.core.tool
import bonsai.tool as tool
import numpy as np
from test.bim.bootstrap import NewFile
from bonsai.tool.system import System as subject
from mathutils import Euler, Vector, Matrix
from math import pi


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.System)


class TestAddPorts(NewFile):
    def setup_mep_segment(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        obj = bpy.data.objects["Cube"]
        obj.scale = (1, 1, 5)
        bpy.ops.bim.assign_class(ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        obj.matrix_world = Euler((pi / 2, 0, pi / 2)).to_matrix().to_4x4() @ obj.matrix_world
        # move origin
        for v in obj.data.vertices:
            v.co += Vector((0, 0, 2.5))
        return obj, element

    def check_ports_matrices(self, ports, expected_matrices):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port, expected_matrix in zip(ports, expected_matrices, strict=True):
            port_matrix = tool.Model.get_element_matrix(port)
            port_matrix.translation *= si_conversion
            assert np.allclose(port_matrix, expected_matrix, atol=1.0e-5)

    def test_run(self):
        # default use
        obj, element = self.setup_mep_segment()
        ports = subject.add_ports(obj)
        assert len(subject.get_ports(element)) == len(ports)
        self.check_ports_matrices(ports, (obj.matrix_world, obj.matrix_world @ Matrix.Translation((0, 0, 5))))

        # skip end port
        obj, element = self.setup_mep_segment()
        ports = subject.add_ports(obj, add_end_port=False)
        self.check_ports_matrices(ports, (obj.matrix_world,))

        # skip start port
        obj, element = self.setup_mep_segment()
        ports = subject.add_ports(obj, add_start_port=False)
        self.check_ports_matrices(ports, (obj.matrix_world @ Matrix.Translation((0, 0, 5)),))

        # position end port
        obj, element = self.setup_mep_segment()
        ports = subject.add_ports(obj, end_port_pos=Vector((1, 2, 3)))
        translated_matrix = obj.matrix_world.copy()
        translated_matrix.translation = (1, 2, 3)
        self.check_ports_matrices(ports, (obj.matrix_world, translated_matrix))

        # offset end port
        obj, element = self.setup_mep_segment()
        ports = subject.add_ports(obj, offset_end_port=Vector((0, 0, 1)))
        translated_matrix = obj.matrix_world.copy()
        translated_matrix.translation = (5, 0, 1)
        self.check_ports_matrices(ports, (obj.matrix_world, translated_matrix))


class TestCreateEmptyAtCursorWithElementOrientation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcWall()
        tool.Ifc.link(element, obj)
        obj = subject.create_empty_at_cursor_with_element_orientation(element)
        assert obj.matrix_world == bpy.context.scene.cursor.matrix


class TestDeleteElementObjects(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcWall()
        tool.Ifc.link(element, obj)
        subject.delete_element_objects([element])
        assert not bpy.data.objects.get("Object")


class TestDisableEditingSystem(NewFile):
    def test_run(self):
        bpy.context.scene.BIMSystemProperties.edited_system_id = 10
        subject.disable_editing_system()
        assert bpy.context.scene.BIMSystemProperties.edited_system_id == 0


class TestDisableSystemEditingUI(NewFile):
    def test_run(self):
        subject.enable_system_editing_ui()
        subject.disable_system_editing_ui()
        assert bpy.context.scene.BIMSystemProperties.is_editing is False


class TestEnableSystemEditingUI(NewFile):
    def test_run(self):
        subject.enable_system_editing_ui()
        assert bpy.context.scene.BIMSystemProperties.is_editing is True


class TestExportSystemAttributes(NewFile):
    def test_run(self):
        TestImportSystemAttributes().test_importing_a_system()
        assert subject.export_system_attributes() == {
            "GlobalId": "GlobalId",
            "Name": "Name",
            "Description": "Description",
            "ObjectType": "ObjectType",
        }


class TestGetConnectedPort(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        port1 = ifcopenshell.api.run("system.add_port", ifc)
        port2 = ifcopenshell.api.run("system.add_port", ifc)
        ifcopenshell.api.run("system.connect_port", ifc, port1=port1, port2=port2)
        assert subject.get_connected_port(port1) == port2
        assert subject.get_connected_port(port2) == port1


class TestGetPorts(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        element = ifc.createIfcDuctSegment()
        port = ifc.createIfcDistributionPort()
        ifcopenshell.api.run("system.assign_port", ifc, element=element, port=port)
        subject.get_ports(element) == [port]


class TestImportSystemAttributes(NewFile):
    def test_importing_a_system(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcSystem()
        system.GlobalId = "GlobalId"
        system.Name = "Name"
        system.Description = "Description"
        system.ObjectType = "ObjectType"
        subject().import_system_attributes(system)
        props = bpy.context.scene.BIMSystemProperties
        assert props.system_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.system_attributes.get("Name").string_value == "Name"
        assert props.system_attributes.get("Description").string_value == "Description"
        assert props.system_attributes.get("ObjectType").string_value == "ObjectType"

    def test_importing_a_building_system(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcBuildingSystem()
        system.GlobalId = "GlobalId"
        system.Name = "Name"
        system.Description = "Description"
        system.ObjectType = "ObjectType"
        system.PredefinedType = "SHADING"
        system.LongName = "LongName"
        subject().import_system_attributes(system)
        props = bpy.context.scene.BIMSystemProperties
        assert props.system_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.system_attributes.get("Name").string_value == "Name"
        assert props.system_attributes.get("Description").string_value == "Description"
        assert props.system_attributes.get("ObjectType").string_value == "ObjectType"
        assert props.system_attributes.get("PredefinedType").enum_value == "SHADING"
        assert props.system_attributes.get("LongName").string_value == "LongName"

    def test_importing_a_distribution_system(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcDistributionSystem()
        system.GlobalId = "GlobalId"
        system.Name = "Name"
        system.Description = "Description"
        system.ObjectType = "ObjectType"
        system.PredefinedType = "ELECTRICAL"
        system.LongName = "LongName"
        subject().import_system_attributes(system)
        props = bpy.context.scene.BIMSystemProperties
        assert props.system_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.system_attributes.get("Name").string_value == "Name"
        assert props.system_attributes.get("Description").string_value == "Description"
        assert props.system_attributes.get("ObjectType").string_value == "ObjectType"
        assert props.system_attributes.get("PredefinedType").enum_value == "ELECTRICAL"
        assert props.system_attributes.get("LongName").string_value == "LongName"


class TestImportSystems(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcDistributionSystem()
        zone = ifc.createIfcZone()
        subject.import_systems()
        props = bpy.context.scene.BIMSystemProperties
        assert len(props.systems) == 2
        assert props.systems[0].ifc_definition_id == system.id()
        assert props.systems[0].name == "Unnamed"
        assert props.systems[0].ifc_class == "IfcDistributionSystem"


class TestLoadPorts(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        element = ifc.create_entity("IfcChiller")
        obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, obj)

        port = ifc.create_entity("IfcDistributionPort")
        subject.load_ports(element, [port])
        obj = tool.Ifc.get_object(port)
        assert obj
        assert obj.users_collection
        assert list(obj.location) == [0, 0, 0]


class TestRunGeometryEditObjectPlacement(NewFile):
    def test_nothing(self):
        pass


class TestRunRootAssignClass(NewFile):
    def test_nothing(self):
        pass


class TestSelectSystemProducts(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcPump")
        system = ifcopenshell.api.run("system.add_system", ifc, ifc_class="IfcSystem")
        ifcopenshell.api.run("system.assign_system", ifc, products=[element], system=system)
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(element, obj)
        subject.select_system_products(system)
        assert obj in bpy.context.selected_objects


class TestSetActiveSystem(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifcopenshell.api.run("system.add_system", ifc, ifc_class="IfcSystem")
        subject.set_active_edited_system(system)
        assert bpy.context.scene.BIMSystemProperties.edited_system_id == system.id()


class TestFlowElementAndControls(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        flow_element = ifc.createIfcFlowSegment()
        flow_control = ifc.createIfcController()
        flow_control1 = ifc.createIfcController()

        assert len(subject.get_flow_element_controls(flow_element)) == 0
        assert subject.get_flow_control_flow_element(flow_control) == None

        ifcopenshell.api.run(
            "system.assign_flow_control",
            ifc,
            related_flow_control=flow_control,
            relating_flow_element=flow_element,
        )
        ifcopenshell.api.run(
            "system.assign_flow_control",
            ifc,
            related_flow_control=flow_control1,
            relating_flow_element=flow_element,
        )
        controls = subject.get_flow_element_controls(flow_element)
        assert set(controls) == set((flow_control, flow_control1))
        assert subject.get_flow_control_flow_element(flow_control) == flow_element
