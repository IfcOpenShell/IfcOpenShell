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
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.geometry
import ifcopenshell.util.schema
import ifcopenshell.util.element
import ifcopenshell.util.type
import bonsai.bim.handler
import bonsai.core.root as core
import bonsai.core.geometry
import bonsai.tool as tool
import bonsai.bim.module.root.prop as root_prop
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import get_enum_items, prop_with_search
from mathutils import Vector


class EnableReassignClass(bpy.types.Operator):
    bl_idname = "bim.enable_reassign_class"
    bl_label = "Enable Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        self.file = IfcStore.get_file()
        ifc_class = obj.name.split("/")[0]
        context.active_object.BIMObjectProperties.is_reassigning_class = True
        ifc_products = [
            "IfcElement",
            "IfcElementType",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcContext",
            "IfcAnnotation",
            "IfcRelSpaceBoundary",
        ]
        for ifc_product in ifc_products:
            if ifcopenshell.util.schema.is_a(IfcStore.get_schema().declaration_by_name(ifc_class), ifc_product):
                context.scene.BIMRootProperties.ifc_product = ifc_product
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        context.scene.BIMRootProperties.ifc_class = element.is_a()
        context.scene.BIMRootProperties.relating_class_object = None
        if hasattr(element, "PredefinedType"):
            if element.PredefinedType:
                context.scene.BIMRootProperties.ifc_predefined_type = element.PredefinedType
            userdefined_type = ifcopenshell.util.element.get_predefined_type(element)
            context.scene.BIMRootProperties.ifc_userdefined_type = userdefined_type or ""
        return {"FINISHED"}


class DisableReassignClass(bpy.types.Operator):
    bl_idname = "bim.disable_reassign_class"
    bl_label = "Disable Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class ReassignClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reassign_class"
    bl_label = "Reassign IFC Class"
    bl_description = "Reassign IFC class for selected objects"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = set(context.selected_objects + [context.active_object])
        self.file = IfcStore.get_file()
        root_props = context.scene.BIMRootProperties
        ifc_product: str = root_props.ifc_product
        ifc_class: str = root_props.ifc_class
        type_ifc_class = next(iter(ifcopenshell.util.type.get_applicable_types(ifc_class)), None)

        predefined_type = root_props.ifc_predefined_type
        if predefined_type == "USERDEFINED":
            predefined_type = root_props.ifc_userdefined_type

        # NOTE: root.reassign_class
        # automatically will reassign class for other occurrences of the type
        # so we need to run it only for the types or non-typed elements
        elements_to_reassign: dict[ifcopenshell.entity_instance, str] = dict()
        # need to update blender object name
        # for all elements that were changed in the process
        elements_to_update: set[ifcopenshell.entity_instance] = set()
        for obj in objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue

            same_ifc_product = element.is_a(ifc_product)

            if not same_ifc_product:
                if not (element.is_a("IfcElement") and ifc_product == "IfcElementType") and not (
                    element.is_a("IfcElementType") and ifc_product == "IfcElement"
                ):
                    self.report(
                        {"ERROR"}, f"Not supported class reassignment for object '{obj.name}' -> {ifc_product}."
                    )
                    return {"CANCELLED"}

            obj.BIMObjectProperties.is_reassigning_class = False
            if element.is_a("IfcTypeObject"):
                elements_to_reassign[element] = ifc_class
                elements_to_update.update(ifcopenshell.util.element.get_types(element))
                continue
            elif same_ifc_product and (element_type := ifcopenshell.util.element.get_type(element)):
                assert type_ifc_class
                elements_to_reassign[element_type] = type_ifc_class
                elements_to_update.update(ifcopenshell.util.element.get_types(element_type))
                continue

            # non-typed element
            elements_to_reassign[element] = ifc_class

        # store elements to objects to update later as elements will get invalid
        # after class reassignment
        elements_to_update = elements_to_update | set(elements_to_reassign)
        objects_to_update = set(o for e in elements_to_update if (o := tool.Ifc.get_object(e)))

        reassigned_elements = set()
        for element, ifc_class_ in elements_to_reassign.items():
            element = ifcopenshell.api.run(
                "root.reassign_class",
                self.file,
                product=element,
                ifc_class=ifc_class_,
                predefined_type=predefined_type,
            )
            reassigned_elements.add(element)

        for obj in objects_to_update:
            obj.name = tool.Loader.get_name(tool.Ifc.get_entity(obj))
            tool.Collector.assign(obj)
        return {"FINISHED"}


class AssignClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_class"
    bl_label = "Assign IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Assign the IFC Class to the selected objects"
    obj: bpy.props.StringProperty()
    ifc_class: bpy.props.StringProperty()
    predefined_type: bpy.props.StringProperty()
    userdefined_type: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()
    should_add_representation: bpy.props.BoolProperty(default=True)
    ifc_representation_class: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMRootProperties
        objects: list[bpy.types.Object] = []
        if self.obj:
            objects = [bpy.data.objects[self.obj]]
        elif objects := context.selected_objects:
            pass
        elif obj := context.active_object:
            objects = [obj]

        if not objects:
            self.report({"INFO"}, "No objects selected.")
            return

        ifc_class = self.ifc_class or props.ifc_class
        predefined_type = self.userdefined_type if self.predefined_type == "USERDEFINED" else self.predefined_type
        ifc_context = self.context_id
        if not ifc_context and get_enum_items(props, "contexts", context):
            ifc_context = int(props.contexts or "0") or None
        if ifc_context:
            ifc_context = tool.Ifc.get().by_id(ifc_context)
        active_object = context.active_object
        for obj in objects:
            if obj.mode != "OBJECT":
                self.report({"ERROR"}, "Object must be in OBJECT mode to assign class")
                continue
            element = core.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=False,
                context=ifc_context,
                ifc_representation_class=self.ifc_representation_class,
            )
            if self.should_add_representation and obj.data and len(obj.data.vertices):
                representation = tool.Geometry.export_mesh_to_tessellation(obj, ifc_context)
                ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj=obj,
                    representation=representation,
                    should_reload=True,
                    is_global=True,
                    should_sync_changes_first=False,
                )

        context.view_layer.objects.active = active_object


class UnlinkObject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_object"
    bl_label = "Unlink Object"
    bl_description = (
        "Unlink Blender object from it's linked IFC element.\n\n"
        "You can either remove element the blender object is linked to from IFC or keep it. "
        "Note that keeping the unlinked element in IFC might lead to unpredictable issues "
        "and should be used only by advanced users"
    )
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty(name="Object Name")
    should_delete: bpy.props.BoolProperty(name="Delete IFC Element", default=True)
    skip_invoke: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def _execute(self, context):
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = context.selected_objects

        objects: list[bpy.types.Object]
        for obj in objects:
            was_active_object = obj == context.active_object

            tool.Ifc.finish_edit(obj)

            element = tool.Ifc.get_entity(obj)
            if element and self.should_delete:
                object_name = obj.name

                # Copy object, so it won't be removed by `delete_ifc_object`
                obj_copy = obj.copy()
                if obj.data:
                    obj_copy.data = obj.data.copy()

                    # prevent unlinking materials that might be used elsewhere
                    replacements: dict[bpy.types.Material, bpy.types.Material] = dict()
                    for material_slot in obj_copy.material_slots:
                        material = material_slot.material
                        if material is None:
                            continue

                        if material in replacements:
                            material_replacement = replacements[material]

                        # no need to copy non-ifc materials as unlinking won't do anything to them
                        elif tool.Ifc.get_entity(material) is None:
                            replacements[material] = material
                            continue

                        else:
                            material_replacement = material.copy()
                            replacements[material] = material_replacement

                        material_slot.material = material_replacement

                tool.Geometry.delete_ifc_object(obj)

                obj = obj_copy
                obj.name = object_name
            elif element:
                if obj.data.users > 1:
                    obj.data = obj.data.copy()
                tool.Ifc.unlink(element)

            tool.Root.unlink_object(obj)
            for collection in obj.users_collection:
                # Reset collection because its original collection may be removed too.
                collection.objects.unlink(obj)
            bpy.context.scene.collection.objects.link(obj)

            if was_active_object:
                tool.Blender.set_active_object(obj)
        return {"FINISHED"}

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "should_delete")

    def invoke(self, context, event):
        if self.skip_invoke:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self)


