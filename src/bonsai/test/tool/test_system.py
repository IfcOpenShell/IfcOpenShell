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

from math import pi

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.root
import ifcopenshell.api.system
import ifcopenshell.util.representation
import ifcopenshell.util.system
import ifcopenshell.util.unit
import numpy as np
from mathutils import Euler, Matrix, Vector

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.system import System as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.System)


class TestHasParametricBody(NewFile):
    """The MEP-action gizmo predicates gate on ``has_parametric_body``;
    fittings whose swept body lives on the type via ``IfcMappedItem`` must
    return True so the pen-icon and lock-icon rows show on the occurrence."""

    def _build_bend_occurrence_with_mapped_body(self):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        body_ctx = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")

        placement = ifc_file.create_entity(
            "IfcAxis2Placement3D",
            Location=ifc_file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        )
        line = ifc_file.create_entity(
            "IfcLine",
            Pnt=ifc_file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            Dir=ifc_file.create_entity(
                "IfcVector",
                Orientation=ifc_file.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
                Magnitude=1.0,
            ),
        )
        trimmed = ifc_file.create_entity(
            "IfcTrimmedCurve",
            BasisCurve=line,
            Trim1=(ifc_file.create_entity("IfcParameterValue", wrappedValue=0.0),),
            Trim2=(ifc_file.create_entity("IfcParameterValue", wrappedValue=1.0),),
            SenseAgreement=True,
            MasterRepresentation="PARAMETER",
        )
        swept = ifc_file.create_entity("IfcSweptDiskSolid", Directrix=trimmed, Radius=0.05)
        type_body = ifc_file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_ctx,
            RepresentationIdentifier="Body",
            RepresentationType="AdvancedSweptSolid",
            Items=(swept,),
        )
        rep_map = ifc_file.create_entity(
            "IfcRepresentationMap", MappingOrigin=placement, MappedRepresentation=type_body
        )
        fitting_type = ifc_file.create_entity(
            "IfcPipeFittingType",
            GlobalId=ifcopenshell.guid.new(),
            Name="BendType",
            PredefinedType="BEND",
            RepresentationMaps=(rep_map,),
        )
        mapped_item = ifc_file.create_entity(
            "IfcMappedItem",
            MappingSource=rep_map,
            MappingTarget=ifc_file.create_entity(
                "IfcCartesianTransformationOperator3D",
                LocalOrigin=ifc_file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            ),
        )
        occurrence_body = ifc_file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_ctx,
            RepresentationIdentifier="Body",
            RepresentationType="MappedRepresentation",
            Items=(mapped_item,),
        )
        fitting = ifc_file.create_entity(
            "IfcPipeFitting",
            GlobalId=ifcopenshell.guid.new(),
            Name="Bend",
            PredefinedType="BEND",
            Representation=ifc_file.create_entity("IfcProductDefinitionShape", Representations=(occurrence_body,)),
        )
        ifc_file.create_entity(
            "IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=(fitting,),
            RelatingType=fitting_type,
        )
        return fitting

    def test_returns_true_for_swept_disk_via_mapped_item(self):
        """``traverse()`` follows the
        ``IfcMappedItem.MappingSource.MappedRepresentation`` chain so the
        ``IfcSweptDiskSolid`` on the type's body is reachable from the
        occurrence's body representation. Bend fittings produced by the
        bend-preview commit path use this exact representation shape."""
        fitting = self._build_bend_occurrence_with_mapped_body()
        assert subject.has_parametric_body(fitting) is True

    def test_returns_false_for_tessellated_body(self):
        """The bend creation path replaces the swept-disk body with an
        ``IfcTriangulatedFaceSet`` as an upstream geometry-kernel
        workaround. The traverse finds no extruded / swept solid, so the
        predicate returns False — pinning the constraint that drives the
        ``BBIM_Fitting`` pset fallback in the bend-icon visibility
        predicate."""
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        body_ctx = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")

        coords = ifc_file.create_entity(
            "IfcCartesianPointList3D",
            CoordList=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        )
        tessellation = ifc_file.create_entity(
            "IfcTriangulatedFaceSet",
            Coordinates=coords,
            CoordIndex=((1, 2, 3),),
        )
        body = ifc_file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_ctx,
            RepresentationIdentifier="Body",
            RepresentationType="Tessellation",
            Items=(tessellation,),
        )
        fitting = ifc_file.create_entity(
            "IfcPipeFitting",
            GlobalId=ifcopenshell.guid.new(),
            Name="TessellatedBend",
            PredefinedType="BEND",
            Representation=ifc_file.create_entity("IfcProductDefinitionShape", Representations=(body,)),
        )

        assert subject.has_parametric_body(fitting) is False


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
        assert isinstance(obj.data, bpy.types.Mesh)
        for v in obj.data.vertices:
            v.co += Vector((0, 0, 2.5))
        return obj, element

    def check_ports_matrices(self, ports, expected_matrices):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port, expected_matrix in zip(ports, expected_matrices, strict=True):
            port_matrix = tool.Model.get_element_matrix(port)
            port_matrix.translation *= si_conversion
            assert np.allclose(
                port_matrix, expected_matrix, atol=1.0e-5
            ), f"Matrix does not match:\n{port_matrix}\n{expected_matrix}"

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
        assert bpy.context.scene
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcWall()
        tool.Ifc.link(element, obj)
        obj = subject.create_empty_at_cursor_with_element_orientation(element)
        assert obj.matrix_world == bpy.context.scene.cursor.matrix


