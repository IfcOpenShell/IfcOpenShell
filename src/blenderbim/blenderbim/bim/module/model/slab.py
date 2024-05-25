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
import json
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import ifcopenshell.util.type
import blenderbim.bim.handler
import blenderbim.core.type
import blenderbim.core.geometry
import blenderbim.core.root
import blenderbim.tool as tool
from math import radians
from mathutils import Vector, Matrix
from blenderbim.bim.module.geometry.helper import Helper
from blenderbim.bim.module.model.decorator import ProfileDecorator
from typing import Optional


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


class DumbSlabGenerator:
    def __init__(self, relating_type: ifcopenshell.entity_instance):
        self.relating_type = relating_type

    def generate(self):
        self.file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        thicknesses = []
        for rel in self.relating_type.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                material = rel.RelatingMaterial
                if material.is_a("IfcMaterialLayerSet"):
                    thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                    break
        if not sum(thicknesses):
            return

        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.footprint_context = ifcopenshell.util.representation.get_context(
            tool.Ifc.get(), "Plan", "FootPrint", "SKETCH_VIEW"
        )

        props = bpy.context.scene.BIMModelProperties
        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = self.collection.BIMCollectionProperties.obj
        self.depth = sum(thicknesses) * unit_scale
        self.width = 3
        self.length = 3
        self.rotation = 0
        self.location = Vector((0, 0, 0))
        self.x_angle = 0 if tool.Cad.is_x(props.x_angle, 0, tolerance=0.001) else props.x_angle
        return self.derive_from_cursor()

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        return self.create_slab()

    def create_slab(self):
        ifc_classes = ifcopenshell.util.type.get_applicable_entities(self.relating_type.is_a(), self.file.schema)
        # Standard cases are deprecated, so let's cull them
        ifc_class = [c for c in ifc_classes if "StandardCase" not in c][0]

        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)

        matrix_world = Matrix()
        matrix_world.translation = self.location
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            matrix_world.translation.z = self.collection_obj.location.z - self.depth
        else:
            matrix_world.translation.z -= self.depth
        obj.matrix_world = Matrix.Rotation(self.x_angle, 4, "X") @ matrix_world
        bpy.context.view_layer.update()
        self.collection.objects.link(obj)

        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
        )
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=self.relating_type)

        blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        representation = ifcopenshell.api.run(
            "geometry.add_slab_representation",
            tool.Ifc.get(),
            context=self.body_context,
            depth=self.depth,
            x_angle=self.x_angle,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
        )

        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        tool.Blender.remove_data_block(mesh)

        if self.footprint_context:
            extrusion = tool.Model.get_extrusion(representation)
            if extrusion.SweptArea.is_a("IfcArbitraryClosedProfileDef"):
                curves = [extrusion.SweptArea.OuterCurve]
                if extrusion.SweptArea.is_a("IfcArbitraryProfileDefWithVoids"):
                    curves.extend(extrusion.SweptArea.InnerCurves)
                representation = ifcopenshell.api.run(
                    "geometry.add_footprint_representation",
                    tool.Ifc.get(),
                    context=self.footprint_context,
                    curves=curves,
                )
                ifcopenshell.api.run(
                    "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
                )

        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbLayer3"})
        obj.select_set(True)
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
                            self.change_thickness(element, total_thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, total_thickness)

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        relating_type = settings["relating_type"]

        new_material = ifcopenshell.util.element.get_material(relating_type)
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return

        parametric = ifcopenshell.util.element.get_psets(settings["relating_type"]).get("EPset_Parametric")
        layer_set_direction = None
        if parametric:
            layer_set_direction = parametric.get("LayerSetDirection", layer_set_direction)
        new_thickness = sum([l.LayerThickness for l in new_material.MaterialLayers])

        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        for related_object in settings["related_objects"]:
            self._regenerate_from_type(related_object, layer_set_direction, new_thickness)

    def _regenerate_from_type(
        self, related_object: ifcopenshell.entity_instance, layer_set_direction: Optional[str], new_thickness: float
    ) -> None:
        obj = tool.Ifc.get_object(related_object)
        if not obj or not obj.data or not obj.data.BIMMeshProperties.ifc_definition_id:
            return

        material = ifcopenshell.util.element.get_material(related_object)
        if not material or not material.is_a("IfcMaterialLayerSetUsage"):
            return
        if layer_set_direction:
            material.LayerSetDirection = layer_set_direction
        if material.LayerSetDirection == "AXIS3":
            self.change_thickness(related_object, new_thickness)

    def change_thickness(self, element: ifcopenshell.entity_instance, thickness: float) -> None:
        body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        obj = tool.Ifc.get_object(element)
        if not obj:
            return

        delta_thickness = (thickness * self.unit_scale) - obj.dimensions.z
        if round(delta_thickness, 2) == 0:
            return

        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            extrusion = tool.Model.get_extrusion(representation)
            if extrusion:
                extrusion.Depth = thickness
            else:
                props = bpy.context.scene.BIMModelProperties
                x_angle = 0 if tool.Cad.is_x(props.x_angle, 0, tolerance=0.001) else props.x_angle
                new_rep = ifcopenshell.api.run(
                    "geometry.add_slab_representation",
                    tool.Ifc.get(),
                    context=body_context,
                    depth=thickness * self.unit_scale,
                    x_angle=x_angle,
                )
                for inverse in tool.Ifc.get().get_inverse(representation):
                    ifcopenshell.util.element.replace_attribute(inverse, representation, new_rep)
                blenderbim.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=new_rep,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )
                blenderbim.core.geometry.remove_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=representation
                )
                return
        else:
            props = bpy.context.scene.BIMModelProperties
            x_angle = 0 if tool.Cad.is_x(props.x_angle, 0, tolerance=0.001) else props.x_angle
            representation = ifcopenshell.api.run(
                "geometry.add_slab_representation",
                tool.Ifc.get(),
                context=body_context,
                depth=thickness * self.unit_scale,
                x_angle=x_angle,
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
            )

        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

        obj.location[2] -= delta_thickness


class EnableEditingSketchExtrusionProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_sketch_extrusion_profile"
    bl_label = "Enable Editing Sketch Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        pset = ifcopenshell.util.element.get_psets(element).get("EPset_Parametric", None)
        if pset and pset["Engine"] == "CADSketcher" and pset["Entities"]:
            context.scene["sketcher"].update(json.loads(pset["Entities"]))
            bpy.context.view_layer.update()
            bpy.ops.wm.tool_set_by_id(name="sketcher.slvs_select")
            bpy.ops.view3d.slvs_set_all_constraints_visibility(visibility="SHOW")
            return {"FINISHED"}

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = tool.Model.get_extrusion(body)
        profile = extrusion.SweptArea
        if extrusion.Position:
            position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
            position.matrix_world.translation *= self.unit_scale
        else:
            position = Matrix()

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

        points = []

        for vertex in self.vertices:
            points.append(context.scene.sketcher.entities.add_point_2d(vertex.to_2d(), sketch))
        for edge in self.edges:
            context.scene.sketcher.entities.add_line_2d(points[edge[0]], points[edge[1]], sketch)

        bpy.ops.view3d.slvs_set_active_sketch(index=sketch.slvs_index)
        return {"FINISHED"}

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
            self.edges[-1] = (len(self.vertices) - 1, offset)  # Close the loop
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
                for local_point in curve.Points.CoordList:
                    global_point = position @ Vector(self.convert_unit_to_si(local_point)).to_3d()
                    self.vertices.append(global_point)
                # Curves without segments are self closing
                del self.vertices[-1]

            self.edges.extend([(i, i + 1) for i in range(offset, len(self.vertices))])
            self.edges[-1] = (len(self.vertices) - 1, offset)  # Close the loop
        elif curve.is_a("IfcCircle"):
            center = self.convert_unit_to_si(
                Matrix(ifcopenshell.util.placement.get_axis2placement(curve.Position).tolist()).translation
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


class EditSketchExtrusionProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_sketch_extrusion_profile"
    bl_label = "Edit Sketch Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        extrusion = tool.Model.get_extrusion(representation)
        if extrusion.Position:
            position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
        else:
            position = Matrix()
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

        old_profile = extrusion.SweptArea
        extrusion.SweptArea = profile
        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_profile)

        pset = ifcopenshell.util.element.get_psets(element).get("EPset_Parametric", None)
        if pset:
            pset = tool.Ifc.get().by_id(pset["id"])
        else:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="EPset_Parametric")
        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Engine": "CADSketcher", "Entities": json.dumps(context.scene["sketcher"].to_dict())},
        )

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
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        return {"FINISHED"}


class DisableEditingSketchExtrusionProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_sketch_extrusion_profile"
    bl_label = "Disable Editing Sketch Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        sketch = context.scene.sketcher.active_sketch
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
        return {"FINISHED"}


def disable_editing_extrusion_profile(context):
    ProfileDecorator.uninstall()
    bpy.ops.object.mode_set(mode="OBJECT")

    obj = context.active_object
    element = tool.Ifc.get_entity(obj)
    body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")

    profile_mesh = obj.data
    blenderbim.core.geometry.switch_representation(
        tool.Ifc,
        tool.Geometry,
        obj=obj,
        representation=body,
        should_reload=True,
        is_global=True,
        should_sync_changes_first=False,
    )
    tool.Geometry.delete_data(profile_mesh)
    return {"FINISHED"}


class DisableEditingExtrusionProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_extrusion_profile"
    bl_label = "Disable Editing Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        return disable_editing_extrusion_profile(context)


class EnableEditingExtrusionProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_extrusion_profile"
    bl_label = "Enable Editing Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        body = ifcopenshell.util.representation.resolve_representation(body)
        extrusion = tool.Model.get_extrusion(body)

        if extrusion.Position:
            position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
            position.translation *= self.unit_scale
        else:
            position = Matrix()

        tool.Model.import_profile(extrusion.SweptArea, obj=obj, position=position)

        bpy.ops.object.mode_set(mode="EDIT")
        ProfileDecorator.install(context, exit_edit_mode_callback=lambda: disable_editing_extrusion_profile(context))
        if not bpy.app.background:
            tool.Blender.set_viewport_tool("bim.cad_tool")
        return {"FINISHED"}


class EditExtrusionProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_extrusion_profile"
    bl_label = "Edit Extrusion Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        ProfileDecorator.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")

        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        body = ifcopenshell.util.representation.resolve_representation(body)
        extrusion = tool.Model.get_extrusion(body)
        if extrusion.Position:
            position = Matrix(ifcopenshell.util.placement.get_axis2placement(extrusion.Position).tolist())
            position.translation *= self.unit_scale
        else:
            position = Matrix()

        profile = tool.Model.export_profile(obj, position=position)

        if not profile:

            def msg(self, context):
                self.layout.label(text="INVALID PROFILE")

            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            ProfileDecorator.install(
                context, exit_edit_mode_callback=lambda: disable_editing_extrusion_profile(context)
            )
            bpy.ops.object.mode_set(mode="EDIT")
            return

        old_profile = extrusion.SweptArea
        for inverse in tool.Ifc.get().get_inverse(old_profile):
            ifcopenshell.util.element.replace_attribute(inverse, old_profile, profile)
        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_profile)

        profile_mesh = obj.data
        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        bpy.data.meshes.remove(profile_mesh)

        # Only certain classes should have a footprint
        if element.is_a() not in ("IfcSlab", "IfcRamp"):
            return

        footprint_context = ifcopenshell.util.representation.get_context(
            tool.Ifc.get(), "Plan", "FootPrint", "SKETCH_VIEW"
        )
        if not footprint_context:
            return

        curves = [profile.OuterCurve]
        if profile.is_a("IfcArbitraryProfileDefWithVoids"):
            curves.extend(profile.InnerCurves)
        new_footprint = ifcopenshell.api.run(
            "geometry.add_footprint_representation", tool.Ifc.get(), context=footprint_context, curves=curves
        )
        old_footprint = ifcopenshell.util.representation.get_representation(element, "Plan", "FootPrint", "SKETCH_VIEW")
        if old_footprint:
            for inverse in tool.Ifc.get().get_inverse(old_footprint):
                ifcopenshell.util.element.replace_attribute(inverse, old_footprint, new_footprint)
            blenderbim.core.geometry.remove_representation(
                tool.Ifc, tool.Geometry, obj=obj, representation=old_footprint
            )
        else:
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_footprint
            )


class ResetVertex(bpy.types.Operator):
    bl_idname = "bim.reset_vertex"
    bl_label = "Reset Vertex"
    bl_options = {"REGISTER", "UNDO"}

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
        for group in obj.vertex_groups:
            group.remove(selected_vertices)
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class SetArcIndex(bpy.types.Operator):
    bl_idname = "bim.set_arc_index"
    bl_label = "Set Arc Index"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj) and obj.type == "MESH"

    def cancel_message(self, msg):
        self.report({"ERROR"}, msg)
        return {"CANCELLED"}

    def execute(self, context):
        # NOTE: undo won't remove new verex group
        # because of jumping between modes
        obj = context.active_object

        bm = tool.Blender.get_bmesh_for_mesh(obj.data)
        selected_vertices = [v.index for v in bm.verts if v.select]
        if len(selected_vertices) != 3:
            return self.cancel_message("Select 3 vertices.")

        bpy.ops.object.mode_set(mode="OBJECT")
        in_group = any([bool(obj.data.vertices[v].groups) for v in selected_vertices])
        for group in obj.vertex_groups:
            group.remove(selected_vertices)
        group = obj.vertex_groups.new(name="IFCARCINDEX")
        group.add(selected_vertices, 1, "REPLACE")
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}