class AddElement(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_element"
    bl_label = "Add Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add an IFC physical product, construction type, and more"

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, is_invoke=True)

    def _invoke(self, context, event):
        # For convenience, preselect OBJ representation template if applicable
        if (obj := context.active_object) and obj.type == "MESH":
            props = context.scene.BIMRootProperties
            props.representation_template = "OBJ"
            props.representation_obj = obj
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        props = context.scene.BIMRootProperties
        predefined_type = (
            props.userdefined_type if props.ifc_predefined_type == "USERDEFINED" else props.ifc_predefined_type
        )
        representation_template = props.representation_template

        ifc_context = None
        if get_enum_items(props, "contexts", context):
            ifc_context = int(props.contexts or "0") or None
            if ifc_context:
                ifc_context = tool.Ifc.get().by_id(ifc_context)

        if representation_template in (
            "EMPTY",
            "LAYERSET_AXIS2",
            "LAYERSET_AXIS3",
            "PROFILESET",
        ) or representation_template.startswith("FLOW_SEGMENT_"):
            mesh = None
        elif representation_template == "OBJ" and not props.representation_obj:
            mesh = None
        else:
            mesh = bpy.data.meshes.new("Mesh")

        obj = bpy.data.objects.new(props.ifc_class[3:], mesh)
        obj.location = bpy.context.scene.cursor.location
        element = core.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=props.ifc_class,
            predefined_type=predefined_type,
            should_add_representation=False,
        )

        if representation_template == "EMTPY" or not ifc_context:
            pass
        elif representation_template == "OBJ" and props.representation_obj:
            obj.matrix_world = props.representation_obj.matrix_world
            representation = tool.Geometry.export_mesh_to_tessellation(props.representation_obj, ifc_context)
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )
            if not tool.Ifc.get_entity(props.representation_obj):
                bpy.data.objects.remove(props.representation_obj)
        elif representation_template == "MESH":
            builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=0.5)
            verts = [v.co / unit_scale for v in bm.verts]
            faces = [[v.index for v in p.verts] for p in bm.faces]
            item = builder.mesh(verts, faces)
            bm.free()
            representation = builder.get_representation(ifc_context, [item])
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )
        elif representation_template == "EXTRUSION":
            builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            curve = builder.rectangle(size=Vector((0.5, 0.5)) / unit_scale)
            item = builder.extrude(curve, magnitude=0.5 / unit_scale)
            representation = builder.get_representation(ifc_context, [item])
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )
        elif representation_template in ("LAYERSET_AXIS2", "LAYERSET_AXIS3"):
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            materials = tool.Ifc.get().by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = ifcopenshell.api.run("material.add_material", tool.Ifc.get(), name="Unknown")
            rel = ifcopenshell.api.run(
                "material.assign_material", tool.Ifc.get(), products=[element], type="IfcMaterialLayerSet"
            )
            layer_set = rel.RelatingMaterial
            layer = ifcopenshell.api.run("material.add_layer", tool.Ifc.get(), layer_set=layer_set, material=material)
            thickness = 0.1  # Arbitrary metric thickness for now
            layer.LayerThickness = thickness / unit_scale
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="EPset_Parametric")
            if representation_template == "LAYERSET_AXIS2":
                axis = "AXIS2"
            elif representation_template == "LAYERSET_AXIS3":
                axis = "AXIS3"
            ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"LayerSetDirection": axis})
        elif representation_template == "PROFILESET" or representation_template.startswith("FLOW_SEGMENT_"):
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            materials = tool.Ifc.get().by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = ifcopenshell.api.run("material.add_material", tool.Ifc.get(), name="Unknown")
            if representation_template == "PROFILESET":
                named_profiles = [p for p in tool.Ifc.get().by_type("IfcProfileDef") if p.ProfileName]
                if named_profiles:
                    profile = named_profiles[0]
                else:
                    size = 0.5 / unit_scale
                    profile = tool.Ifc.get().create_entity(
                        "IfcRectangleProfileDef", ProfileName="New Profile", ProfileType="AREA", XDim=size, YDim=size
                    )
            else:
                # NOTE: defaults dims are in meters / mm
                # for now default names are hardcoded to mm
                if representation_template == "FLOW_SEGMENT_RECTANGULAR":
                    default_x_dim = 0.4
                    default_y_dim = 0.2
                    profile_name = f"{props.ifc_class}-{default_x_dim*1000}x{default_y_dim*1000}"
                    profile = tool.Ifc.get().create_entity(
                        "IfcRectangleProfileDef",
                        ProfileName=profile_name,
                        ProfileType="AREA",
                        XDim=default_x_dim / unit_scale,
                        YDim=default_y_dim / unit_scale,
                    )
                elif representation_template == "FLOW_SEGMENT_CIRCULAR":
                    default_diameter = 0.1
                    profile_name = f"{props.ifc_class}-{default_diameter*1000}"
                    profile = tool.Ifc.get().create_entity(
                        "IfcCircleProfileDef",
                        ProfileName=profile_name,
                        ProfileType="AREA",
                        Radius=(default_diameter / 2) / unit_scale,
                    )
                elif representation_template == "FLOW_SEGMENT_CIRCULAR_HOLLOW":
                    default_diameter = 0.15
                    default_thickness = 0.005
                    profile_name = f"{props.ifc_class}-{default_diameter*1000}x{default_thickness*1000}"
                    profile = tool.Ifc.get().create_entity(
                        "IfcCircleHollowProfileDef",
                        ProfileName=profile_name,
                        ProfileType="AREA",
                        Radius=(default_diameter / 2) / unit_scale,
                        WallThickness=default_thickness,
                    )

            rel = ifcopenshell.api.run(
                "material.assign_material", tool.Ifc.get(), products=[element], type="IfcMaterialProfileSet"
            )
            profile_set = rel.RelatingMaterial
            material_profile = ifcopenshell.api.run(
                "material.add_profile", tool.Ifc.get(), profile_set=profile_set, material=material
            )
            ifcopenshell.api.run(
                "material.assign_profile", tool.Ifc.get(), material_profile=material_profile, profile=profile
            )
        elif representation_template == "WINDOW":
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_window()
        elif representation_template == "DOOR":
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_door()
        elif representation_template == "STAIR":
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_stair()
        elif representation_template == "RAILING":
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_railing()
        elif representation_template == "ROOF":
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_roof()

    def draw(self, context):
        props = context.scene.BIMRootProperties
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        prop_with_search(self.layout, props, "ifc_product", text="Definition")
        prop_with_search(self.layout, props, "ifc_class", should_click_ok_to_validate=True)
        ifc_predefined_types = root_prop.get_ifc_predefined_types(context.scene.BIMRootProperties, context)
        if ifc_predefined_types:
            prop_with_search(self.layout, props, "ifc_predefined_type")
            if props.ifc_predefined_type == "USERDEFINED":
                row = self.layout.row()
                row.prop(props, "ifc_userdefined_type")
        prop_with_search(self.layout, props, "representation_template", text="Representation")
        if props.representation_template == "OBJ":
            row = self.layout.row()
            row.prop(props, "representation_obj", text="Object")
        if props.representation_template != "EMPTY":
            prop_with_search(self.layout, props, "contexts")


class LaunchAddElement(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.launch_add_element"
    bl_label = "Add Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add an IFC physical product, construction type, and more"

    def execute(self, context):
        # This stub operator is needed because operators from menu skip the invoke call
        bpy.ops.bim.add_element("INVOKE_DEFAULT")
        return {"FINISHED"}