class TestCreatePortAtCursor(NewFile):
    def test_run(self):
        assert bpy.context.scene
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifcopenshell.api.system.add_system(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcDuctSegment")
        ifcopenshell.api.system.assign_system(ifc, products=[element], system=system)
        obj = tool.Ifc.link(element, bpy.data.objects.new("Object", None))
        port = subject.create_port_at_cursor(element)
        assert port.is_a("IfcDistributionPort")
        assert ifcopenshell.util.system.get_ports(element) == [port]


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
        props = tool.System.get_system_props()
        props.edited_system_id = 10
        subject.disable_editing_system()
        assert props.edited_system_id == 0


class TestDisableSystemEditingUI(NewFile):
    def test_run(self):
        subject.enable_system_editing_ui()
        subject.disable_system_editing_ui()
        props = tool.System.get_system_props()
        assert props.is_editing is False


class TestEnableSystemEditingUI(NewFile):
    def test_run(self):
        subject.enable_system_editing_ui()
        props = tool.System.get_system_props()
        assert props.is_editing is True


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
        port1 = ifcopenshell.api.system.add_port(ifc)
        port2 = ifcopenshell.api.system.add_port(ifc)
        ifcopenshell.api.system.connect_port(ifc, port1=port1, port2=port2)
        assert subject.get_connected_port(port1) == port2
        assert subject.get_connected_port(port2) == port1


class TestGetPorts(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        element = ifc.createIfcDuctSegment()
        port = ifc.createIfcDistributionPort()
        ifcopenshell.api.system.assign_port(ifc, element=element, port=port)
        assert subject.get_ports(element) == [port]


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
        props = tool.System.get_system_props()
        assert props.system_attributes["GlobalId"].string_value == "GlobalId"
        assert props.system_attributes["Name"].string_value == "Name"
        assert props.system_attributes["Description"].string_value == "Description"
        assert props.system_attributes["ObjectType"].string_value == "ObjectType"

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
        props = tool.System.get_system_props()
        assert props.system_attributes["GlobalId"].string_value == "GlobalId"
        assert props.system_attributes["Name"].string_value == "Name"
        assert props.system_attributes["Description"].string_value == "Description"
        assert props.system_attributes["ObjectType"].string_value == "ObjectType"
        assert props.system_attributes["PredefinedType"].enum_value == "SHADING"
        assert props.system_attributes["LongName"].string_value == "LongName"

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
        props = tool.System.get_system_props()
        assert props.system_attributes["GlobalId"].string_value == "GlobalId"
        assert props.system_attributes["Name"].string_value == "Name"
        assert props.system_attributes["Description"].string_value == "Description"
        assert props.system_attributes["ObjectType"].string_value == "ObjectType"
        assert props.system_attributes["PredefinedType"].enum_value == "ELECTRICAL"
        assert props.system_attributes["LongName"].string_value == "LongName"


class TestImportSystems(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcDistributionSystem()
        zone = ifc.createIfcZone()
        subject.import_systems()
        props = tool.System.get_system_props()
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
        assert isinstance(obj, bpy.types.Object)
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
        assert bpy.context.scene
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcPump")
        system = ifcopenshell.api.system.add_system(ifc, ifc_class="IfcSystem")
        ifcopenshell.api.system.assign_system(ifc, products=[element], system=system)
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(element, obj)
        subject.select_system_products(system)
        assert obj in bpy.context.selected_objects


class TestSetActiveSystem(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifcopenshell.api.system.add_system(ifc, ifc_class="IfcSystem")
        subject.set_active_edited_system(system)
        props = tool.System.get_system_props()
        assert props.edited_system_id == system.id()


class TestFlowElementAndControls(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        flow_element = ifc.createIfcFlowSegment()
        flow_control = ifc.createIfcController()
        flow_control1 = ifc.createIfcController()

        assert len(subject.get_flow_element_controls(flow_element)) == 0
        assert subject.get_flow_control_flow_element(flow_control) == None

        ifcopenshell.api.system.assign_flow_control(
            ifc,
            related_flow_control=flow_control,
            relating_flow_element=flow_element,
        )
        ifcopenshell.api.system.assign_flow_control(
            ifc,
            related_flow_control=flow_control1,
            relating_flow_element=flow_element,
        )
        controls = subject.get_flow_element_controls(flow_element)
        assert set(controls) == set((flow_control, flow_control1))
        assert subject.get_flow_control_flow_element(flow_control) == flow_element
