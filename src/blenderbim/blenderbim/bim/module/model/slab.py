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

import os
import gpu
import blf
import bgl
import bpy
import bmesh
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import ifcopenshell.util.element
import mathutils.geometry
import blenderbim.bim.handler
import blenderbim.core.type
import blenderbim.core.geometry
import blenderbim.tool as tool
from bpy.types import SpaceView3D
from blenderbim.bim.ifc import IfcStore
from math import pi, degrees, sin, cos, radians
from mathutils import Vector, Matrix
from ifcopenshell.api.pset.data import Data as PsetData
from ifcopenshell.api.material.data import Data as MaterialData
from blenderbim.bim.module.geometry.helper import Helper
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader


def generate_footprint(usecase_path, ifc_file, settings):
    footprint_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "FootPrint", "SKETCH_VIEW")
    if not footprint_context:
        return
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbLayer3":
        return
    old_footprint = ifcopenshell.util.representation.get_representation(product, "Plan", "FootPrint", "SKETCH_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_footprint:
            blenderbim.core.geometry.remove_representation(
                tool.Ifc, tool.Geometry, obj=obj, representation=old_footprint
            )

        helper = Helper(ifc_file)
        indices = helper.auto_detect_arbitrary_profile_with_voids_extruded_area_solid(settings["geometry"])

        bm = bmesh.new()
        bm.from_mesh(settings["geometry"])
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        profile_edges = []

        def append_profile_edges(profile_edges, indices):
            indices.append(indices[0])  # Close the loop
            edge_vert_pairs = list(zip(indices, indices[1:]))
            for p in edge_vert_pairs:
                profile_edges.append(
                    [e for e in bm.verts[p[0]].link_edges if e.other_vert(bm.verts[p[0]]).index == p[1]][0]
                )

        append_profile_edges(profile_edges, indices["profile"])
        for inner_indices in indices["inner_curves"]:
            append_profile_edges(profile_edges, inner_indices)

        irrelevant_edges = [e for e in bm.edges if e not in profile_edges]
        bmesh.ops.delete(bm, geom=irrelevant_edges, context="EDGES")
        mesh = bpy.data.meshes.new("Temporary Footprint")
        bm.to_mesh(mesh)
        bm.free()

        new_settings = settings.copy()
        new_settings["context"] = footprint_context
        new_settings["geometry"] = mesh
        new_footprint = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )

        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_footprint}
        )
        bpy.data.meshes.remove(mesh)


def calculate_quantities(usecase_path, ifc_file, settings):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or "Engine" not in parametric or parametric["Engine"] != "BlenderBIM.DumbLayer3":
        return
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=product, name="Qto_SlabBaseQuantities"
    )
    length = obj.dimensions[0] / unit_scale
    width = obj.dimensions[1] / unit_scale
    depth = obj.dimensions[2] / unit_scale

    perimeter = 0
    helper = Helper(ifc_file)
    indices = helper.auto_detect_arbitrary_profile_with_voids_extruded_area_solid(settings["geometry"])

    bm = bmesh.new()
    bm.from_mesh(settings["geometry"])
    bm.verts.ensure_lookup_table()

    def calculate_profile_length(indices):
        indices.append(indices[0])  # Close the loop
        edge_vert_pairs = list(zip(indices, indices[1:]))
        return sum([(bm.verts[p[1]].co - bm.verts[p[0]].co).length for p in edge_vert_pairs])

    perimeter += calculate_profile_length(indices["profile"])
    for inner_indices in indices["inner_curves"]:
        perimeter += calculate_profile_length(inner_indices)

    bm.free()

    if product.HasOpenings:
        # TODO: calculate gross / net
        gross_area = 0
        net_area = 0
        gross_volume = 0
        net_volume = 0
    else:
        bm = bmesh.new()
        bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
        bm.faces.ensure_lookup_table()
        gross_area = sum([f.calc_area() for f in bm.faces if f.normal.z > 0.9])
        net_area = gross_area
        gross_volume = bm.calc_volume()
        net_volume = gross_volume
        bm.free()

    properties = {
        "Depth": round(depth, 2),
        "Perimeter": round(perimeter, 2),
        "GrossArea": round(gross_area, 2),
        "NetArea": round(net_area, 2),
        "GrossVolume": round(gross_volume, 2),
        "NetVolume": round(net_volume, 2),
    }

    if round(obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2], 2) == round(gross_volume, 2):
        properties.update(
            {
                "Length": round(length, 2),
                "Width": round(width, 2),
            }
        )
    else:
        properties.update(
            {
                "Length": None,
                "Width": None,
            }
        )

    ifcopenshell.api.run("pset.edit_qto", ifc_file, should_run_listeners=False, qto=qto, properties=properties)
    PsetData.load(ifc_file, obj.BIMObjectProperties.ifc_definition_id)


class DumbSlabGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        self.file = IfcStore.get_file()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        thicknesses = []
        for rel in self.relating_type.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                material = rel.RelatingMaterial
                if material.is_a("IfcMaterialLayerSet"):
                    thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                    break
        if not sum(thicknesses):
            return

        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.depth = sum(thicknesses) * unit_scale
        self.width = 3
        self.length = 3
        self.rotation = 0
        self.location = Vector((0, 0, 0))
        return self.derive_from_cursor()

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        return self.create_slab()

    def create_slab(self):
        verts = [
            Vector((0, 0, 0)),
            Vector((0, self.width, 0)),
            Vector((self.length, self.width, 0)),
            Vector((self.length, 0, 0)),
        ]
        edges = []
        faces = [[0, 3, 2, 1]]

        ifc_classes = ifcopenshell.util.type.get_applicable_entities(self.relating_type.is_a(), self.file.schema)
        # Standard cases are deprecated, so let's cull them
        ifc_class = [c for c in ifc_classes if "StandardCase" not in c][0]

        mesh = bpy.data.meshes.new(name="Dumb Slab")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)
        modifier = obj.modifiers.new("Slab Depth", "SOLIDIFY")
        modifier.use_even_offset = True
        modifier.offset = 1
        modifier.thickness = self.depth

        obj.location = self.location
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2] - self.depth
        else:
            obj.location[2] -= self.depth
        self.collection.objects.link(obj)
        bpy.ops.bim.assign_class(
            obj=obj.name,
            ifc_class=ifc_class,
            ifc_representation_class="IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids",
        )
        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=tool.Ifc.get_entity(obj), type=self.relating_type)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbLayer3"})
        MaterialData.load(self.file)
        try:
            obj.select_set(True)
        except RuntimeError:

            def msg(self, context):
                txt = "The created object could not be assigned to a collection. "
                txt += "Has any IfcSpatialElement been deleted?"
                self.layout.label(text=txt)

            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
        return obj


class DumbSlabPlaner:
    def regenerate_from_layer(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        layer = settings["layer"]
        thickness = settings["attributes"].get("LayerThickness")
        if thickness is None:
            return
        for layer_set in layer.ToMaterialLayerSet:
            total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers])
            if not total_thickness:
                continue
            for inverse in ifc_file.get_inverse(layer_set):
                if not inverse.is_a("IfcMaterialLayerSetUsage") or inverse.LayerSetDirection != "AXIS3":
                    continue
                if ifc_file.schema == "IFC2X3":
                    for rel in ifc_file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return
        new_thickness = sum([l.LayerThickness for l in new_material.MaterialLayers])
        material = ifcopenshell.util.element.get_material(settings["related_object"])

        relating_type = settings["relating_type"]
        if hasattr(relating_type, "HasPropertySets"):
            psets = relating_type.HasPropertySets
            if psets is not None:
                for pset in psets:
                    if hasattr(pset, "HasProperties"):
                        pset_props = pset.HasProperties
                        if pset_props is not None:
                            for prop in pset_props:
                                if prop.Name == "LayerSetDirection":
                                    if hasattr(prop, "NominalValue"):
                                        nominal_value = prop.NominalValue
                                        if hasattr(nominal_value, "wrappedValue"):
                                            if nominal_value.wrappedValue == "AXIS2":
                                                return

        if material and material.is_a("IfcMaterialLayerSetUsage") and material.LayerSetDirection == "AXIS3":
            self.change_thickness(settings["related_object"], new_thickness)

    def change_thickness(self, element, thickness):
        obj = IfcStore.get_element(element.id())
        if not obj:
            return

        delta_thickness = (thickness * self.unit_scale) - obj.dimensions.z
        if round(delta_thickness, 2) == 0:
            return

        modifier = ensure_solidify_modifier(obj)
        modifier.thickness += delta_thickness
        obj.location[2] -= delta_thickness


class EnableEditingSketchExtrusionProfile(bpy.types.Operator):
    bl_idname = "bim.xxx"
    bl_label = "Enable Editing Sketch Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = self.get_extrusion(body)
        profile = extrusion.SweptArea
        position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())

        z_values = [v[2] for v in obj.bound_box]

        element = tool.Ifc.get_entity(obj)
        entities = context.scene.sketcher.entities
        entities.ensure_origin_elements(context)

        origin = entities.add_point_3d(obj.matrix_world @ Vector((0, 0, max(z_values))))
        origin.fixed = True
        origin.origin = True
        normal = entities.add_normal_3d(obj.matrix_world.to_quaternion())
        normal.fixed = True
        normal.origin = True

        wp = entities.add_workplane(origin, normal)
        sketch = entities.add_sketch(wp)

        points = []
        total_points = len(profile.OuterCurve.Points)
        last_index = len(profile.OuterCurve.Points) - 1
        for i, point in enumerate(profile.OuterCurve.Points):
            if i == last_index:
                continue
            global_point = (position @ Vector(point.Coordinates).to_3d()).to_2d()
            p = context.scene.sketcher.entities.add_point_2d(global_point, sketch)
            if i != 0:
                context.scene.sketcher.entities.add_line_2d(points[-1], p, sketch)
            points.append(p)
        context.scene.sketcher.entities.add_line_2d(points[-1], points[0], sketch)

        bpy.ops.view3d.slvs_set_active_sketch(index=sketch.slvs_index)
        return {"FINISHED"}

    def get_extrusion(self, representation):
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanClippingResult"):
                item = item.FirstOperand
            else:
                break


class EditSketchExtrusionProfile(bpy.types.Operator):
    bl_idname = "bim.xxe"
    bl_label = "Edit Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = self.get_extrusion(representation)
        position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
        position_i = position.inverted()

        cad_sketcher = __import__("CAD_Sketcher-main")
        sketch = context.scene.sketcher.active_sketch
        converter = cad_sketcher.convertors.BezierConverter(context.scene, sketch)
        converter.run()

        profile = tool.Ifc.get().createIfcArbitraryClosedProfileDef("AREA")
        for path in converter.paths:
            points = []
            lines = path[0]
            last_index = len(lines) - 1
            for i, line in enumerate(lines):
                local_point = (position_i @ Vector(line.p1.co).to_3d()).to_2d()
                points.append(tool.Ifc.get().createIfcCartesianPoint(local_point))
            points.append(points[0])
            curve = tool.Ifc.get().createIfcPolyline(points)
        profile.OuterCurve = curve

        extrusion.SweptArea = profile

        bpy.foo = converter.paths

        bpy.ops.view3d.slvs_set_active_sketch(index=-1)
        workplane = sketch.wp
        p1 = workplane.p1
        p1.origin = False
        nm = workplane.nm
        nm.origin = False
        bpy.ops.view3d.slvs_delete_entity(index=sketch["slvs_index"])
        bpy.ops.view3d.slvs_delete_entity(index=workplane["slvs_index"])
        bpy.ops.view3d.slvs_delete_entity(index=p1["slvs_index"])
        bpy.ops.view3d.slvs_delete_entity(index=nm["slvs_index"])

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )
        return {"FINISHED"}

    def get_extrusion(self, representation):
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanClippingResult"):
                item = item.FirstOperand
            else:
                break


class DisableEditingExtrusionProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_extrusion_profile"
    bl_label = "Disable Editing Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        DecorationsHandler.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")

        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=body,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )
        return {"FINISHED"}


class EnableEditingExtrusionProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_extrusion_profile"
    bl_label = "Enable Editing Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = self.get_extrusion(body)
        position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
        position[0][3] *= self.unit_scale
        position[1][3] *= self.unit_scale
        position[2][3] *= self.unit_scale

        z_values = [v[2] for v in obj.bound_box]
        origin = obj.matrix_world @ Vector((0, 0, max(z_values)))
        normal = obj.matrix_world.to_quaternion()

        self.vertices = []
        self.edges = []
        self.arcs = []
        self.circles = []

        profile = extrusion.SweptArea
        if profile.is_a("IfcArbitraryClosedProfileDef"):
            self.process_curve(obj, position, profile.OuterCurve)
            if profile.is_a("IfcArbitraryProfileDefWithVoids"):
                for inner_curve in profile.InnerCurves:
                    self.process_curve(obj, position, inner_curve)

        mesh = bpy.data.meshes.new("Profile")
        mesh.from_pydata(self.vertices, self.edges, [])
        mesh.BIMMeshProperties.is_profile = True
        obj.data = mesh

        for arc in self.arcs:
            group = obj.vertex_groups.new(name="IFCARCINDEX")
            group.add(arc, 1, "REPLACE")

        for circle in self.circles:
            group = obj.vertex_groups.new(name="IFCCIRCLE")
            group.add(circle, 1, "REPLACE")

        bpy.ops.object.mode_set(mode="EDIT")
        DecorationsHandler.install(context)
        bpy.ops.wm.tool_set_by_id(name="bim.cad_tool")
        return {"FINISHED"}

    def get_extrusion(self, representation):
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanClippingResult"):
                item = item.FirstOperand
            else:
                break

    def process_curve(self, obj, position, curve):
        offset = len(self.vertices)

        if curve.is_a("IfcPolyline"):
            total_points = len(curve.Points)
            last_index = len(curve.Points) - 1
            for i, point in enumerate(curve.Points):
                if i == last_index:
                    continue
                global_point = position @ Vector(self.convert_unit_to_si(point.Coordinates)).to_3d()
                self.vertices.append(global_point)
            self.edges.extend([(i, i + 1) for i in range(offset, len(self.vertices))])
            self.edges[-1] = (len(self.vertices) - 1, offset) # Close the loop
        elif curve.is_a("IfcIndexedPolyCurve"):
            is_arc = False
            if curve.Segments:
                for segment in curve.Segments:
                    if len(segment[0]) == 3:  # IfcArcIndex
                        is_arc = True
                        local_point = self.convert_unit_to_si(curve.Points.CoordList[segment[0][0] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        self.vertices.append(global_point)
                        local_point = self.convert_unit_to_si(curve.Points.CoordList[segment[0][1] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        self.vertices.append(global_point)
                        self.arcs.append([len(self.vertices) - 2, len(self.vertices) - 1])
                    else:
                        local_point = self.convert_unit_to_si(curve.Points.CoordList[segment[0][0] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        self.vertices.append(global_point)
                        if is_arc:
                            self.arcs[-1].append(len(self.vertices) - 1)
                            is_arc = False
            else:
                for local_point in curve.PointsCoordList:
                    global_point = position @ Vector(self.convert_unit_to_si(local_point)).to_3d()
                    self.vertices.append(global_point)

            self.edges.extend([(i, i + 1) for i in range(offset, len(self.vertices))])
            self.edges[-1] = (len(self.vertices) - 1, offset) # Close the loop
        elif curve.is_a("IfcCircle"):
            center = self.convert_unit_to_si(
                Matrix(ifcopenshell.util.placement.get_axis2placement(curve.Position).tolist()).col[3].to_3d()
            )
            radius = self.convert_unit_to_si(curve.Radius)
            self.vertices.extend(
                [
                    position @ Vector((center[0], center[1] - curve.Radius, 0.0)),
                    position @ Vector((center[0], center[1] + curve.Radius, 0.0)),
                ]
            )
            self.circles.append([offset, offset + 1])
            self.edges.append((offset, offset + 1))

    def convert_unit_to_si(self, value):
        if isinstance(value, (tuple, list)):
            return [v * self.unit_scale for v in value]
        return value * self.unit_scale


class EditExtrusionProfile(bpy.types.Operator):
    bl_idname = "bim.edit_extrusion_profile"
    bl_label = "Edit Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        DecorationsHandler.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")

        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = self.get_extrusion(representation)
        position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
        position[0][3] *= self.unit_scale
        position[1][3] *= self.unit_scale
        position[2][3] *= self.unit_scale

        helper = Helper(tool.Ifc.get())
        indices = helper.auto_detect_arbitrary_profile_with_voids(obj, obj.data)

        if isinstance(indices, tuple) and indices[0] is False:  # Ugly
            self.report({"ERROR"}, "INVALID PROFILE: " + indices[1])
            DecorationsHandler.install(context)
            bpy.ops.object.mode_set(mode="EDIT")
            return {"CANCELLED"}

        self.bm = bmesh.new()
        self.bm.from_mesh(obj.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()

        if indices["inner_curves"]:
            profile = tool.Ifc.get().createIfcArbitraryProfileDefWithVoids("AREA")
        else:
            profile = tool.Ifc.get().createIfcArbitraryClosedProfileDef("AREA")

        if tool.Ifc.get().schema != "IFC2X3":
            self.points = self.create_points(position, indices["points"])

        profile.OuterCurve = self.create_curve(position, indices["profile"])
        if indices["inner_curves"]:
            results = []
            for inner_curve in indices["inner_curves"]:
                results.append(self.create_curve(position, inner_curve))
            profile.InnerCurves = results

        self.bm.free()

        extrusion.SweptArea = profile

        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )
        return {"FINISHED"}

    def create_points(self, position, indices):
        position_i = position.inverted()
        points = []
        for point in indices:
            local_point = (position_i @ point).to_2d()
            points.append(self.convert_si_to_unit(list(local_point)))
        return tool.Ifc.get().createIfcCartesianPointList2D(points)

    def create_curve(self, position, edge_indices, points=None):
        position_i = position.inverted()
        if len(edge_indices) == 2:
            diameter = edge_indices[0]
            p1 = self.bm.verts[diameter[0]].co
            p2 = self.bm.verts[diameter[1]].co
            center = self.convert_si_to_unit(list(position_i @ p1.lerp(p2, 0.5)))
            radius = self.convert_si_to_unit((p1 - p2).length / 2)
            return tool.Ifc.get().createIfcCircle(
                tool.Ifc.get().createIfcAxis2Placement2D(tool.Ifc.get().createIfcCartesianPoint(center)), radius
            )
        if tool.Ifc.get().schema == "IFC2X3":
            points = []
            for edge in edge_indices:
                local_point = (position_i @ Vector(self.bm.verts[edge[0]].co)).to_2d()
                points.append(tool.Ifc.get().createIfcCartesianPoint(self.convert_si_to_unit(local_point)))
            points.append(points[0])
            return tool.Ifc.get().createIfcPolyline(points)
        segments = []
        for segment in edge_indices:
            if len(segment) == 2:
                segments.append(tool.Ifc.get().createIfcLineIndex([i + 1 for i in segment]))
            elif len(segment) == 3:
                segments.append(tool.Ifc.get().createIfcArcIndex([i + 1 for i in segment]))
        return tool.Ifc.get().createIfcIndexedPolyCurve(self.points, segments, False)

    def get_extrusion(self, representation):
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanClippingResult"):
                item = item.FirstOperand
            else:
                break

    def convert_si_to_unit(self, value):
        if isinstance(value, (tuple, list)):
            return [v / self.unit_scale for v in value]
        return value / self.unit_scale


class SetArcIndex(bpy.types.Operator):
    bl_idname = "bim.set_arc_index"
    bl_label = "Set Arc Index"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def cancel_message(self, msg):
        self.report({"WARNING"}, msg)
        return {"CANCELLED"}

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.mode_set(mode="OBJECT")
        selected_vertices = [v.index for v in obj.data.vertices if v.select]
        in_group = any([bool(obj.data.vertices[v].groups) for v in selected_vertices])
        for group in obj.vertex_groups:
            group.remove(selected_vertices)
        if in_group is False:
            group = obj.vertex_groups.new(name="IFCARCINDEX")
            group.add(selected_vertices, 1, "REPLACE")
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class DecorationsHandler:
    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW")

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def __call__(self, context):
        obj = context.active_object
        if obj.mode != "EDIT":
            return

        bgl.glLineWidth(2)
        bgl.glPointSize(6)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)

        all_vertices = []
        error_vertices = []
        selected_vertices = []
        unselected_vertices = []
        special_vertices = []
        special_vertex_indices = {}
        selected_edges = []
        unselected_edges = []
        special_edges = []

        arc_groups = []
        circle_groups = []
        for i, group in enumerate(obj.vertex_groups):
            if "IFCARCINDEX" in group.name:
                arc_groups.append(i)
            elif "IFCCIRCLE" in group.name:
                circle_groups.append(i)

        arcs = {}
        circles = {}

        bm = bmesh.from_edit_mesh(obj.data)

        # https://docs.blender.org/api/blender_python_api_2_63_8/bmesh.html#CustomDataAccess
        # This is how we access vertex groups via bmesh, apparently, it's not very intuitive
        deform_layer = bm.verts.layers.deform.active

        for vertex in bm.verts:
            co = tuple(obj.matrix_world @ vertex.co)
            all_vertices.append(co)
            if vertex.hide:
                continue

            is_arc = False
            for group_index in arc_groups:
                if group_index in vertex[deform_layer]:
                    is_arc = True
                    break
            if is_arc:
                arcs.setdefault(group_index, []).append(vertex)
                special_vertex_indices[vertex.index] = group_index

            is_circle = False
            for group_index in circle_groups:
                if group_index in vertex[deform_layer]:
                    is_circle = True
                    break
            if is_circle:
                circles.setdefault(group_index, []).append(vertex)
                special_vertex_indices[vertex.index] = group_index

            if vertex.select:
                selected_vertices.append(co)
            else:
                if len(vertex.link_edges) != 2:
                    error_vertices.append(co)
                elif is_arc:
                    special_vertices.append(co)
                else:
                    unselected_vertices.append(co)

        for edge in bm.edges:
            edge_indices = [v.index for v in edge.verts]
            if edge.hide:
                continue
            if edge.select:
                selected_edges.append(edge_indices)
            else:
                i1, i2 = edge.verts[0].index, edge.verts[1].index
                if i1 in special_vertex_indices and special_vertex_indices[i1] == special_vertex_indices.get(i2, None):
                    special_edges.append(edge_indices)
                else:
                    unselected_edges.append(edge_indices)
        indices = [[v.index for v in e.verts] for e in bm.edges]

        white = (1, 1, 1, 1)
        green = (0.545, 0.863, 0, 1)
        red = (1, 0.2, 0.322, 1)
        blue = (0.157, 0.565, 1, 1)
        grey = (0.2, 0.2, 0.2, 1)

        self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")

        batch = batch_for_shader(self.shader, "LINES", {"pos": all_vertices}, indices=unselected_edges)
        self.shader.bind()
        self.shader.uniform_float("color", white)
        batch.draw(self.shader)

        batch = batch_for_shader(self.shader, "LINES", {"pos": all_vertices}, indices=selected_edges)
        self.shader.uniform_float("color", green)
        batch.draw(self.shader)

        batch = batch_for_shader(self.shader, "LINES", {"pos": all_vertices}, indices=special_edges)
        self.shader.uniform_float("color", grey)
        batch.draw(self.shader)

        batch = batch_for_shader(self.shader, "POINTS", {"pos": unselected_vertices})
        self.shader.uniform_float("color", white)
        batch.draw(self.shader)

        batch = batch_for_shader(self.shader, "POINTS", {"pos": error_vertices})
        self.shader.uniform_float("color", red)
        batch.draw(self.shader)

        batch = batch_for_shader(self.shader, "POINTS", {"pos": special_vertices})
        self.shader.uniform_float("color", blue)
        batch.draw(self.shader)

        batch = batch_for_shader(self.shader, "POINTS", {"pos": selected_vertices})
        self.shader.uniform_float("color", green)
        batch.draw(self.shader)

        # Draw arcs

        arc_centroids = []
        arc_segments = []
        for arc in arcs.values():
            if len(arc) != 3:
                continue
            sorted_arc = [None, None, None]
            for v1 in arc:
                connections = 0
                for link_edge in v1.link_edges:
                    v2 = link_edge.other_vert(v1)
                    if v2 in arc:
                        connections += 1
                if connections == 2:  # Midpoint
                    sorted_arc[1] = v1
                else:
                    sorted_arc[2 if sorted_arc[2] is None else 0] = v1
            points = [tuple(obj.matrix_world @ v.co) for v in sorted_arc]
            centroid = tool.Cad.get_center_of_arc(points)
            if centroid:
                arc_centroids.append(tuple(centroid))
            arc_segments.append(tool.Cad.create_arc_segments(pts=points, num_verts=17, make_edges=True))

        batch = batch_for_shader(self.shader, "POINTS", {"pos": arc_centroids})
        self.shader.uniform_float("color", (0.2, 0.2, 0.2, 1))
        batch.draw(self.shader)

        for verts, edges in arc_segments:
            batch = batch_for_shader(self.shader, "LINES", {"pos": verts}, indices=edges)
            self.shader.uniform_float("color", (0.157, 0.565, 1, 1))
            batch.draw(self.shader)

        # Draw circles

        circle_centroids = []
        circle_segments = []
        for circle in circles.values():
            if len(circle) != 2:
                continue
            p1 = obj.matrix_world @ circle[0].co
            p2 = obj.matrix_world @ circle[1].co
            radius = (p2 - p1).length / 2
            centroid = p1.lerp(p2, 0.5)
            circle_centroids.append(tuple(centroid))
            segments = self.create_circle_segments(360, 20, radius)
            matrix = obj.matrix_world.copy()
            matrix.col[3] = centroid.to_4d()
            segments = [[list(matrix @ Vector(v)) for v in segments[0]], segments[1]]
            circle_segments.append(segments)

        batch = batch_for_shader(self.shader, "POINTS", {"pos": circle_centroids})
        self.shader.uniform_float("color", (0.2, 0.2, 0.2, 1))
        batch.draw(self.shader)

        for verts, edges in circle_segments:
            batch = batch_for_shader(self.shader, "LINES", {"pos": verts}, indices=edges)
            self.shader.uniform_float("color", (0.157, 0.565, 1, 1))
            batch.draw(self.shader)

    def create_matrix(self, p, x, y, z):
        return Matrix([x, y, z, p]).to_4x4().transposed()

    # https://github.com/nortikin/sverchok/blob/master/nodes/generator/basic_3pt_arc.py
    # This function is taken from Sverchok, licensed under GPL v2-or-later.
    # This is a combination of the make_verts and make_edges function.
    def create_circle_segments(self, Angle, Vertices, Radius):
        if Angle < 360:
            theta = Angle / (Vertices - 1)
        else:
            theta = Angle / Vertices
        listVertX = []
        listVertY = []
        for i in range(Vertices):
            listVertX.append(Radius * cos(radians(theta * i)))
            listVertY.append(Radius * sin(radians(theta * i)))

        if Angle < 360 and self.mode_ == 0:
            sigma = radians(Angle)
            listVertX[-1] = Radius * cos(sigma)
            listVertY[-1] = Radius * sin(sigma)
        elif Angle < 360 and self.mode_ == 1:
            listVertX.append(0.0)
            listVertY.append(0.0)

        points = list((x, y, 0) for x, y in zip(listVertX, listVertY))

        listEdg = [(i, i + 1) for i in range(Vertices - 1)]

        if Angle < 360 and self.mode_ == 1:
            listEdg.append((0, Vertices))
            listEdg.append((Vertices - 1, Vertices))
        else:
            listEdg.append((Vertices - 1, 0))

        return points, listEdg
