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

import hashlib
import json
import logging
import multiprocessing
import os
import shutil
import subprocess
import time
from math import radians
from pathlib import Path
from timeit import default_timer as timer
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    Optional,
    TypedDict,
    Union,
    get_args,
)

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.document
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.api.style
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.selector
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import numpy as np
import shapely
from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import ImportHelper
from lxml import etree
from mathutils import Color, Vector

import bonsai.bim.export_ifc
import bonsai.bim.handler
import bonsai.bim.import_ifc
import bonsai.bim.module.drawing.sheeter as sheeter
import bonsai.bim.module.drawing.svgwriter as svgwriter
import bonsai.core.drawing as core
import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim.helper import prop_with_search
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.decorator import PolylineDecorator
from bonsai.bim.module.model.polyline import PolylineOperator
from bonsai.bim.module.drawing.data import DecoratorData, ElementValuesData
from bonsai.bim.module.drawing.decoration import CutDecorator
from bonsai.bim.module.drawing.prop import (
    RASTER_STYLE_PROPERTIES_EXCLUDE,
    RasterStyleProperty,
)
from bonsai.bim.module.drawing.ui import get_current_product_for_element_values
from bonsai.bim.prop import StrProperty

if TYPE_CHECKING:
    from bpy.stub_internal import rna_enums

    from bonsai.bim.module.drawing.prop import RenderType
    from bonsai.bim.module.project.prop import Link

cwd = os.path.dirname(os.path.realpath(__file__))


class profile:
    """
    A python context manager timing utility
    """

    def __init__(self, task):
        self.task = task

    def __enter__(self):
        self.start = timer()

    def __exit__(self, *args):
        print(self.task, timer() - self.start)


class LineworkContexts(NamedTuple):
    body: list[list[int]]
    annotation: list[list[int]]


class AddAnnotationType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_annotation_type"
    bl_label = "Add Annotation Type"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Drawing.get_annotation_props()
        object_type = props.object_type
        has_representation = props.create_representation_for_type
        drawing = tool.Ifc.get_entity(bpy.context.scene.camera)

        if props.create_representation_for_type:
            obj = tool.Drawing.create_annotation_object(drawing, object_type)
        else:
            obj = bpy.data.objects.new(object_type, None)

        obj.name = props.type_name
        ifc_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Annotation", "MODEL_VIEW")
        element = tool.Drawing.run_root_assign_class(
            obj=obj,
            ifc_class="IfcTypeProduct",
            predefined_type=object_type,
            should_add_representation=has_representation,
            context=ifc_context,
            ifc_representation_class=tool.Drawing.get_ifc_representation_class(object_type),
        )
        if representation := tool.Drawing.get_representation(element, ifc_context):
            tool.Drawing.reload_representation(obj=obj, representation=representation)
        element.ApplicableOccurrence = f"IfcAnnotation/{object_type}"

        if props.create_representation_for_type and object_type == "IMAGE":
            bpy.ops.bim.add_reference_image("INVOKE_DEFAULT", existing_object_by_name=obj.name)


class EnableAddAnnotationType(bpy.types.Operator):
    bl_idname = "bim.enable_add_annotation_type"
    bl_label = "Enable Add Annotation Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        tool.Drawing.get_annotation_props().is_adding_type = True
        return {"FINISHED"}


class DisableAddAnnotationType(bpy.types.Operator):
    bl_idname = "bim.disable_add_annotation_type"
    bl_label = "Disable Add Annotation Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        tool.Drawing.get_annotation_props().is_adding_type = False
        return {"FINISHED"}


class AddDrawing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_drawing"
    bl_label = "Add Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Add a drawing view to the IFC project.\n\n"
        "For all views besides MODEL_VIEW camera will be placed at the current cursor position,\n"
        "for MODEL_VIEW camera will be aligned to the current viewport position and orientation."
    )

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        hint = props.location_hint
        if props.target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]:
            hint = int(hint)
        else:
            assert hint in tool.Drawing.LOCATION_HINT_LITERALS
        core.add_drawing(
            tool.Ifc,
            tool.Collector,
            tool.Drawing,
            target_view=props.target_view,
            location_hint=hint,
        )

        # TODO: Why need to resync active drawing, if it wasn't changed.
        drawing = props.get_active_drawing()
        if drawing is None:
            return
        core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=drawing)


class DuplicateDrawing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_drawing"
    bl_label = "Duplicate Drawing"
    bl_description = "Make a copy of currently selected drawing"
    bl_options = {"REGISTER", "UNDO"}
    drawing: bpy.props.IntProperty()
    should_duplicate_annotations: bpy.props.BoolProperty(name="Should Duplicate Annotations", default=False)

    @classmethod
    def poll(cls, context):
        if not tool.Drawing.get_active_drawing_item():
            cls.poll_message_set("No drawing selected.")
            return False
        return True

    def invoke(self, context, event):
        assert context.window_manager
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        assert self.layout
        row = self.layout
        row.prop(self, "should_duplicate_annotations")

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        core.duplicate_drawing(
            tool.Ifc,
            tool.Blender,
            tool.Drawing,
            tool.Geometry,
            drawing=tool.Ifc.get().by_id(self.drawing),
            should_duplicate_annotations=self.should_duplicate_annotations,
        )


class CreateDrawing(bpy.types.Operator):
    """Creates/refreshes a .svg drawing

    Only available if :
    - IFC file is created
    - Camera is in Orthographic mode"""

    bl_idname = "bim.create_drawing"
    bl_label = "Create Drawing"
    bl_description = (
        "Creates/refreshes a .svg drawing based on currently active camera\n"
        + 'and open with default system viewer or using "svg_command" or\n'
        + '"pdf_command" from the Bonsai preferences (if provided).\n\n'
        + "SHIFT+CLICK to create/refresh all shown checked drawings, but doesn't\n"
        + "open them for viewing.\n\n"
        + "Add the CTRL modifier to optionally open drawings to view them as\n"
        + "they are created"
    )
    print_all: bpy.props.BoolProperty(
        name="Print All",
        default=False,
        options={"SKIP_SAVE"},
    )
    open_viewer: bpy.props.BoolProperty(
        name="Open in Viewer",
        default=False,
        options={"SKIP_SAVE"},
    )
    sync: bpy.props.BoolProperty(
        name="Sync Before Creating Drawing",
        description="Could save some time if you're sure IFC and current Blender session are already in sync",
        default=True,
    )

    if TYPE_CHECKING:
        print_all: bool
        open_viewer: bool
        sync: bool

    drawing_name: str
    is_manifold_cache: dict[str, bool]

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        if not tool.Drawing.is_drawing_active():
            cls.poll_message_set("No active drawing.")
            return False
        assert context.scene
        assert (camera_obj := context.scene.camera)
        if tool.Drawing.get_camera_props(camera_obj).linework_mode == "FREESTYLE" and not hasattr(
            context.scene, "svg_export"
        ):
            cls.poll_message_set(
                "Freestyle SVG Exporter extension is not installed (required for 'Freestyle' linework mode)."
            )
            return False
        return True

    def invoke(self, context, event):
        # printing all drawings on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.print_all = True
        if event.type == "LEFTMOUSE" and event.ctrl:
            self.open_viewer = True
        return self.execute(context)

    def execute(self, context):
        self.props = tool.Drawing.get_document_props()
        assert context.scene and context.scene.camera

        active_drawing_id = tool.Blender.get_ifc_definition_id(context.scene.camera)
        original_drawing_id = None
        if self.print_all:
            original_drawing_id = active_drawing_id
            drawings_to_print = [d.ifc_definition_id for d in self.props.drawings if d.is_selected and d.is_drawing]
        else:
            drawings_to_print = [active_drawing_id]

        for drawing_i, drawing_id in enumerate(drawings_to_print):
            self.drawing_index = drawing_i
            if self.print_all:
                bpy.ops.bim.activate_drawing(drawing=drawing_id, should_view_from_camera=False)
                original_cache_setting = self.props.should_use_underlay_cache
                self.props.should_use_underlay_cache = False

                # Force Blender to process all pending operations
                for area in context.screen.areas:
                    area.tag_redraw()

                # Process events to let Blender finish internal cleanup
                bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
            self.camera = context.scene.camera
            assert (camera_element := tool.Ifc.get_entity(self.camera))
            self.camera_element = camera_element
            self.camera_document = tool.Drawing.get_drawing_document(self.camera_element)
            self.file = tool.Ifc.get()

            with profile("Drawing generation process"):
                with profile("Initialize drawing generation process"):
                    self.cprops = tool.Drawing.get_camera_props(self.camera)
                    self.drawing = self.file.by_id(drawing_id)
                    self.drawing_name = self.drawing.Name
                    self.metadata = tool.Drawing.get_drawing_metadata(self.camera_element)
                    self.get_scale(context)
                    if self.cprops.update_representation(self.camera.matrix_world):
                        bpy.ops.bim.update_representation(obj=self.camera.name, ifc_representation_class="")
                        # Reassign props as data is recreated during the update.
                        self.cprops = tool.Drawing.get_camera_props(self.camera)

                    camera_dims = self.get_camera_dimensions()
                    self.svg_writer = svgwriter.SvgWriter(
                        camera_width=camera_dims[0],
                        camera_height=camera_dims[1],
                        camera=self.camera,
                        camera_projection=(self.camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))),
                        scale=self.scale,
                        human_scale=self.human_scale,
                    )
                    self.svg_writer.setup_drawing_resource_paths(self.camera_element)

                underlay_svg = None
                linework_svg = None
                annotation_svg = None

                with profile("Generate underlay"):
                    if ifcopenshell.util.element.get_pset(self.drawing, "EPset_Drawing", "HasUnderlay"):
                        drawing_style = self.cprops.get_active_drawing_style()
                        if not drawing_style:
                            self.report(
                                {"ERROR"},
                                f"Failed to create drawing '{self.drawing.Name}' - drawing has underlay but there's no active drawing underlay style.",
                            )
                            return {"FINISHED"}

                        # Clear any local camera setup and force viewport to use scene camera
                        for area in context.screen.areas:
                            if area.type == "VIEW_3D":
                                for space in area.spaces:
                                    if space.type == "VIEW_3D":
                                        # Clear local camera to ensure we use scene.camera
                                        space.use_local_camera = False
                                        space.camera = context.scene.camera
                                        space.region_3d.view_perspective = "CAMERA"
                                        print(f"Set viewport camera to: {context.scene.camera.name}")
                                        break

                        # Force complete scene update
                        context.view_layer.update()
                        context.evaluated_depsgraph_get()

                        underlay_svg = self.generate_underlay(context)

                with profile("Generate linework"):
                    if tool.Drawing.is_camera_orthographic():
                        if self.cprops.linework_mode == "OPENCASCADE":
                            linework_svg = self.generate_linework(context)
                        elif self.cprops.linework_mode == "FREESTYLE":
                            linework_svg = self.generate_freestyle_linework(context)
                    elif self.cprops.linework_mode == "FREESTYLE":
                        linework_svg = self.generate_freestyle_linework(context)

                with profile("Generate annotation"):
                    if tool.Drawing.is_camera_orthographic():
                        annotation_svg = self.generate_annotation(context)

                with profile("Combine SVG layers"):
                    svg_path = self.combine_svgs(context, underlay_svg, linework_svg, annotation_svg)

            if self.open_viewer:
                drawing_uri = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_document(self.drawing))
                tool.Drawing.open_with_user_command(tool.Blender.get_addon_preferences().svg_command, drawing_uri)
        if not self.open_viewer:
            self.report({"INFO"}, f"{len(drawings_to_print)} drawings created...")
        if self.print_all:
            assert original_drawing_id is not None
            bpy.ops.bim.activate_drawing(drawing=original_drawing_id, should_view_from_camera=False)
        return {"FINISHED"}

    def get_camera_dimensions(self) -> tuple[float, float]:
        assert bpy.context.scene
        render = bpy.context.scene.render
        assert isinstance(self.camera.data, bpy.types.Camera)
        if self.is_landscape(render):
            width = self.camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = self.camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x
        return width, height

    def combine_svgs(
        self, context: bpy.types.Context, underlay: Optional[str], linework: Optional[str], annotation: Optional[str]
    ) -> str:
        # Hacky :)
        svg_path = self.get_svg_path()
        with open(svg_path, "w") as outfile:
            self.svg_writer.create_blank_svg(svg_path).define_boilerplate()
            boilerplate = self.svg_writer.svg.tostring()
            outfile.write(boilerplate.replace("</svg>", ""))
            if underlay:
                with open(underlay) as infile:
                    for i, line in enumerate(infile):
                        if i < 2:
                            continue
                        elif "</svg>" in line:
                            continue
                        outfile.write(line)
                shutil.copyfile(os.path.splitext(underlay)[0] + ".png", os.path.splitext(svg_path)[0] + "-underlay.png")
            if linework:
                with open(linework) as infile:
                    should_skip = False
                    for i, line in enumerate(infile):
                        if i == 0:
                            continue
                        if "</svg>" in line:
                            continue
                        elif "<defs>" in line:
                            should_skip = True
                            continue
                        elif "</defs>" in line:
                            should_skip = False
                            continue
                        elif should_skip:
                            continue
                        outfile.write(line)
            if annotation:
                with open(annotation) as infile:
                    for i, line in enumerate(infile):
                        if i < 2:
                            continue
                        if "</svg>" in line:
                            continue
                        outfile.write(line)
            outfile.write("</svg>")
        return svg_path

    def generate_underlay(self, context: bpy.types.Context) -> Union[str, None]:
        if not ifcopenshell.util.element.get_pset(self.drawing, "EPset_Drawing", "HasUnderlay"):
            return
        svg_path = self.get_svg_path(cache_type="underlay")
        if os.path.isfile(svg_path) and self.props.should_use_underlay_cache:
            return svg_path

        assert context.scene and context.view_layer and context.screen
        context.scene.render.filepath = str(Path(svg_path).with_suffix(".png"))
        assert (drawing_style := self.cprops.get_active_drawing_style())

        tool.Blender.sync_render_visibility()

        if drawing_style.render_type == "DEFAULT":
            bpy.ops.render.render(write_still=True)
        else:
            previous_visibility: dict[str, bool] = {}
            collection = tool.Blender.get_object_bim_props(self.camera).collection
            assert collection
            # Hide annotations.
            for obj in collection.objects:
                if context.view_layer.objects.get(obj.name):
                    previous_visibility[obj.name] = obj.hide_get()
                    obj.hide_set(True)

            # Hide objects that shouldn't appear on render - empties, camera, grids, etc.
            for obj in context.visible_objects:
                if (
                    (not obj.data and not obj.instance_collection)
                    or isinstance(obj.data, bpy.types.Camera)
                    or "IfcGrid/" in obj.name
                    or "IfcGridAxis/" in obj.name
                    or "IfcOpeningElement/" in obj.name
                ):
                    if context.view_layer.objects.get(obj.name):
                        previous_visibility[obj.name] = obj.hide_get()
                        obj.hide_set(True)

            assert (space := tool.Blender.get_view3d_space())
            previous_shading = space.shading.type
            previous_format = context.scene.render.image_settings.file_format
            space.shading.type = "RENDERED"
            context.scene.render.image_settings.file_format = "PNG"

            with tool.Blender.bonsai_crash_txt("render.opengl"):
                bpy.ops.render.opengl(write_still=True)

            space.shading.type = previous_shading
            context.scene.render.image_settings.file_format = previous_format

            for name, value in previous_visibility.items():
                bpy.data.objects[name].hide_set(value)

        self.svg_writer.create_blank_svg(svg_path).draw_underlay(context.scene.render.filepath).save()
        return svg_path

    def get_linework_contexts(self, ifc: ifcopenshell.file, target_view: str) -> LineworkContexts:
        plan_body_target_contexts: list[int] = []
        plan_body_model_contexts: list[int] = []
        model_body_target_contexts: list[int] = []
        model_body_model_contexts: list[int] = []

        plan_annotation_target_contexts: list[int] = []
        plan_annotation_model_contexts: list[int] = []
        model_annotation_target_contexts: list[int] = []
        model_annotation_model_contexts: list[int] = []

        for rep_context in ifc.by_type("IfcGeometricRepresentationContext"):
            if rep_context.is_a("IfcGeometricRepresentationSubContext"):
                if rep_context.ContextType == "Plan":
                    if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                        if rep_context.TargetView == target_view:
                            plan_body_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            plan_body_model_contexts.append(rep_context.id())
                    elif rep_context.ContextIdentifier == "Annotation":
                        if rep_context.TargetView == target_view:
                            plan_annotation_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            plan_annotation_model_contexts.append(rep_context.id())
                elif rep_context.ContextType == "Model":
                    if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                        if rep_context.TargetView == target_view:
                            model_body_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            model_body_model_contexts.append(rep_context.id())
                    elif rep_context.ContextIdentifier == "Annotation":
                        if rep_context.TargetView == target_view:
                            model_annotation_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            model_annotation_model_contexts.append(rep_context.id())
            elif rep_context.ContextType == "Model":
                # You should never purely assign to a "Model" context, but
                # if you do, this is what we assume your intention is.
                model_body_model_contexts.append(rep_context.id())
                continue

        body_contexts = (
            [
                plan_body_target_contexts,
                plan_body_model_contexts,
                model_body_target_contexts,
                model_body_model_contexts,
            ]
            if target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]
            else [
                model_body_target_contexts,
                model_body_model_contexts,
            ]
        )

        annotation_contexts = (
            [
                plan_annotation_target_contexts,
                plan_annotation_model_contexts,
                model_annotation_target_contexts,
                model_annotation_model_contexts,
            ]
            if target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]
            else [
                model_annotation_target_contexts,
                model_annotation_model_contexts,
            ]
        )

        return LineworkContexts(body_contexts, annotation_contexts)

    def serialize_contexts_elements(
        self,
        ifc: ifcopenshell.file,
        tree: ifcopenshell.geom.tree,
        contexts: LineworkContexts,
        context_type: Literal["body", "annotation"],
        drawing_elements: set[ifcopenshell.entity_instance],
        target_view: str,
    ) -> None:
        drawing_elements = drawing_elements.copy()
        contexts_: list[list[int]] = getattr(contexts, context_type)
        for context in contexts_:
            with profile(f"Processing {context_type} context"):
                if not context or not drawing_elements:
                    continue
                geom_settings = ifcopenshell.geom.settings()
                geom_settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
                geom_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)

                if ifc.by_id(context[0]).ContextType == "Plan" and "PLAN_VIEW" in target_view:
                    # A 2mm Z offset to combat Z-fighting in plan or RCPs
                    geom_settings.set("model-offset", (0.0, 0.0, 0.002 if target_view == "PLAN_VIEW" else -0.002))

                geom_settings.set("context-ids", context)
                it = ifcopenshell.geom.iterator(
                    geom_settings, ifc, multiprocessing.cpu_count(), include=drawing_elements
                )
                processed = set()
                for elem in it:
                    processed.add(ifc.by_id(elem.id))
                    self.serialiser.write(elem)
                    tree.add_element(elem)
                drawing_elements -= processed

    def generate_bisect_linework(self, context: bpy.types.Context, root) -> None:
        camera_matrix_i = context.scene.camera.matrix_world.inverted()

        group = root.find("{http://www.w3.org/2000/svg}g")
        raw_width, raw_height = self.get_camera_dimensions()
        x_offset = raw_width / 2
        y_offset = raw_height / 2
        svg_scale = self.scale * 1000  # IFC is in meters, SVG is in mm

        for obj in context.visible_objects:
            if obj.type != "MESH":
                continue
            if not (element := tool.Ifc.get_entity(obj)):
                continue
            if not tool.Drawing.is_intersecting_camera(obj, context.scene.camera):
                continue
            verts, edges = tool.Drawing.bisect_mesh(obj, context.scene.camera)

            g = etree.SubElement(root, "{http://www.w3.org/2000/svg}g")
            g.attrib["{http://www.ifcopenshell.org/ns}guid"] = element.GlobalId
            g.attrib["{http://www.ifcopenshell.org/ns}name"] = element.Name or ""

            lines = []
            for edge in edges:
                start = [o for o in (camera_matrix_i @ Vector(verts[edge[0]])).xy]
                end = [o for o in (camera_matrix_i @ Vector(verts[edge[1]])).xy]
                coords = [start, end]
                d = " ".join(
                    ["L{},{}".format((x_offset + p[0]) * svg_scale, (y_offset - p[1]) * svg_scale) for p in coords]
                )
                d = "M{}".format(d[1:])
                path = etree.SubElement(g, "{http://www.w3.org/2000/svg}path")
                path.attrib["d"] = d
            group.append(g)

    def generate_material_layers(self, context: bpy.types.Context, root) -> None:
        for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]"):
            if "projection" in el.get("class", "").split():
                continue
            element = self.get_element_by_guid(el.get("{http://www.ifcopenshell.org/ns}guid"))
            if not (obj := tool.Ifc.get_object(element)):
                continue
            if not (material := ifcopenshell.util.element.get_material(element)):
                continue
            if material.is_a() not in ("IfcMaterialLayerSet", "IfcMaterialLayerSetUsage"):
                continue

            self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

            if material.is_a("IfcMaterialLayerSetUsage"):
                usage = material
                layer_set = material.ForLayerSet
                offset = usage.OffsetFromReferenceLine * self.unit_scale
                sense_factor = 1 if usage.DirectionSense == "POSITIVE" else -1
            elif material.is_a("IfcMaterialLayerSet"):
                usage = None
                layer_set = material
                offset = 0
                sense_factor = 1

            camera_matrix_i = context.scene.camera.matrix_world.inverted()

            group = root.find("{http://www.w3.org/2000/svg}g")
            raw_width, raw_height = self.get_camera_dimensions()
            x_offset = raw_width / 2
            y_offset = raw_height / 2
            svg_scale = self.scale * 1000  # IFC is in meters, SVG is in mm

            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)

            # Slice our mesh into a 2D drawing cut (2D is always easier)
            camera_matrix = obj.matrix_world.inverted() @ context.scene.camera.matrix_world
            plane_co = camera_matrix.translation
            plane_no = camera_matrix.col[2].xyz
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(
                bm, geom=geom, dist=0.0001, plane_co=plane_co, plane_no=plane_no, clear_outer=True, clear_inner=True
            )
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.000001)
            bmesh.ops.triangle_fill(bm, use_dissolve=True, edges=bm.edges)

            prev_co = None
            if not usage:
                sense_factor = 1  # Assume the extrusion vector points in the direction sense
                no = tool.Drawing.get_extrusion_vector(element).normalized()
                co = Vector((0.0, 0.0, offset))
            elif usage.LayerSetDirection == "AXIS2":
                co = Vector((0.0, offset, 0.0))
                no = tool.Drawing.get_extrusion_vector(element).normalized()
                no = no.cross(Vector([1.0, 0.0, 0.0]))
            elif usage.LayerSetDirection == "AXIS3":
                co = Vector((0.0, 0.0, offset))
                no = tool.Drawing.get_extrusion_vector(element).normalized()
                no = Vector([0.0, 0.0, 1.0])
            elif usage.LayerSetDirection == "AXIS1":
                co = Vector((0.0, 0.0, offset))
                no = tool.Drawing.get_extrusion_vector(element).normalized()
                no = Vector([1.0, 0.0, 0.0])
            no *= sense_factor
            last_i = len(layer_set.MaterialLayers) - 1
            for i, layer in enumerate(layer_set.MaterialLayers):
                prev_co = co.copy()
                co += no * layer.LayerThickness * self.unit_scale

                bm_fill = bm.copy()
                if i != last_i:
                    geom = bm_fill.verts[:] + bm_fill.edges[:] + bm_fill.faces[:]
                    bmesh.ops.bisect_plane(bm_fill, geom=geom, dist=0.0001, plane_co=co, plane_no=no, clear_outer=True)
                if i != 0:
                    geom = bm_fill.verts[:] + bm_fill.edges[:] + bm_fill.faces[:]
                    bmesh.ops.bisect_plane(
                        bm_fill, geom=geom, dist=0.0001, plane_co=prev_co, plane_no=no, clear_inner=True
                    )

                bm_fill.verts.ensure_lookup_table()
                bm_fill.edges.ensure_lookup_table()
                verts = [tuple(obj.matrix_world @ v.co) for v in bm_fill.verts]
                edges = [[v.index for v in e.verts] for e in bm_fill.edges]

                g = etree.SubElement(root, "{http://www.w3.org/2000/svg}g")
                g.attrib["{http://www.ifcopenshell.org/ns}guid"] = element.GlobalId
                g.attrib["{http://www.ifcopenshell.org/ns}name"] = element.Name or ""
                g.attrib["{http://www.ifcopenshell.org/ns}layer-id"] = str(layer.id())

                lines = []
                for edge in edges:
                    start = [o for o in (camera_matrix_i @ Vector(verts[edge[0]])).xy]
                    end = [o for o in (camera_matrix_i @ Vector(verts[edge[1]])).xy]
                    coords = [start, end]
                    d = " ".join(
                        ["L{},{}".format((x_offset + p[0]) * svg_scale, (y_offset - p[1]) * svg_scale) for p in coords]
                    )
                    d = "M{}".format(d[1:])
                    path = etree.SubElement(g, "{http://www.w3.org/2000/svg}path")
                    path.attrib["d"] = d
                group.append(g)

            bm.free()

    def generate_freestyle_linework(self, context: bpy.types.Context) -> str | None:
        if not ifcopenshell.util.element.get_pset(self.drawing, "EPset_Drawing", "HasLinework"):
            return
        svg_path = self.get_svg_path(cache_type="linework")
        if os.path.isfile(svg_path) and self.props.should_use_linework_cache:
            return svg_path

        context.scene.render.use_freestyle = True
        context.scene.svg_export.use_svg_export = True

        linesets = context.view_layer.freestyle_settings.linesets
        if len(linesets) == 1 and linesets[0].name == "LineSet":
            context.view_layer.freestyle_settings.crease_angle = radians(140)
            context.view_layer.freestyle_settings.use_culling = True
            lineset = linesets[0]
            lineset.edge_type_negation = "EXCLUSIVE"
            lineset.select_silhouette = False
            lineset.select_crease = False
            lineset.select_border = False
            lineset.select_edge_mark = False
            lineset.select_contour = False
            lineset.select_external_contour = False
            lineset.select_material_boundary = False
            lineset.select_suggestive_contour = True
            lineset.select_ridge_valley = True

        edge_mesh = bpy.data.meshes.new("Temp Merged Edges")
        edge_obj = bpy.data.objects.new("Temp Merged Edges", edge_mesh)
        context.scene.collection.objects.link(edge_obj)
        edge_bm = bmesh.new()

        visible_object_names = {obj.name for obj in bpy.context.visible_objects}
        for obj in bpy.context.view_layer.objects:
            is_visible = obj.name in visible_object_names
            obj.hide_render = not is_visible
            if (
                is_visible
                and obj.type == "MESH"
                and len(obj.data.edges)
                and not len(obj.data.polygons)
                and not obj.name.startswith("IfcAnnotation")
            ):
                tmp_mesh = None
                try:
                    tmp_mesh = obj.data.copy()
                    tmp_mesh.transform(obj.matrix_world)
                    edge_bm.from_mesh(tmp_mesh)
                finally:
                    if tmp_mesh:
                        bpy.data.meshes.remove(tmp_mesh)

        ret = bmesh.ops.extrude_edge_only(edge_bm, edges=edge_bm.edges)
        verts_extruded = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]

        cam_z = self.camera.matrix_world.to_3x3() @ self.camera.data.view_frame(scene=None)[-1].normalized()
        cam_z *= 0.001

        for v in verts_extruded:
            v.co += cam_z

        edge_bm.to_mesh(edge_mesh)
        edge_bm.free()

        freestyle_svg_exporter = tool.Blender.get_addon("freestyle_svg_exporter")
        context.scene.render.filepath = svg_path[0:-4]
        actual_path = freestyle_svg_exporter.create_path(bpy.context.scene)
        bpy.ops.render.render(write_still=False)

        os.replace(actual_path, svg_path)

        bpy.data.objects.remove(edge_obj)
        bpy.data.meshes.remove(edge_mesh)

        context.scene.render.use_freestyle = False
        context.scene.svg_export.use_svg_export = False

        tree = etree.parse(svg_path)
        root = tree.getroot()

        freestyle_width = float(root.attrib["width"])
        freestyle_height = float(root.attrib["height"])
        svg_width = self.svg_writer.width
        svg_height = self.svg_writer.height

        group = root.find(".//{http://www.w3.org/2000/svg}g")
        group.attrib["class"] = "projection"

        # Resize Freestyle to our proper width / height and purge all other attributes
        for path in root.findall(".//{http://www.w3.org/2000/svg}path"):
            for key in path.attrib:
                if key == "fill":
                    continue
                elif key != "d":
                    del path.attrib[key]
                    continue
                d = path.attrib[key]
                coords = d.strip().split()[1:]
                new_d = "M"
                for i in range(0, len(coords), 2):
                    x = float(coords[i][:-1])
                    y = float(coords[i + 1])
                    x = x / freestyle_width * svg_width
                    y = y / freestyle_height * svg_height
                    new_d += f" {x},{y}"
                path.attrib["d"] = new_d
            pass

        if tool.Drawing.is_camera_orthographic():
            self.generate_bisect_linework(context, root)
            if self.cprops.generate_material_layers:
                self.generate_material_layers(context, root)
            self.merge_linework_and_add_metadata(root)
            self.move_elements_to_top(root)

        with open(svg_path, "wb") as svg:
            svg.write(etree.tostring(root))

        return svg_path

    def generate_linework(self, context: bpy.types.Context) -> Union[str, None]:
        if not ifcopenshell.util.element.get_pset(self.drawing, "EPset_Drawing", "HasLinework"):
            return
        svg_path = self.get_svg_path(cache_type="linework")
        if os.path.isfile(svg_path) and self.props.should_use_linework_cache:
            return svg_path

        # in case of printing multiple drawings we need to sync just once
        if self.sync and self.drawing_index == 0:
            with profile("sync"):
                # All very hackish whilst prototyping
                exporter = bonsai.bim.export_ifc.IfcExporter(None)
                exporter.file = tool.Ifc.get()
                invalidated_elements = exporter.sync_all_objects()
                invalidated_guids = [e.GlobalId for e in invalidated_elements if hasattr(e, "GlobalId")]
                if cache := IfcStore.get_cache():
                    [cache.remove(guid) for guid in invalidated_guids]

        # If we have already calculated it in the SVG in the past, don't recalculate
        edited_guids = set()
        for obj in IfcStore.edited_objs:
            element = tool.Ifc.get_entity(obj)
            edited_guids.add(element.GlobalId) if hasattr(element, "GlobalId") else None
        cached_linework = set()
        if os.path.isfile(svg_path):
            tree = etree.parse(svg_path)
            root = tree.getroot()
            cached_linework = {
                el.get("{http://www.ifcopenshell.org/ns}guid")
                for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]")
            }
        cached_linework -= edited_guids

        bim_props = tool.Blender.get_bim_props()
        prefs = tool.Blender.get_addon_preferences()
        files = {bim_props.ifc_file: tool.Ifc.get()}

        props = tool.Project.get_project_props()
        for link in props.get_loaded_links_for_drawings():
            files[link.filepath] = self.get_linked_file(link)

        target_view = ifcopenshell.util.element.get_psets(self.camera_element)["EPset_Drawing"]["TargetView"]
        self.setup_serialiser(target_view)

        tree = ifcopenshell.geom.tree()
        tree.enable_face_styles(True)

        for ifc_path, ifc in files.items():
            # Don't use draw.main() just whilst we're prototyping and experimenting
            # TODO: hash paths are never used
            ifc_hash = hashlib.md5(ifc_path.encode("utf-8")).hexdigest()
            ifc_cache_path = os.path.join(prefs.cache_dir, f"{ifc_hash}.h5")

            self.serialiser.setFile(ifc)
            drawing_elements = tool.Drawing.get_drawing_elements(self.camera_element, ifc_file=ifc)

            # Get all representation contexts to see what we're dealing with.
            # Drawings only draw bodies and annotations (and facetation, due to a Revit bug).
            # A drawing prioritises a target view context first, followed by a model view context as a fallback.
            # Specifically for PLAN_VIEW and REFLECTED_PLAN_VIEW, any Plan context is also prioritised.
            contexts = self.get_linework_contexts(ifc, target_view)
            self.serialize_contexts_elements(ifc, tree, contexts, "body", drawing_elements, target_view)
            self.serialize_contexts_elements(ifc, tree, contexts, "annotation", drawing_elements, target_view)

            if tool.Ifc.get() == ifc and self.camera_element not in drawing_elements:
                with profile("Camera element"):
                    # The camera must always be included, regardless of any include/exclude filters.
                    geom_settings = ifcopenshell.geom.settings()
                    geom_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)
                    it = ifcopenshell.geom.iterator(geom_settings, ifc, include=[self.camera_element])
                    for elem in it:
                        self.serialiser.write(elem)

        with profile("Finalizing"):
            self.serialiser.finalize()
        results = self.svg_buffer.get_value()

        root = etree.fromstring(results)

        group = root.find("{http://www.w3.org/2000/svg}g")
        if group is None:
            with open(svg_path, "wb") as svg:
                svg.write(etree.tostring(root))

            return svg_path

        # Add target_view and scale classes to the parent group from IFC data
        if group is not None:
            existing_classes = group.get("class", "").split()

            # Add target_view class
            if hasattr(self, "cprops") and getattr(self.cprops, "target_view", None):
                target_view_class = tool.Drawing.canonicalise_class_name(str(self.cprops.target_view))
                target_view_full_class = f"target-view-{target_view_class}"
                if target_view_full_class not in existing_classes:
                    existing_classes.append(target_view_full_class)

            # Add scale class from EPset_Drawing.Scale
            drawing_pset = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing")
            if drawing_pset and drawing_pset.get("Scale"):
                scale_value = drawing_pset["Scale"]
                # Remove "1/" prefix if it exists
                if isinstance(scale_value, str) and scale_value.startswith("1/"):
                    scale_value = scale_value[2:]
                scale_class = tool.Drawing.canonicalise_class_name(str(scale_value))
                scale_full_class = f"scale-{scale_class}"
                if scale_full_class not in existing_classes:
                    existing_classes.append(scale_full_class)

            group.set("class", " ".join(existing_classes))

        if self.cprops.cut_mode == "BISECT":
            self.remove_cut_linework(root)
            self.generate_bisect_linework(context, root)
            if self.cprops.generate_material_layers:
                self.generate_material_layers(context, root)
            self.merge_linework_and_add_metadata(root)
            self.move_elements_to_top(root)
        elif self.cprops.cut_mode == "OPENCASCADE":
            self.move_projection_to_bottom(root)
            if self.cprops.generate_material_layers:
                self.generate_material_layers(context, root)
            self.merge_linework_and_add_metadata(root)
            self.move_elements_to_top(root)

        if self.cprops.fill_mode == "SHAPELY":
            # shapely variant
            group = root.find("{http://www.w3.org/2000/svg}g")

            raycast_objs = set()
            elements_with_faces = set()
            for element in drawing_elements.copy():
                if element.is_a("IfcAnnotation"):
                    continue
                obj = tool.Ifc.get_object(element)
                if obj and obj.type == "MESH" and len(obj.data.polygons):
                    elements_with_faces.add(element.GlobalId)
                    raycast_objs.add(obj)

            projections = root.xpath(
                ".//svg:g[contains(@class, 'projection')]", namespaces={"svg": "http://www.w3.org/2000/svg"}
            )

            boundary_lines = []
            for projection in projections:
                global_id = projection.attrib["{http://www.ifcopenshell.org/ns}guid"]
                if global_id not in elements_with_faces:
                    continue
                for path in projection.findall("./{http://www.w3.org/2000/svg}path"):
                    start, end = [[float(o) for o in co[1:].split(",")] for co in path.attrib["d"].split()]
                    if start == end:
                        continue
                    # Extension by 0.5mm is necessary to ensure lines overlap with other diagonal lines
                    start, end = tool.Drawing.extend_line(start, end, 0.5)
                    boundary_lines.append(shapely.LineString([start, end]))

            unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
            closed_polygons = shapely.polygonize(unioned_boundaries.geoms)

            for polygon in closed_polygons.geoms:
                # Less than 0.1mm2 is not worth styling on sheet
                if polygon.area < 0.1:
                    continue
                centroid = polygon.centroid
                centroid = centroid if polygon.contains(centroid) else polygon.representative_point()
                if centroid:
                    centroid3d = self.drawing_to_model_co(centroid.x, centroid.y)
                    inside_elements = [
                        e for e in tree.select(self.pythonize(centroid3d)) if not e.is_a("IfcAnnotation")
                    ]
                    if not inside_elements:
                        camera_dir = self.camera.matrix_world.col[2].to_3d() * -1
                        # We previously used tree.select_ray, but raycasting in Blender is 100x faster.
                        raycast_results = self.cast_rays_and_get_best_object(raycast_objs, centroid3d, camera_dir)
                        raycast_element = None
                        if raycast_obj := raycast_results[0]:
                            raycast_element = tool.Ifc.get_entity(raycast_obj)

                        if raycast_element:
                            path = etree.Element("path")
                            d = (
                                "M"
                                + " L".join([",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]])
                                + " Z"
                            )
                            for interior in polygon.interiors:
                                d += (
                                    " M"
                                    + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]])
                                    + " Z"
                                )
                            path.attrib["d"] = d
                            classes = self.get_svg_classes(raycast_element)
                            classes.append("surface")
                            path.set("class", " ".join(list(classes)))
                            group.insert(0, path)

        if self.cprops.fill_mode == "SVGFILL":
            results = etree.tostring(root).decode("utf8")
            svg_data_1 = results
            from xml.dom.minidom import parseString

            def yield_groups(n):
                if n.nodeType == n.ELEMENT_NODE and n.tagName == "g":
                    yield n
                for c in n.childNodes:
                    yield from yield_groups(c)

            dom1 = parseString(svg_data_1)
            svg1 = dom1.childNodes[0]
            groups1 = [g for g in yield_groups(svg1) if "projection" in g.getAttribute("class")]

            ls_groups = ifcopenshell.ifcopenshell_wrapper.svg_to_line_segments(results, "projection")

            for i, (ls, g1) in enumerate(zip(ls_groups, groups1)):
                projection, g1 = g1, g1.parentNode

                svgfill_context = ifcopenshell.ifcopenshell_wrapper.context(
                    ifcopenshell.ifcopenshell_wrapper.EXACT_CONSTRUCTIONS, 1.0e-3
                )

                # EXACT_CONSTRUCTIONS is significantly faster than FILTERED_CARTESIAN_QUOTIENT
                # remove duplicates (without tolerance)
                ls = [l for l in map(tuple, set(map(frozenset, ls))) if len(l) == 2 and l[0] != l[1]]
                svgfill_context.add(ls)

                num_passes = 0

                for iteration in range(num_passes + 1):
                    # initialize empty group, note that in the current approach only one
                    # group is stored
                    ps = ifcopenshell.ifcopenshell_wrapper.svg_groups_of_polygons()
                    if iteration != 0 or svgfill_context.build():
                        svgfill_context.write(ps)

                    if iteration != num_passes:
                        pairs = svgfill_context.get_face_pairs()
                        semantics = [None] * (max(pairs) + 1)

                    # Reserialize cells into an SVG string
                    svg_data_2 = ifcopenshell.ifcopenshell_wrapper.polygons_to_svg(ps, True)

                    # We parse both SVG files to create on document with the combination of sections from
                    # the output directly from the serializer and the cells found from the hidden line
                    # rendering
                    dom2 = parseString(svg_data_2)
                    svg2 = dom2.childNodes[0]
                    # file 2 only has the groups we are interested in.
                    # in fact in the approach, it's only a single group

                    g2 = next(yield_groups(svg2))

                    # Loop over the cell paths
                    for pi, p in enumerate(g2.getElementsByTagName("path")):
                        d = p.getAttribute("d")
                        coords = [co[1:].split(",") for co in d.split() if co[1:]]
                        polygon = shapely.Polygon(coords)
                        # 1mm2 polygons aren't worth styling in paperspace. Raycasting is expensive!
                        if polygon.area < 1:
                            continue
                        # point inside is an attribute that comes from line_segments_to_polygons() polygons_to_svg?
                        # it is an arbitrary point guaranteed to be inside the polygon and outside
                        # of any potential inner bounds. We can use this to construct a ray to find
                        # the face of the IFC element that the cell belongs to.
                        assert p.hasAttribute("ifc:pointInside")

                        xy = list(map(float, p.getAttribute("ifc:pointInside").split(",")))

                        centroid3d = self.drawing_to_model_co(*xy)

                        inside_elements = [
                            e for e in tree.select(self.pythonize(centroid3d)) if not e.is_a("IfcAnnotation")
                        ]
                        if inside_elements:
                            elements = None
                            if iteration != num_passes:
                                semantics[pi] = (inside_elements[0], -1)
                        else:
                            camera_dir = self.camera.matrix_world.col[2].to_3d() * -1
                            elements = [
                                e
                                for e in tree.select_ray(self.pythonize(centroid3d), self.pythonize(camera_dir))
                                if not e.instance.is_a("IfcAnnotation")
                            ]

                        if elements:
                            classes = self.get_svg_classes(ifc.by_id(elements[0].instance.id()))
                            classes.append("projection")
                            classes.append("surface")

                            if iteration != num_passes:
                                semantics[pi] = elements[0]
                        else:
                            classes = ["projection"]

                        p.setAttribute("style", "foo")
                        p.setAttribute("class", " ".join(classes))

                    if iteration != num_passes:
                        to_remove = []

                        for he_idx in range(0, len(pairs), 2):
                            # @todo instead of ray_distance, better do (x.point - y.point).dot(x.normal)
                            # to see if they're coplanar, because ray-distance will be different in case
                            # of element surfaces non-orthogonal to the view direction

                            def format(x):
                                if x is None:
                                    return None
                                elif isinstance(x, tuple):
                                    # found to be inside element using tree.select() no face or style info
                                    return x
                                else:
                                    return (x.instance.is_a(), x.ray_distance, tuple(x.position))

                            pp = pairs[he_idx : he_idx + 2]
                            if pp == (-1, -1):
                                continue
                            data = list(map(format, map(semantics.__getitem__, pp)))
                            if None not in data and data[0][0] == data[1][0] and abs(data[0][1] - data[1][1]) < 1.0e-5:
                                to_remove.append(he_idx // 2)
                                # Print edge index and semantic data
                                # print(he_idx // 2, *data)

                        svgfill_context.merge(to_remove)

                # Swap the XML nodes from the files
                # Remove the original hidden line node we still have in the serializer output
                g1.removeChild(projection)
                g2.setAttribute("class", "projection")
                # Find the children of the projection node parent
                children = [x for x in g1.childNodes if x.nodeType == x.ELEMENT_NODE]
                if children:
                    # Insert the new semantically enriched cell-based projection node
                    # *before* the node with sections from the serializer. SVG derives
                    # draw order from node order in the DOM so sections are draw over
                    # the projections.
                    g1.insertBefore(g2, children[0])
                else:
                    # This generally shouldn't happen
                    g1.appendChild(g2)

            results = dom1.toxml()
            results = results.encode("ascii", "xmlcharrefreplace")
            root = etree.fromstring(results)

        # Spaces are handled as a special case, since they are often overlayed
        # in addition to elements. For example, a space should not obscure
        # other elements in projection. Spaces should also not override cut
        # elements but instead be drawn in addition to cut elements.
        spaces = tool.Drawing.get_drawing_spaces(self.camera_element)

        group = root.findall(".//{http://www.w3.org/2000/svg}g")[0]

        x_offset = self.svg_writer.raw_width / 2
        y_offset = self.svg_writer.raw_height / 2

        for space in spaces:
            obj = tool.Ifc.get_object(space)
            if not obj or not tool.Drawing.is_intersecting_camera(obj, self.camera):
                continue
            verts, edges = tool.Drawing.bisect_mesh(obj, self.camera)
            verts = [self.svg_writer.project_point_onto_camera(Vector(v)) for v in verts]
            line_strings = [
                shapely.LineString(
                    [
                        (
                            (x_offset + verts[e[0]][0]) * self.svg_writer.svg_scale,
                            (y_offset - verts[e[0]][1]) * self.svg_writer.svg_scale,
                        ),
                        (
                            (x_offset + verts[e[1]][0]) * self.svg_writer.svg_scale,
                            (y_offset - verts[e[1]][1]) * self.svg_writer.svg_scale,
                        ),
                    ]
                )
                for e in edges
            ]
            closed_polygons = shapely.polygonize(line_strings)
            for polygon in closed_polygons.geoms:
                classes = self.get_svg_classes(space)
                path = etree.Element("path")
                d = "M" + " L".join([",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]]) + " Z"
                for interior in polygon.interiors:
                    d += " M" + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]]) + " Z"
                path.attrib["d"] = d
                path.set("class", " ".join(list(classes)))
                group.append(path)

        with open(svg_path, "wb") as svg:
            svg.write(etree.tostring(root))

        return svg_path

    def setup_serialiser(self, target_view):
        self.svg_settings = ifcopenshell.geom.settings()
        self.svg_settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        self.svg_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)
        self.svg_buffer = ifcopenshell.geom.serializers.buffer()
        self.serialiser_settings = ifcopenshell.geom.serializer_settings()
        self.serialiser = ifcopenshell.geom.serializers.svg(
            self.svg_buffer, self.svg_settings, self.serialiser_settings
        )
        self.serialiser.setWithoutStoreys(True)
        self.serialiser.setPolygonal(True)
        self.serialiser.setUseHlrPoly(True)
        # Objects with more than these edges are rendered as wireframe instead of HLR for optimisation
        self.serialiser.setProfileThreshold(10000)
        self.serialiser.setUseNamespace(True)
        self.serialiser.setAlwaysProject(True)
        self.serialiser.setAutoElevation(False)
        self.serialiser.setAutoSection(False)
        self.serialiser.setPrintSpaceNames(False)
        self.serialiser.setPrintSpaceAreas(False)
        self.serialiser.setDrawDoorArcs(False)
        self.serialiser.setNoCSS(True)
        self.serialiser.setElevationRefGuid(self.camera_element.GlobalId)
        self.serialiser.setScale(self.scale)
        self.serialiser.setSubtractionSettings(ifcopenshell.ifcopenshell_wrapper.ALWAYS)
        self.serialiser.setUsePrefiltering(True)  # See #3359
        self.serialiser.setUnifyInputs(True)
        self.serialiser.setSegmentProjection(True)
        if target_view == "REFLECTED_PLAN_VIEW":
            self.serialiser.setMirrorY(True)
        # tree = ifcopenshell.geom.tree()
        # This instructs the tree to explode BReps into faces and return
        # the style of the face when running tree.select_ray()
        # tree.enable_face_styles(True)

    def get_svg_classes(self, element, layer=None):
        classes = [element.is_a()]

        # ─── Material ──────────────────────────────────────────────
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        material_name = ""
        if material:
            if material.is_a("IfcMaterialLayerSet"):
                material_name = material.LayerSetName or "null"
            else:
                material_name = getattr(material, "Name", "null") or "null"
            material_name = tool.Drawing.canonicalise_class_name(material_name)
            classes.append(f"material-{material_name}")
        else:
            classes.append("material-null")

        # ─── Layer ─────────────────────────────────────────────────
        if layer:
            classes.append(layer.is_a())
            layer_material = layer.Material
            layer_material_name = layer_material.Name or "null"
            layer_material_name = tool.Drawing.canonicalise_class_name(layer_material_name)
            classes.append(f"layer-material-{layer_material_name}")

            # Add material category if available
            if hasattr(layer_material, "Category") and layer_material.Category:
                layer_material_category = tool.Drawing.canonicalise_class_name(layer_material.Category)
                classes.append(f"layer-material-category-{layer_material_category}")

        # ─── Metadata ──────────────────────────────────────────────
        for key in self.metadata:
            value = ifcopenshell.util.selector.get_element_value(element, key)
            if value:
                classes.append(
                    tool.Drawing.canonicalise_class_name(key) + "-" + tool.Drawing.canonicalise_class_name(str(value))
                )

        return classes

    def is_manifold(self, obj) -> bool:
        result = self.is_manifold_cache.get(obj.data.name, None)
        if result is not None:
            return result

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.000001)
        for edge in bm.edges:
            if not edge.is_manifold:
                bm.free()
                self.is_manifold_cache[obj.data.name] = False
                return False
        self.is_manifold_cache[obj.data.name] = True
        return True

    def get_linked_file(self, link: "Link") -> ifcopenshell.file:
        link_path = link.filepath
        ifc_file = IfcStore.session_files.get(link_path, None)
        if ifc_file is not None:
            return ifc_file
        resolved_path = tool.Ifc.resolve_uri(link_path)
        ifc_file = IfcStore.session_files[link_path] = ifcopenshell.open(resolved_path)
        return ifc_file

    def get_element_by_guid(self, guid: str) -> Union[ifcopenshell.entity_instance, None]:
        try:
            return tool.Ifc.get().by_guid(guid)
        except RuntimeError:
            props = tool.Project.get_project_props()
            for link in props.get_loaded_links_for_drawings():
                ifc_file = self.get_linked_file(link)
                try:
                    return ifc_file.by_guid(guid)
                except RuntimeError:
                    continue

    def get_element_by_id(self, step_id: Any) -> Union[ifcopenshell.entity_instance, None]:
        try:
            step_id = int(step_id)
        except:
            return
        try:
            return tool.Ifc.get().by_id(step_id)
        except RuntimeError:
            props = tool.Project.get_project_props()
            for link in props.get_loaded_links_for_drawings():
                ifc_file = self.get_linked_file(link)
                try:
                    return ifc_file.by_id(step_id)
                except RuntimeError:
                    continue

    def remove_cut_linework(self, root):
        for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]"):
            if "projection" not in el.get("class", "").split():
                el.getparent().remove(el)

    def merge_linework_and_add_metadata(self, root):
        join_criteria = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "JoinCriteria")
        if join_criteria:
            join_criteria = join_criteria.split(",")
        else:
            # Drawing convention states that same objects classes with the same material are merged when cut.
            join_criteria = [
                "class",
                "material.Name",
                "/Pset_.*Common/.Status",
                "EPset_Status.Status",
                "EPset_Status.UserDefinedStatus",
                "Material.Name",
            ]

        group = root.find("{http://www.w3.org/2000/svg}g")
        joined_paths = {}
        self.is_manifold_cache = {}

        for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]"):
            element = self.get_element_by_guid(el.get("{http://www.ifcopenshell.org/ns}guid"))
            layer = self.get_element_by_id(el.get("{http://www.ifcopenshell.org/ns}layer-id"))

            if "projection" in el.get("class", "").split():
                classes = self.get_svg_classes(element)
                classes.append("projection")
                el.set("class", " ".join(classes))
                continue
            else:
                classes = self.get_svg_classes(element, layer)
                classes.append("cut")
                el.set("class", " ".join(classes))

            obj = tool.Ifc.get_object(element)

            if not obj:  # This is a linked model object. For now, do nothing.
                continue

            if (material := ifcopenshell.util.element.get_material(element)) and material.is_a() in (
                "IfcMaterialLayerSet",
                "IfcMaterialLayerSetUsage",
            ):
                pass  # These are always manifold
            elif not self.is_manifold(obj):
                continue

            # An element group will contain a bunch of paths representing the
            # cut of that element. However IfcOpenShell may not correctly
            # create closed paths. We post-process all paths with shapely to
            # ensure things that should be closed (i.e.
            # shapely.polygonize_full) are, and things which aren't are left
            # alone (e.g. dangles, cuts, invalids). See #3421.
            line_strings = []
            old_paths = []
            has_open_paths = False
            for path in el.findall("{http://www.w3.org/2000/svg}path"):
                for subpath in path.attrib["d"].split("M")[1:]:
                    subpath = "M" + subpath.strip()
                    coords = [[float(o) for o in co[1:].split(",")] for co in subpath.split()]
                    if coords[0] != coords[-1]:
                        has_open_paths = True
                    line_strings.append(shapely.LineString(coords))
                old_paths.append(path)

            results = []
            if has_open_paths:
                unioned_line_strings = shapely.union_all(shapely.GeometryCollection(line_strings))
                if hasattr(unioned_line_strings, "geoms"):
                    results = shapely.polygonize_full(unioned_line_strings.geoms)

            # If we succeeded in generating new path geometry, remove all the
            # old paths and add new ones.
            if results:
                for path in old_paths:
                    path.getparent().remove(path)

            # polygonize_full will create polygons for everything, including
            # interior "holes". As a result we do two passes. The first pass
            # records polygon interior rings. The second pass uses this to
            # check if the exterior ring matches an interior ring. If it does,
            # it's a hole. Skip it!

            interior_hashes = set()
            for result in results:
                for geom in result.geoms:
                    if isinstance(geom, shapely.Polygon):
                        for interior in geom.interiors:
                            # Sorted because coordinate ordering may differ,
                            # and frozenset because shapely sometimes emits
                            # duplicate coordinates.
                            interior_hashes.add(hash(frozenset(sorted(interior.coords))))
                    elif isinstance(geom, shapely.LineString):
                        path = etree.SubElement(el, "{http://www.w3.org/2000/svg}path")
                        d = "M" + " L".join([",".join([str(o) for o in co]) for co in geom.coords]) + " Z"
                        path.attrib["d"] = d

            for result in results:
                for geom in result.geoms:
                    if isinstance(geom, shapely.Polygon):
                        path = etree.SubElement(el, "{http://www.w3.org/2000/svg}path")
                        if hash(frozenset(sorted(geom.exterior.coords))) in interior_hashes:
                            # This is a "hole", as its exterior perfectly matches an interior.
                            continue
                        d = (
                            "M"
                            + " L".join([",".join([str(o) for o in co]) for co in geom.exterior.coords[0:-1]])
                            + " Z"
                        )
                        for interior in geom.interiors:
                            d += (
                                " M"
                                + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]])
                                + " Z"
                            )
                        path.attrib["d"] = d

            # Architectural convention only merges these objects. E.g. pipe segments and fittings shouldn't merge.
            if not element.is_a("IfcWall") and not element.is_a("IfcSlab"):
                continue

            keys = []
            for query in join_criteria:
                key = ifcopenshell.util.selector.get_element_value(element, query)
                if isinstance(key, (list, tuple)):
                    keys.extend(key)
                else:
                    keys.append(key)

            if layer:
                for query in join_criteria:
                    key = ifcopenshell.util.selector.get_element_value(layer, query)
                    if isinstance(key, (list, tuple)):
                        keys.extend(key)
                    else:
                        keys.append(key)

            hash_keys = hash(tuple(keys))

            if el.findall("{http://www.w3.org/2000/svg}path"):
                joined_paths.setdefault(hash_keys, []).append(el)

        for key, els in joined_paths.items():
            queue = []

            for el in els:
                classes = set(el.attrib["class"].split())
                classes.add(el.attrib["{http://www.ifcopenshell.org/ns}guid"])
                is_closed_polygon = False
                for path in el.findall("{http://www.w3.org/2000/svg}path"):
                    # Temporary hack.
                    if "d" not in path.attrib:
                        continue
                    for subpath in path.attrib["d"].split("M")[1:]:
                        subpath_co = "M" + subpath.strip(" Z")
                        # Round due to inaccuracies from Blender meshes and bisection
                        coords = [[round(float(o), 3) for o in co[1:].split(",")] for co in subpath_co.split()]
                        if subpath.strip().lower().endswith("z"):
                            coords.append(coords[0])
                        if len(coords) > 2 and coords[0] == coords[-1]:
                            is_closed_polygon = True
                            queue.append((shapely.Polygon(coords), classes))
                if is_closed_polygon:
                    el.getparent().remove(el)

            while queue:
                polygon, polygon_classes = queue.pop()
                for polygon2, polygon2_classes in queue[:]:
                    try:
                        merged_polygon = shapely.union(polygon, polygon2)
                    except:
                        print("Warning. Portions of the merge failed. Please report a bug!", polygon, polygon2)
                        continue
                    if type(merged_polygon) == shapely.Polygon:
                        polygon = merged_polygon
                        polygon_classes.update(polygon2_classes)
                        queue.remove((polygon2, polygon2_classes))

                g = etree.Element("g")
                path = etree.SubElement(g, "path")
                d = "M" + " L".join([",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]]) + " Z"
                for interior in polygon.interiors:
                    d += " M" + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]]) + " Z"
                path.attrib["d"] = d
                g.set("class", " ".join(list(polygon_classes)))
                group.append(g)

    def drawing_to_model_co(self, x: float, y: float) -> Vector:
        camera_xy = np.array((x, -y)) / self.scale / 1000
        camera_xy += np.array((self.cprops.width / -2, self.cprops.height / 2))  # top left offset
        return self.camera.matrix_world @ Vector(camera_xy).to_3d()

    def pythonize(self, arr):
        return tuple(map(float, arr))

    def cast_rays_and_get_best_object(
        self, objs_to_raycast: list[bpy.types.Object], ray_origin, ray_direction
    ) -> Union[tuple[bpy.types.Object, Vector, int], tuple[None, None, None]]:
        # This could be optimised even further with 2D box culling
        best_length_squared = 1.0
        best_obj = None
        best_hit = None
        best_face_index = None

        for obj in objs_to_raycast:
            matrix_inv = obj.matrix_world.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_direction_obj = ray_direction.to_4d()
            ray_direction_obj[3] = 0.0
            ray_direction_obj = (matrix_inv @ ray_direction_obj).to_3d()

            success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

            if success:
                hit = obj.matrix_world @ location
                length_squared = (hit - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = obj
                    best_hit = hit
                    best_face_index = face_index

        if best_obj is not None:
            return best_obj, best_hit, best_face_index
        return None, None, None

    def move_projection_to_bottom(self, root):
        # IfcConvert puts the projection afterwards which is not correct since
        # projection should be drawn underneath the cut.
        group = root.find("{http://www.w3.org/2000/svg}g")
        projections = root.xpath(
            ".//svg:g[contains(@class, 'projection')]", namespaces={"svg": "http://www.w3.org/2000/svg"}
        )
        for projection in projections:
            projection.getparent().remove(projection)
            group.insert(0, projection)

    def move_elements_to_top(self, root):
        group = root.find("{http://www.w3.org/2000/svg}g")
        bringtofront = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "BringToFront") or ""
        bringtofront = [item.strip() for item in bringtofront.split(",") if item.strip()]

        # Iterate through classes in order of preference
        for class_name in bringtofront:
            xpath_query = f".//svg:g[contains(@class, '{class_name}')]"
            elements_to_move = root.xpath(xpath_query, namespaces={"svg": "http://www.w3.org/2000/svg"})

            # Move each element to the end of the group (effectively placing them at the top visually)
            for element in elements_to_move:
                element.getparent().remove(element)
                group.append(element)

    def generate_annotation(self, context: bpy.types.Context) -> Union[str, None]:
        if not ifcopenshell.util.element.get_pset(self.drawing, "EPset_Drawing", "HasAnnotation"):
            return
        svg_path = self.get_svg_path(cache_type="annotation")
        if os.path.isfile(svg_path) and self.props.should_use_annotation_cache:
            return svg_path

        elements = tool.Drawing.get_group_elements(tool.Drawing.get_drawing_group(self.camera_element))
        filtered_drawing_elements = tool.Drawing.get_drawing_elements(self.camera_element)
        filtered_drawing_annotations = {e for e in filtered_drawing_elements if e.is_a("IfcAnnotation")}
        elements = {e for e in elements if e in filtered_drawing_elements}
        elements = list(elements | filtered_drawing_annotations)

        annotations = sorted(
            elements,
            key=lambda a: (
                tool.Drawing.get_annotation_z_index(a),
                1 if ifcopenshell.util.element.get_predefined_type(a) == "TEXT" else 0,
            ),
        )

        precision = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "MetricPrecision")
        if not precision:
            precision = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "ImperialPrecision")

        decimal_places = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "DecimalPlaces")
        self.svg_writer.metadata = self.metadata
        self.svg_writer.create_blank_svg(svg_path).draw_annotations(annotations, precision, decimal_places).save()

        return svg_path

    def get_scale(self, context):
        diagram_scale = tool.Drawing.get_diagram_scale(self.camera)
        self.human_scale = diagram_scale["HumanScale"]
        self.scale = tool.Drawing.get_scale_ratio(diagram_scale["Scale"])

        if ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "IsNTS"):
            self.human_scale = "NTS"

    def is_landscape(self, render):
        return render.resolution_x > render.resolution_y

    def get_material_name(self, element: ifcopenshell.entity_instance) -> str:
        if hasattr(element, "Name") and element.Name:
            return element.Name
        elif hasattr(element, "LayerSetName") and element.LayerSetName:
            return element.LayerSetName
        return "mat-" + str(element.id())

    def get_svg_path(self, cache_type: Optional[str] = None) -> str:
        drawing_path = tool.Drawing.get_document_uri(self.camera_document)
        assert drawing_path
        drawings_dir = os.path.dirname(drawing_path)

        if cache_type:
            drawings_dir = os.path.join(drawings_dir, "cache")
            os.makedirs(drawings_dir, exist_ok=True)
            filename = tool.Drawing.sanitise_filename(f"{self.drawing_name}-{cache_type}.svg")
            return os.path.join(drawings_dir, filename)
        os.makedirs(drawings_dir, exist_ok=True)
        return drawing_path


def _get_drawing_enum_items(self, context):
    items = [("0", "None", "Clear the drawing assignment")]
    if ifc := tool.Ifc.get():
        for d in ifc.by_type("IfcAnnotation"):
            if d.ObjectType == "DRAWING":
                items.append((str(d.id()), d.Name or f"Drawing {d.id()}", ""))
    return items


def _get_reference_doc_enum_items(self, context):
    items = [("0", "None", "Clear the reference assignment")]
    if ifc := tool.Ifc.get():
        for d in ifc.by_type("IfcDocumentInformation"):
            if d.Scope == "REFERENCE":
                items.append((str(d.id()), d.Name or f"Reference {d.id()}", ""))
    return items


class AddAnnotation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_annotation"
    bl_label = "Add Annotation"
    bl_options = {"REGISTER", "UNDO"}
    description: bpy.props.StringProperty()
    drawing_id: bpy.props.EnumProperty(name="Drawing", items=_get_drawing_enum_items)
    reference_doc_id: bpy.props.EnumProperty(name="Reference", items=_get_reference_doc_enum_items)
    is_document_reference: bpy.props.BoolProperty(name="External Reference", default=False)
    # Used only when placing via the legacy MANUAL_DRAWING_REFERENCE dropdown type.
    manual_style: bpy.props.EnumProperty(
        name="Style",
        items=[
            ("ELEVATION", "Elevation", "Use the elevation tag visual (circle with arrow)"),
            ("SECTION", "Section", "Use the section tag visual (line with end circles)"),
        ],
        default="ELEVATION",
    )

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.scene.camera

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def invoke(self, context, event):
        props = tool.Drawing.get_annotation_props()
        needs_dialog = (
            (props.is_manual_reference and props.object_type in ("ELEVATION", "SECTION"))
            or props.object_type == "MANUAL_DRAWING_REFERENCE"
        )
        if needs_dialog:
            self.drawing_id = "0"
            self.reference_doc_id = "0"
            self.is_document_reference = False
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        props = tool.Drawing.get_annotation_props()
        if props.object_type == "MANUAL_DRAWING_REFERENCE":
            self.layout.prop(self, "manual_style", expand=True)
        self.layout.prop(self, "is_document_reference")
        if self.is_document_reference:
            prop_with_search(self.layout, self, "reference_doc_id", should_click_ok=True, search_threshold=0, original_operator_path=f"{__name__}.AddAnnotation")
        else:
            prop_with_search(self.layout, self, "drawing_id", should_click_ok=True, search_threshold=0, original_operator_path=f"{__name__}.AddAnnotation")

    def _execute(self, context):
        props = tool.Drawing.get_annotation_props()
        dprops = tool.Drawing.get_document_props()
        if not (drawing := dprops.get_active_drawing()):
            self.report({"WARNING"}, "No active drawing.")
            return

        # MANUAL_DRAWING_REFERENCE is a legacy/convenience dropdown entry; resolve
        # it to the chosen style so create_annotation_object knows what to build.
        if props.object_type == "MANUAL_DRAWING_REFERENCE":
            object_type = self.manual_style
            is_manual = True
        else:
            object_type = props.object_type
            is_manual = props.is_manual_reference and object_type in ("ELEVATION", "SECTION")

        obj = core.add_annotation(
            tool.Ifc,
            tool.Collector,
            tool.Drawing,
            drawing=drawing,
            object_type=object_type,
            relating_type=tool.Ifc.get().by_id(int(props.relating_type_id)) if props.relating_type_id != "0" else None,
            # ELEVATION/SECTION annotations use simple empty/line geometry that
            # cannot be tessellated by the IFC geometry engine, so skip IFC
            # item edit mode for these types.
            enable_editing=object_type not in ("ELEVATION", "SECTION"),
        )
        if object_type == "IMAGE":
            bpy.ops.bim.add_reference_image("INVOKE_DEFAULT", existing_object_by_name=obj.name)
        if is_manual:
            element = tool.Ifc.get_entity(obj)
            tool.Drawing.set_manual_drawing_reference(element)
            if self.is_document_reference:
                tool.Drawing.set_document_reference_flag(element)
                if self.reference_doc_id != "0":
                    core.assign_manual_reference_document(
                        tool.Drawing, element=element, document=tool.Ifc.get().by_id(int(self.reference_doc_id))
                    )
            elif self.drawing_id != "0":
                core.assign_manual_drawing_reference(
                    tool.Ifc, tool.Drawing, element=element, drawing=tool.Ifc.get().by_id(int(self.drawing_id))
                )


class AssignManualDrawingReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_manual_drawing_reference"
    bl_label = "Assign Drawing"
    bl_description = "Assign a target drawing or reference to this manual drawing reference tag"
    bl_options = {"REGISTER", "UNDO"}
    drawing_id: bpy.props.EnumProperty(name="Drawing", items=_get_drawing_enum_items)
    reference_doc_id: bpy.props.EnumProperty(name="Reference", items=_get_reference_doc_enum_items)

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not context.active_object:
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element or not element.is_a("IfcAnnotation"):
            return False
        if element.ObjectType not in ("ELEVATION", "SECTION"):
            cls.poll_message_set("Active object is not an elevation or section annotation.")
            return False
        if not ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "IsManualDrawingReference"):
            cls.poll_message_set("Active object is not a manual drawing reference.")
            return False
        return True

    def invoke(self, context, event):
        element = tool.Ifc.get_entity(context.active_object)
        if tool.Drawing.is_document_reference(element):
            doc = tool.Drawing.get_annotation_reference_doc(element)
            self.reference_doc_id = str(doc.id()) if doc else "0"
        else:
            current = tool.Drawing.get_annotation_element(element)
            self.drawing_id = str(current.id()) if current else "0"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element and tool.Drawing.is_document_reference(element):
            prop_with_search(self.layout, self, "reference_doc_id", search_threshold=0, original_operator_path=f"{__name__}.AssignManualDrawingReference")
        else:
            prop_with_search(self.layout, self, "drawing_id", search_threshold=0, original_operator_path=f"{__name__}.AssignManualDrawingReference")

    def _execute(self, context):
        element = tool.Ifc.get_entity(context.active_object)
        if tool.Drawing.is_document_reference(element):
            document = tool.Ifc.get().by_id(int(self.reference_doc_id)) if self.reference_doc_id != "0" else None
            core.assign_manual_reference_document(tool.Drawing, element=element, document=document)
        else:
            drawing = tool.Ifc.get().by_id(int(self.drawing_id)) if self.drawing_id != "0" else None
            core.assign_manual_drawing_reference(tool.Ifc, tool.Drawing, element=element, drawing=drawing)
        for area in context.screen.areas:
            if area.type == "PROPERTIES":
                area.tag_redraw()


class AddSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_sheet"
    bl_label = "Add Sheet"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a sheet to the project"

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        core.add_sheet(tool.Ifc, tool.Drawing, titleblock=props.titleblock)


class DuplicateSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_sheet"
    bl_label = "Duplicate Sheet"
    bl_description = "Make a copy of currently selected sheet"
    bl_options = {"REGISTER", "UNDO"}
    drawing: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        # Unconditionally disable until implemented
        cls.poll_message_set("Not implemented yet.")
        return False

        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_drawing_item():
            cls.poll_message_set("No drawing selected.")
            return False
        return True

    def _execute(self, context):
        pass
        """
        self.props = tool.Drawing.get_document_props()
        core.duplicate_sheet(
            tool.Ifc,
            tool.Drawing,
            sheet=tool.Ifc.get().by_id(self.sheet),
        )
        try:
            sheet = tool.Ifc.get().by_id(self.props.active_sheet_id)
            core.sync_references(tool.Ifc, tool.Collector, tool.Sheet, drawing=sheet)
        except:
            pass
        """


class OpenLayout(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.open_layout"
    bl_label = "Open Sheet Layout"
    bl_description = (
        "Opens selected .svg layout with default system viewer\n"
        + 'or using "layout_svg_command" from the Bonsai preferences\n'
        + "(if provided)"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = tool.Drawing.get_document_props()
        sheet_item = tool.Drawing.get_active_sheet_item()
        assert sheet_item
        sheet = tool.Ifc.get().by_id(sheet_item.ifc_definition_id)
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.update_sheet_drawing_sizes(sheet)
        core.open_layout(tool.Drawing, sheet=sheet)


class SelectAllSheets(bpy.types.Operator):
    bl_idname = "bim.select_all_sheets"
    bl_label = "Select All Sheets"
    view: bpy.props.StringProperty()
    bl_description = "Select all sheets in the sheet list.\n\n" + "SHIFT+CLICK to deselect all sheets"
    select_all: bpy.props.BoolProperty(name="Open All", default=True, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # deselect all sheets on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.select_all = False
        return self.execute(context)

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        for sheet in props.sheets:
            if sheet.is_selected != self.select_all:
                sheet.is_selected = self.select_all
        return {"FINISHED"}


class OpenSheet(bpy.types.Operator):
    bl_idname = "bim.open_sheet"
    bl_label = "Open Sheet"
    bl_description = (
        "Opens selected sheet with default system viewer\n"
        + 'or using "svg_command" or "pdf_command" from\n'
        + "the Bonsai preferences (if provided).\n\n"
        + "SHIFT+CLICK to open all shown checked sheets"
    )
    bl_options = {"REGISTER", "UNDO"}
    open_all: bpy.props.BoolProperty(name="Open All", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_sheet_item(is_sheet=True):
            cls.poll_message_set("No sheet selected.")
            return False
        return True

    def invoke(self, context, event):
        # opening all sheets on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.open_all = True
        return self.execute(context)

    def execute(self, context):
        self.props = tool.Drawing.get_document_props()
        svg2pdf_command = tool.Blender.get_addon_preferences().svg2pdf_command

        if self.open_all:
            sheets = [
                tool.Ifc.get().by_id(s.ifc_definition_id) for s in self.props.sheets if s.is_sheet and s.is_selected
            ]
        else:
            sheet_item = tool.Drawing.get_active_sheet_item()
            assert sheet_item
            sheets = [tool.Ifc.get().by_id(sheet_item.ifc_definition_id)]

        sheet_uris: list[str] = []
        sheets_not_found: list[str] = []
        warnings: list[tool.Drawing.SheetWarningType] = []

        for sheet in sheets:
            if not sheet.is_a("IfcDocumentInformation"):
                continue
            warnings.extend(sheets_warnings := tool.Drawing.validate_sheet_files(sheet))
            if sheets_warnings:
                continue
            sheet_builder = sheeter.SheetBuilder()
            references = sheet_builder.build(sheet)
            sheet_uri = references["SHEET"]
            if svg2pdf_command:
                sheet_uri = os.path.splitext(sheet_uri)[0] + ".pdf"
            sheet_uris.append(sheet_uri)
            if not os.path.exists(sheet_uri):
                sheets_not_found.append(sheet.Name)

        if warnings:
            self.report({"ERROR"}, f"There were errors opening sheets. See system console for the details.")
            print("-" * 10)
            print("\n".join(str(w) for w in warnings))

        if sheets_not_found:
            msg = "Some sheets .svg/.pdf files were not found, need to create them first: \n{}.".format(
                "\n".join(sheets_not_found)
            )
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        for sheet_uri in sheet_uris:
            if svg2pdf_command:
                tool.Drawing.open_with_user_command(tool.Blender.get_addon_preferences().pdf_command, sheet_uri)
            else:
                tool.Drawing.open_with_user_command(tool.Blender.get_addon_preferences().svg_command, sheet_uri)
        return {"FINISHED"}


class AddDrawingToSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_drawing_to_sheet"
    bl_label = "Add Selected Drawing To Sheet"
    bl_description = "Add the drawing selected in the\nDrawings list below to the sheet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_drawing_item():
            cls.poll_message_set("No drawing selected.")
            return False
        if not props.sheets:
            cls.poll_message_set("No sheets available.")
            return False
        if not tool.Blender.get_user_data_dir():
            cls.poll_message_set("BIM data directory not set.")
            return False
        return True

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        active_drawing = props.drawings[props.active_drawing_index]
        assert active_drawing
        ifc_file = tool.Ifc.get()

        active_sheet = tool.Drawing.get_active_sheet()
        drawing = tool.Ifc.get().by_id(active_drawing.ifc_definition_id)
        drawing_reference = tool.Drawing.get_drawing_document(drawing)

        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return

        references = tool.Drawing.get_document_references(sheet)

        has_drawing = False
        for reference in references:
            if reference.Location == drawing_reference.Location:
                has_drawing = True
                break
        if has_drawing:
            return

        if not tool.Drawing.does_file_exist(tool.Drawing.get_document_uri(drawing_reference)):
            self.report({"ERROR"}, "The drawing must be generated before adding to a sheet.")
            return

        reference = ifcopenshell.api.document.add_reference(ifc_file, information=sheet)
        attributes = tool.Drawing.generate_reference_attributes(
            reference,
            Identification=str(
                len(
                    [
                        r
                        for r in references
                        if tool.Drawing.get_reference_description(r) in ("DRAWING", "SCHEDULE", "REFERENCE")
                    ]
                )
                + 1
            ),
            Location=drawing_reference.Location,
            Description="DRAWING",
        )
        ifcopenshell.api.document.edit_reference(ifc_file, reference=reference, attributes=attributes)
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.add_drawing(reference, drawing, sheet)

        tool.Drawing.import_sheets()


class RemoveDrawingFromSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_drawing_from_sheet"
    bl_label = "Remove Drawing From Sheet"
    bl_description = "Remove currently selected drawing from sheet"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        active_item = tool.Drawing.get_active_sheet_item()
        if active_item is None:
            return False

        if active_item.reference_type == "TITLEBLOCK":
            cls.poll_message_set("No effect deleting titleblock reference.")
            return False
        return True

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        tool.Drawing.remove_drawing_from_sheet(ifc_file.by_id(self.reference))


class CreateSheets(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.create_sheets"
    bl_label = "Create Sheets"
    bl_description = (
        "Build and open selected sheet from the sheet layout and\n"
        + "optionally create .pdf and .dxf from commands in\n"
        + "the Bonsai preferences (if provided).\n\n"
        + "SHIFT+CLICK to create all shown checked sheets, but doesn't\n"
        + "open them for viewing\n\n"
        + "Add the CTRL modifier to optionally open sheets to view them as\n"
        + "they are created"
    )
    bl_options = {"REGISTER", "UNDO"}

    create_all: bpy.props.BoolProperty(name="Create All", default=False, options={"SKIP_SAVE"})
    open_viewer: bpy.props.BoolProperty(name="Open in Viewer", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_sheet_item(is_sheet=True):
            cls.poll_message_set("No sheet selected.")
            return False
        prefs = tool.Blender.get_addon_preferences()
        return props.sheets and prefs.data_dir

    def invoke(self, context, event):
        # opening all sheets on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.create_all = True
        if event.type == "LEFTMOUSE" and event.ctrl:
            self.open_viewer = True
        return self.execute(context)

    def _execute(self, context):
        scene = context.scene
        props = tool.Drawing.get_document_props()
        svg2pdf_command = tool.Blender.get_addon_preferences().svg2pdf_command
        svg2dxf_command = tool.Blender.get_addon_preferences().svg2dxf_command
        ifc_file = tool.Ifc.get()

        if self.create_all:
            sheets = [tool.Ifc.get().by_id(s.ifc_definition_id) for s in props.sheets if s.is_sheet and s.is_selected]
        else:
            sheet_item = tool.Drawing.get_active_sheet_item()
            assert sheet_item
            sheets = [tool.Ifc.get().by_id(sheet_item.ifc_definition_id)]

        warnings: list[tool.Drawing.SheetWarningType] = []
        n_sheets_created = 0
        for sheet in sheets:

            warnings.extend(sheet_warnings := tool.Drawing.validate_sheet_files(sheet))
            if sheet_warnings:
                continue

            # Update any drawing boundary changes
            sheet_builder = sheeter.SheetBuilder()
            sheet_builder.update_sheet_drawing_sizes(sheet)

            if not sheet.is_a("IfcDocumentInformation"):
                return

            name = os.path.splitext(os.path.basename(tool.Drawing.get_document_uri(sheet)))[0]
            sheet_builder = sheeter.SheetBuilder()

            references = sheet_builder.build(sheet)

            # These variables will be made available to the evaluated commands
            svg = references["SHEET"]
            pdf = os.path.splitext(svg)[0] + ".pdf"
            replacements = {
                "svg": svg,
                "basename": os.path.basename(svg),
                "path": os.path.dirname(svg),
                "pdf": pdf,
                "eps": os.path.splitext(svg)[0] + ".eps",
                "dxf": os.path.splitext(svg)[0] + ".dxf",
            }

            has_sheet_reference = False
            for reference in tool.Drawing.get_document_references(sheet):
                reference_description = tool.Drawing.get_reference_description(reference)
                if reference_description == "SHEET":
                    has_sheet_reference = True

            if not has_sheet_reference:
                reference = ifcopenshell.api.document.add_reference(ifc_file, information=sheet)
                ifcopenshell.api.document.edit_reference(
                    ifc_file,
                    reference=reference,
                    attributes=tool.Drawing.generate_reference_attributes(
                        reference, Location=tool.Ifc.get_uri(svg, use_relative_path=True), Description="SHEET"
                    ),
                )

            if svg2pdf_command:
                # With great power comes great responsibility. Example:
                # [["inkscape", "svg", "-o", "pdf"]]
                commands = json.loads(svg2pdf_command)
                for command in commands:
                    subprocess.run([replacements.get(c, c) for c in command])

            if svg2dxf_command:
                # With great power comes great responsibility. Example:
                # [["inkscape", "svg", "-o", "eps"], ["pstoedit", "-dt", "-f", "dxf:-polyaslines -mm", "eps", "dxf", "-psarg", "-dNOSAFER"]]
                commands = json.loads(svg2dxf_command)
                for command in commands:
                    command[0] = shutil.which(command[0]) or command[0]
                    subprocess.run([replacements.get(c, c) for c in command])

            if self.open_viewer:
                if svg2pdf_command:
                    tool.Drawing.open_with_user_command(tool.Blender.get_addon_preferences().pdf_command, pdf)
                else:
                    tool.Drawing.open_with_user_command(tool.Blender.get_addon_preferences().svg_command, svg)

            n_sheets_created += 1

        if not self.open_viewer:
            self.report({"INFO"}, f"{n_sheets_created} sheets created...")

        if warnings:
            self.report({"ERROR"}, f"There were errors creating sheets. See system console for the details.")
            print("-" * 10)
            print("\n".join(str(w) for w in warnings))


class SelectAllDrawings(bpy.types.Operator):
    bl_idname = "bim.select_all_drawings"
    bl_label = "Select All Drawings"
    view: bpy.props.StringProperty()
    bl_description = "Select all drawings in the drawing list.\n\n" + "SHIFT+CLICK to deselect all drawings"
    select_all: bpy.props.BoolProperty(name="Open All", default=True, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # deselect all drawings on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.select_all = False
        return self.execute(context)

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        for drawing in props.drawings:
            if drawing.is_selected != self.select_all:
                drawing.is_selected = self.select_all
        return {"FINISHED"}


class OpenDrawing(bpy.types.Operator):
    bl_idname = "bim.open_drawing"
    bl_label = "Open Drawing"
    view: bpy.props.StringProperty()
    bl_description = (
        "Opens selected .svg drawing with default system viewer\n"
        + 'or using "svg_command" from the Bonsai preferences (if provided).\n\n'
        + "SHIFT+CLICK to open all shown checked drawings"
    )
    open_all: bpy.props.BoolProperty(name="Open All", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_drawing_item():
            cls.poll_message_set("No drawing selected.")
            return False
        return True

    def invoke(self, context, event):
        # opening all drawings on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.open_all = True
        return self.execute(context)

    def execute(self, context):
        self.props = tool.Drawing.get_document_props()
        if self.open_all:
            drawings = [
                tool.Ifc.get().by_id(d.ifc_definition_id) for d in self.props.drawings if d.is_drawing and d.is_selected
            ]
        else:
            drawings = [tool.Ifc.get().by_id(self.props.drawings.get(self.view).ifc_definition_id)]

        drawing_uris = []
        drawings_not_found = []

        for drawing in drawings:
            drawing_uri = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_document(drawing))
            drawing_uris.append(drawing_uri)
            if not os.path.exists(drawing_uri):
                drawings_not_found.append(drawing.Name)

        if drawings_not_found:
            msg = "Some drawings .svg files were not found, need to create them first: \n{}.".format(
                "\n".join(drawings_not_found)
            )
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        for drawing_uri in drawing_uris:
            tool.Drawing.open_with_user_command(tool.Blender.get_addon_preferences().svg_command, drawing_uri)
        return {"FINISHED"}


class ActivateModel(bpy.types.Operator):
    bl_idname = "bim.activate_model"
    bl_label = "Activate Model"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Activate the model view.\n\n"
        "Show all objects (and apply status filters if they were enabled before) and hide all annotations."
    )

    def execute(self, context):
        start_time = time.time()

        dprops = tool.Drawing.get_document_props()
        dprops.active_drawing_id = 0
        model_props = tool.Model.get_model_props()
        if model_props.show_cut_decorator:
            CutDecorator.uninstall()

        ifc_file = tool.Ifc.get()

        if not bpy.app.background:
            with context.temp_override(**tool.Blender.get_viewport_context()):
                bpy.ops.bim.activate_status_filters(only_if_enabled=True)

        elements = {e for obj in context.visible_objects if (e := tool.Ifc.get_entity(obj))}

        def refine_elements(
            elements_mutable: set[ifcopenshell.entity_instance],
        ) -> dict[ifcopenshell.entity_instance, tuple[ifcopenshell.entity_instance, bpy.types.Object]]:
            """
            :return: element -> (representation, obj)
            """
            # TODO: in the future reimport_element_representations should have an option
            # not recalculate elements completely, but get the from cache, to speed up the process further.
            refined_elements: dict[
                ifcopenshell.entity_instance, tuple[ifcopenshell.entity_instance, bpy.types.Object]
            ] = {}
            elements = elements_mutable
            while elements:
                element = elements.pop()
                model = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
                if not model:
                    continue
                assert isinstance(obj := tool.Ifc.get_object(element), bpy.types.Object)
                current_representation = tool.Geometry.get_active_representation(obj)
                if current_representation == model:
                    continue

                # reimport_element_representations automatically reloads all elements sharing representation.
                # So we should avoid reloading same elements twice.
                resolved_model = ifcopenshell.util.representation.resolve_representation(model)
                elements_sharing_representation = ifcopenshell.util.element.get_elements_by_representation(
                    ifc_file, resolved_model
                )

                refined_elements[element] = (model, obj)
                elements = elements - elements_sharing_representation
            return refined_elements

        refined_elements = refine_elements(elements)
        for _, (model, obj) in refined_elements.items():
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=model,
            )

        tool.Blender.reset_object_visibility()
        tool.Drawing.hide_all_drawing_collections()
        tool.Blender.update_viewport()
        bonsai.bim.handler.refresh_ui_data()

        operator_time = time.time() - start_time
        if operator_time > 10:
            self.report({"INFO"}, f"{self.bl_label} was finished in {operator_time:.2f} seconds.")

        return {"FINISHED"}


class ActivateDrawingBase(tool.Ifc.Operator):
    # Ifc Operator is necessary, because sync_references may create or remove IFC elements.
    bl_label = "Activate Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Activates the selected drawing view.\n\n"
        + "ALT+CLICK to keep the viewport position.\n\n"
        + "SHIFT+CLICK to load a quick preview of the drawing view"
    )

    drawing: bpy.props.IntProperty()
    should_view_from_camera: bpy.props.BoolProperty(
        name="Should View From Camera",
        description="Move view to the activated drawing's camera position.",
        default=True,
        options={"SKIP_SAVE"},
    )
    use_quick_preview: bpy.props.BoolProperty(
        name="Use Quick Preview",
        description="Just move the camera to the drawing view, without loading anything else.",
        default=False,
        options={"SKIP_SAVE"},
    )

    if TYPE_CHECKING:
        drawing: int
        should_view_from_camera: bool
        use_quick_preview: bool

    def invoke(self, context, event) -> set["rna_enums.OperatorReturnItems"]:
        if event.type == "LEFTMOUSE" and event.alt:
            self.should_view_from_camera = False
        if event.type == "LEFTMOUSE" and event.shift:
            self.use_quick_preview = True
        return self.execute(context)

    def _execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        assert context.scene
        props = tool.Drawing.get_document_props()
        if props.is_editing_drawings == False:
            bpy.ops.bim.load_drawings()

        drawing = tool.Ifc.get().by_id(self.drawing)
        dprops = tool.Drawing.get_document_props()

        if self.use_quick_preview:
            tool.Blender.activate_camera(tool.Drawing.import_temporary_drawing_camera(drawing))
            return {"FINISHED"}

        viewport_position = None

        v3d_space = tool.Blender.get_view3d_space()
        assert v3d_space
        if self.should_view_from_camera:
            # Since we must switch to drawing camera, undo local camera in viewport.
            # The code is needed to undo `else` branch from activating other cameras.
            v3d_space.use_local_camera = False
        else:
            # Since we use `scene.camera` to store active drawing,
            # the only way to preserve previous drawing camera position is making it local.
            r3d = v3d_space.region_3d
            assert r3d
            if r3d.view_perspective == "CAMERA":
                if v3d_space.use_local_camera:
                    # Nothing to do, local camera is already set by user.
                    pass
                else:
                    previous_camera = context.scene.camera
                    if previous_camera:
                        v3d_space.camera = previous_camera
                        v3d_space.use_local_camera = True
            else:
                viewport_position = tool.Blender.get_viewport_position()

        core.activate_drawing_view(tool.Ifc, tool.Blender, tool.Drawing, drawing=drawing)

        if not self.should_view_from_camera:
            if viewport_position is None:
                # Local camera takes priority over active scene camera,
                # so nothing to do after drawing view activation.
                pass
            else:
                tool.Blender.set_viewport_position(viewport_position)

        dprops.active_drawing_id = self.drawing
        dprops.drawing_styles.clear()
        bpy.ops.bim.reload_drawing_styles()
        bpy.ops.bim.activate_drawing_style()

        if tool.Drawing.is_camera_orthographic():
            core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=tool.Ifc.get().by_id(self.drawing))
        model_props = tool.Model.get_model_props()
        if model_props.show_cut_decorator:
            CutDecorator.install(context)
        tool.Drawing.show_decorations()

        # Save drawing bounds to the .ifc file
        camera = context.scene.camera
        assert camera
        camera_props = tool.Drawing.get_camera_props(camera)
        # Check if this is a reflected ceiling camera and preserve its scale
        camera_element = tool.Ifc.get_entity(camera)
        is_reflected = False
        if camera_element:
            is_reflected = (
                ifcopenshell.util.element.get_pset(camera_element, "EPset_Drawing", "TargetView")
                == "REFLECTED_PLAN_VIEW"
            )
            if is_reflected and camera.scale != (-1, -1, -1):
                camera.scale = (-1, -1, -1)

        if camera_props.update_representation(camera.matrix_world):
            bpy.ops.bim.update_representation(obj=camera.name, ifc_representation_class="")
            # Restore the scale after update if needed
            if is_reflected:
                camera.scale = (-1, -1, -1)

        return {"FINISHED"}


class ActivateDrawing(bpy.types.Operator, ActivateDrawingBase):
    bl_idname = "bim.activate_drawing"
    bl_label = "Activate Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Activates the selected drawing view.\n\n"
        + "ALT+CLICK to keep the viewport position.\n\n"
        + "SHIFT+CLICK to load a quick preview of the drawing view"
    )


class ActivateDrawingFromSheet(bpy.types.Operator, ActivateDrawingBase):
    bl_idname = "bim.activate_drawing_from_sheet"
    bl_label = "Activate Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Activates the selected drawing view.\n\n"
        + "ALT+CLICK to keep the viewport position.\n\n"
        + "SHIFT+CLICK to load a quick preview of the drawing view"
    )

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_sheet_item(reference_type="DRAWING"):
            cls.poll_message_set("No drawing selected.")
            return False
        return True


class RemoveDrawing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_drawing"
    bl_label = "Remove Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove currently selected drawing.\n\n" + "SHIFT+CLICK to remove all selected drawings"

    drawing: bpy.props.IntProperty()
    remove_all: bpy.props.BoolProperty(name="Remove All", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        if not tool.Drawing.get_active_drawing_item():
            cls.poll_message_set("No drawing selected.")
            return False
        return True

    def invoke(self, context, event):
        # removing all selected drawings on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.remove_all = True
        return self.execute(context)

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        if self.remove_all:
            drawings = [
                tool.Ifc.get().by_id(d.ifc_definition_id) for d in props.drawings if d.is_drawing and d.is_selected
            ]
        else:
            if not self.drawing:
                self.report({"ERROR"}, "No drawing selected")
                return {"CANCELLED"}
            drawings = [tool.Ifc.get().by_id(self.drawing)]

        for drawing in drawings:
            sheet_references = tool.Drawing.get_sheet_references(drawing)
            for reference in sheet_references:
                tool.Drawing.remove_drawing_from_sheet(reference)
            core.remove_drawing(tool.Ifc, tool.Drawing, drawing=drawing)

        # In case we removed the active drawing.
        if not context.scene.camera and props.should_draw_decorations:
            props.should_draw_decorations = False


class DrawingStyleJson(TypedDict):
    render_type: "RenderType"
    raster_style: dict[str, Any]


class ReloadDrawingStyles(bpy.types.Operator):
    bl_idname = "bim.reload_drawing_styles"
    bl_label = "Reload Drawing Styles"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reload drawing styles for the active camera from the related JSON file."

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        assert (drawing := props.get_active_drawing())
        drawing_pset_data = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")

        assert context.scene and (camera := context.scene.camera)
        camera_props = tool.Drawing.get_camera_props(camera)

        if "ShadingStyles" not in drawing_pset_data:
            self.report({"ERROR"}, "Could not find shading styles path in EPset_Drawing.ShadingStyles.")
            return {"CANCELLED"}

        rel_path = drawing_pset_data["ShadingStyles"]
        current_style = drawing_pset_data.get("CurrentShadingStyle", None)

        json_path = Path(tool.Ifc.resolve_uri(rel_path))
        if not json_path.exists():
            ootb_resource = tool.Blender.get_data_dir_path(Path("assets") / "shading_styles.json")
            print(
                f"WARNING. Couldn't find shading_styles for the drawing by the path: {json_path}. "
                f"Default BBIM resource will be copied from {ootb_resource}"
            )
            if ootb_resource.exists():
                os.makedirs(json_path.parent, exist_ok=True)
                shutil.copy(ootb_resource, json_path)

        with open(json_path, "r") as fi:
            shading_styles_json: dict[str, DrawingStyleJson] = json.load(fi)

        drawing_styles = props.drawing_styles
        drawing_styles.clear()
        styles = [style for style in shading_styles_json]
        for style_name in styles:
            style_data = shading_styles_json[style_name]
            drawing_style = drawing_styles.add()
            drawing_style["name"] = style_name  # setting as attribute to avoid triggering setter
            drawing_style.render_type = style_data["render_type"]
            drawing_style.raster_style = json.dumps(style_data["raster_style"])

        if current_style is not None:
            if current_style not in styles:
                self.report({"WARNING"}, f"Could not find style {current_style} in EPset_Drawing.ShadingStyles.")
            else:
                camera_props.active_drawing_style_index = styles.index(current_style)
        return {"FINISHED"}


# NOTE: Ifc Operator is not necessary for add and remove,
# as underlying save operator creates ifc undo step for us,
# but we keep it to make it more safe in case operators composition will change.
class AddDrawingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_drawing_style"
    bl_label = "Add Drawing Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        assert context.scene and (camera_obj := context.scene.camera)
        props = tool.Drawing.get_document_props()
        drawing_styles = props.drawing_styles
        new = drawing_styles.add()
        # drawing style is saved to ifc on rename
        new.name = tool.Blender.ensure_unique_name("New Drawing Style", drawing_styles)
        camera_props = tool.Drawing.get_camera_props(camera_obj)
        camera_props.active_drawing_style_index = len(drawing_styles) - 1
        return {"FINISHED"}


class RemoveDrawingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_drawing_style"
    bl_label = "Remove Drawing Style"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def _execute(self, context):
        assert context.scene and (camera_obj := context.scene.camera)
        props = tool.Drawing.get_document_props()
        props.drawing_styles.remove(self.index)
        camera_props = tool.Drawing.get_camera_props(camera_obj)
        camera_props.active_drawing_style_index = max(self.index - 1, 0)
        bpy.ops.bim.save_drawing_styles_data()
        return {"FINISHED"}


class SaveDrawingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_drawing_style"
    bl_label = "Save Drawing Style"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Save current render settings to currently selected drawing style. Also resaves styles data to IFC"

    index: bpy.props.StringProperty()
    # TODO: check undo redo

    def _execute(self, context):
        assert (space := tool.Blender.get_view3d_space())  # Do not remove. It is used later in eval
        scene = context.scene
        assert scene
        style = {}
        eval_namespace = {"context": context, "scene": scene, "space": space}

        def add_prop_to_style(
            prop_path: str, context: bpy.types.Context, scene: bpy.types.Scene, space: bpy.types.SpaceView3D
        ) -> None:
            value = eval(prop_path)
            if not isinstance(value, str):
                try:
                    value = tuple(value)
                except TypeError:
                    pass
            style[prop_path] = value

        for prop in RasterStyleProperty:
            if prop.name.startswith("EVAL_PROP"):
                prop_path = prop.value
                add_prop_to_style(prop_path, **eval_namespace)
            else:
                props_source_path = prop.value
                props_source = eval(props_source_path)
                for prop_name in dir(props_source):
                    if prop_name.startswith("__"):
                        continue

                    prop_path = f"{props_source_path}.{prop_name}"
                    prop_value = eval(prop_path)
                    if (
                        not isinstance(prop_value, (int, float, bool, str, Color, Vector))
                        or props_source.is_property_readonly(prop_name)
                        or prop_path in RASTER_STYLE_PROPERTIES_EXCLUDE
                    ):
                        continue

                    add_prop_to_style(prop_path, **eval_namespace)

        if self.index:
            index = int(self.index)
        else:
            assert (camera := scene.camera)
            props = tool.Drawing.get_camera_props(camera)
            index = props.active_drawing_style_index
        props = tool.Drawing.get_document_props()
        props.drawing_styles[index].raster_style = json.dumps(style)

        bpy.ops.bim.save_drawing_styles_data()
        return {"FINISHED"}


# TODO: operator is not exposed to UI, move it to tool.
class SaveDrawingStylesData(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_drawing_styles_data"
    bl_label = "Save Drawing Styles Data"
    bl_description = "Save current drawing styles settings to IFC and JSON."
    bl_options = {"REGISTER", "UNDO"}

    skip_updating_current_style: bpy.props.BoolProperty(default=False)
    rename_style: bpy.props.BoolProperty(default=False)
    rename_style_from: bpy.props.StringProperty(default="")
    rename_style_to: bpy.props.StringProperty(default="")

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        assert (drawing := props.get_active_drawing())
        drawing_pset_data = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
        drawing_styles = props.drawing_styles

        rel_path = drawing_pset_data["ShadingStyles"]
        current_style = drawing_pset_data.get("CurrentShadingStyle", None)
        json_path = Path(tool.Ifc.resolve_uri(rel_path))
        if not json_path.exists():
            self.report({"ERROR"}, "Shading styles file not found: {}".format(json_path))
            return {"CANCELLED"}

        styles_data: dict[str, DrawingStyleJson] = {}
        for style in drawing_styles:
            styles_data[style.name] = {"render_type": style.render_type, "raster_style": json.loads(style.raster_style)}

        with open(json_path, "w") as fo:
            json.dump(styles_data, fo, indent=4)

        # TODO: currently it doesn't update current style for the other drawings
        # handling case when current style is not present in styles saved in ifc
        if not self.skip_updating_current_style and current_style not in styles_data and current_style is not None:
            # style was renamed
            if self.rename_style and current_style == self.rename_style_from:
                new_style_name = self.rename_style_to

            # style was removed
            else:
                new_style_name = None

            ifc_file = tool.Ifc.get()
            assert (drawing := props.get_active_drawing())
            pset = tool.Pset.get_element_pset(drawing, "EPset_Drawing")
            assert pset
            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"CurrentShadingStyle": new_style_name})
            bonsai.bim.handler.refresh_ui_data()

        return {"FINISHED"}


class ActivateDrawingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.activate_drawing_style"
    bl_label = "Activate Drawing Style"
    bl_options = {"REGISTER", "UNDO"}

    has_errors_during_activation = False
    has_warnings_during_activation = False

    def _execute(self, context):
        scene = context.scene
        assert scene and (camera := scene.camera)
        camera_props = tool.Drawing.get_camera_props(camera)
        ifc_file = tool.Ifc.get()

        drawing_style = camera_props.get_active_drawing_style()
        if drawing_style is None:
            self.report({"ERROR"}, "Could not find active drawing style")
            return {"CANCELLED"}
        self.drawing_style = drawing_style

        self.set_raster_style(context)

        props = tool.Drawing.get_document_props()
        assert (drawing := props.get_active_drawing())
        pset = tool.Pset.get_element_pset(drawing, "EPset_Drawing")
        assert pset
        ifcopenshell.api.pset.edit_pset(
            ifc_file, pset=pset, properties={"CurrentShadingStyle": self.drawing_style.name}
        )
        bonsai.bim.handler.refresh_ui_data()

        if self.has_warnings_during_activation:
            self.report(
                {"WARNING"},
                "There were warnings setting some drawing style properies, see system console for the details.",
            )
        if self.has_errors_during_activation:
            self.report(
                {"WARNING"},
                "There were errors setting some drawing style properies, see system console for the details.",
            )

        return {"FINISHED"}

    def set_raster_style(self, context: bpy.types.Context) -> None:
        scene = context.scene  # Do not remove. It is used in exec later
        assert (space := tool.Blender.get_view3d_space())  # Do not remove. It is used in exec later
        style: dict[str, Any] = json.loads(self.drawing_style.raster_style)

        VIEWPORT_SHADING_TYPE = "scene.display.shading.type"

        def preprocess(path: str, value: Any) -> tuple[str, Any, bool, bool]:
            warning = False
            skip = False

            BLENDER_5_REMOVED = (
                "scene.render.bake_bias",
                "scene.render.bake_margin",
                "scene.render.bake_margin_type",
                "scene.render.bake_samples",
                "scene.render.bake_type",
                "scene.render.bake_user_scale",
                "scene.render.use_bake_clear",
                "scene.render.use_bake_lores_mesh",
                "scene.render.use_bake_multires",
                "scene.render.use_bake_selected_to_active",
                "scene.render.use_bake_user_scale",
            )

            # 25.11.07, Blender 5+
            if path == "scene.render.engine" and value in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
                if value == "BLENDER_EEVEE_NEXT":
                    print(
                        f"Warning: Value 'BLENDER_EEVEE_NEXT' is outdated for property '{path}' "
                        "since Blender 5.0 and should be replaced with 'BLENDER_EEVEE' in shading_styles.json."
                    )
                    warning = True
                value = tool.Blender.get_eevee_name()
            elif tool.Blender.BLENDER_5 and path in BLENDER_5_REMOVED:
                print(
                    f"Warning: Property '{path}' is removed "
                    "since Blender 5.0 and should be also removed from shading_styles.json."
                )
                warning = True
                skip = True
            # @25.11.11
            elif (
                path == "scene.display.shading.studio_light"
                and value == "Default"
                and style[VIEWPORT_SHADING_TYPE] in ("RENDERED", "MATERIAL")
            ):
                value = "forest.exr"
                print(
                    f"Warning: Value 'Default' for property '{path}' and "
                    f"'{VIEWPORT_SHADING_TYPE}' = '{style[VIEWPORT_SHADING_TYPE]}' is outdated "
                    "and should be replaced with 'forest.exr' in shading_styles.json."
                )
                warning = True
            # @25.05.12
            elif path == "scene.display.shading.wireframe_color_type" and value == "MATERIAL":
                value = "THEME"
                print(
                    f"Warning: Value 'MATERIAL' is outdated for property '{path}' "
                    "since Blender 4.0 and should be replaced with 'THEME' in shading_styles.json."
                )
                warning = True
            # @25.05.12
            elif path in ("scene.render.simplify_shadows", "scene.render.simplify_shadows_render"):
                print(
                    f"Warning: Property '{path}' is removed "
                    "since Blender 4.2 and should be also removed from shading_styles.json."
                )
                warning = True
                skip = True
            # @25.05.12
            elif path in ("space.overlay.backwire_opacity", "space.overlay.show_edges"):
                print(
                    f"Warning: Property '{path}' is removed "
                    "since Blender 4.1 and should be also removed from shading_styles.json."
                )
                warning = True
                skip = True
            # @25.05.12
            elif path in ("space.overlay.show_occlude_wire",):
                print(
                    f"Warning: Property '{path}' is removed "
                    "since Blender 3.6 and should be also removed from shading_styles.json."
                )
                warning = True
                skip = True

            return path, value, warning, skip

        paths = list(style.keys())
        PRIORITY_PATHS = (
            # `scene.display.shading.studio_light` values depend on `.type`
            # so we got to set it first.
            VIEWPORT_SHADING_TYPE,
        )
        paths.sort(key=lambda p: p not in PRIORITY_PATHS)

        for path in paths:
            value = style[path]
            path, value, warning, skip = preprocess(path, value)
            self.has_warnings_during_activation |= warning

            if skip:
                continue

            try:
                if isinstance(value, str):
                    exec(f"{path} = '{value}'")
                else:
                    exec(f"{path} = {value}")
            except Exception as e:
                # Differences in Blender versions mean result in failures here
                print(f"Failed to set drawing style property '{path}' to '{value}'. Error: '{str(e)}'")
                self.has_errors_during_activation = True
                if "PYTEST_VERSION" in os.environ:
                    raise


class RemoveSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_sheet"
    bl_label = "Remove Sheet"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove currently selected sheet"
    sheet: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_sheet(tool.Ifc, tool.Drawing, sheet=tool.Ifc.get().by_id(self.sheet))


class AddSchedule(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.add_schedule"
    bl_label = "Add Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add an .ods, .xls or .xlsx file as a schedule"

    files: bpy.props.CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ods;*.xls;*.xlsx", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=True)

    def _execute(self, context):
        for filepath in tool.Blender.get_selected_files(
            self.directory, self.files, use_relative_path=self.use_relative_path
        ):
            core.add_document(tool.Ifc, tool.Drawing, "SCHEDULE", uri=filepath)


class RemoveSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_schedule"
    bl_label = "Remove Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the currently selected schedule"

    schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_document(tool.Ifc, tool.Drawing, "SCHEDULE", document=tool.Ifc.get().by_id(self.schedule))


class OpenSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.open_schedule"
    bl_label = "Open Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Open the currently selected schedule \nin the default system viewer"

    schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.open_schedule(tool.Drawing, schedule=tool.Ifc.get().by_id(self.schedule))


class BuildSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.build_schedule"
    bl_label = "Build Schedule"
    bl_description = "Create a .svg file of the selected schedule\nand open it with default system viewer"
    schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.build_schedule(tool.Drawing, schedule=tool.Ifc.get().by_id(self.schedule))


class AddScheduleToSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_schedule_to_sheet"
    bl_label = "Add Schedule To Sheet"
    bl_description = "Add the schedule selected in the\nSchedules list below to the sheet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not props.schedules:
            cls.poll_message_set("No schedule selected.")
            return False
        if not props.sheets:
            cls.poll_message_set("No sheets available.")
            return False
        if not tool.Blender.get_user_data_dir():
            cls.poll_message_set("BIM data directory not set.")
            return False
        return True

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        active_schedule = props.schedules[props.active_schedule_index]
        active_sheet = tool.Drawing.get_active_sheet()
        ifc_file = tool.Ifc.get()
        schedule = tool.Ifc.get().by_id(active_schedule.ifc_definition_id)
        if tool.Ifc.get_schema() == "IFC2X3":
            schedule_location = tool.Drawing.get_path_with_ext(schedule.DocumentReferences[0].Location, "svg")
        else:
            schedule_location = tool.Drawing.get_path_with_ext(schedule.HasDocumentReferences[0].Location, "svg")

        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return

        references = tool.Drawing.get_document_references(sheet)

        has_schedule = False
        for reference in references:
            if reference.Location == schedule_location:
                has_schedule = True
                break
        if has_schedule:
            return

        if not tool.Drawing.does_file_exist(tool.Ifc.resolve_uri(schedule_location)):
            self.report({"ERROR"}, "The schedule must be generated before adding to a sheet.")
            return

        reference = ifcopenshell.api.document.add_reference(ifc_file, information=sheet)
        attributes = tool.Drawing.generate_reference_attributes(
            reference,
            Identification=str(
                len(
                    [
                        r
                        for r in references
                        if tool.Drawing.get_reference_description(r) in ("DRAWING", "SCHEDULE", "REFERENCE")
                    ]
                )
                + 1
            ),
            Location=schedule_location,
            Description="SCHEDULE",
        )
        ifcopenshell.api.document.edit_reference(ifc_file, reference=reference, attributes=attributes)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.add_document(reference, schedule, sheet)

        tool.Drawing.import_sheets()


class AddReferenceToSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_reference_to_sheet"
    bl_label = "Add Reference To Sheet"
    bl_description = "Add the reference selected in the\nReferences list below to the sheet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not props.references:
            cls.poll_message_set("No reference selected.")
            return False
        if not props.sheets:
            cls.poll_message_set("No sheets available.")
            return False
        if not tool.Blender.get_user_data_dir():
            cls.poll_message_set("BIM data directory not set.")
            return False
        return True

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        active_reference = props.references[props.active_reference_index]
        active_sheet = tool.Drawing.get_active_sheet()
        ifc_file = tool.Ifc.get()
        extref = tool.Ifc.get().by_id(active_reference.ifc_definition_id)
        if tool.Ifc.get_schema() == "IFC2X3":
            extref_location = tool.Drawing.get_path_with_ext(extref.DocumentReferences[0].Location, "svg")
        else:
            extref_location = tool.Drawing.get_path_with_ext(extref.HasDocumentReferences[0].Location, "svg")

        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return

        references = tool.Drawing.get_document_references(sheet)

        has_extref = False
        for reference in references:
            if reference.Location == extref_location:
                has_extref = True
                break
        if has_extref:
            return

        if not tool.Drawing.does_file_exist(tool.Ifc.resolve_uri(extref_location)):
            self.report({"ERROR"}, f"Cannot find reference svg by path {extref_location}.")
            return

        reference = ifcopenshell.api.document.add_reference(ifc_file, information=sheet)
        attributes = tool.Drawing.generate_reference_attributes(
            reference,
            Identification=str(
                len(
                    [
                        r
                        for r in references
                        if tool.Drawing.get_reference_description(r) in ("DRAWING", "SCHEDULE", "REFERENCE")
                    ]
                )
                + 1
            ),
            Location=extref_location,
            Description="REFERENCE",
        )
        ifcopenshell.api.document.edit_reference(ifc_file, reference=reference, attributes=attributes)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.add_document(reference, extref, sheet)

        tool.Drawing.import_sheets()


class AddReference(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.add_reference"
    bl_label = "Add Reference"
    bl_description = "Import a .svg file to the project as a reference"
    bl_options = {"REGISTER", "UNDO"}

    files: bpy.props.CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_glob: bpy.props.StringProperty(default="*.svg", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=True)
    filename_ext = ".svg"

    def _execute(self, context):
        for filepath in tool.Blender.get_selected_files(
            self.directory, self.files, use_relative_path=self.use_relative_path
        ):
            core.add_document(tool.Ifc, tool.Drawing, "REFERENCE", uri=filepath)


class RemoveReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_reference"
    bl_label = "Remove Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the currently selected reference\nfrom the project"

    reference: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_document(tool.Ifc, tool.Drawing, "REFERENCE", document=tool.Ifc.get().by_id(self.reference))


class OpenReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.open_reference"
    bl_label = "Open Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Open the reference into default system viewer"

    reference: bpy.props.IntProperty()

    def _execute(self, context):
        core.open_reference(tool.Drawing, reference=tool.Ifc.get().by_id(self.reference))


class CleanWireframes(bpy.types.Operator):
    bl_idname = "bim.clean_wireframes"
    bl_label = "Clean Wireframes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.selected_objects:
            objects = context.selected_objects
        else:
            objects = context.scene.objects
        for obj in (o for o in objects if o.type == "MESH"):
            if "EDGE_SPLIT" not in (m.type for m in obj.modifiers):
                obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
        return {"FINISHED"}


class EditTextPopup(bpy.types.Operator):
    bl_idname = "bim.edit_text_popup"
    bl_label = "Edit Text"
    first_run: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        from bonsai.bim.module.drawing.ui import BIM_PT_text

        BIM_PT_text.draw_text_editing_ui(self, context, popup_mode=True)

    def cancel(self, context):
        # disable editing when dialog is closed
        bpy.ops.bim.disable_editing_text()

    def execute(self, context):
        # TODO: check for possible subtle undo bug here
        # can't use invoke() because this operator
        # will be run indirectly by hotkey
        # so we use execute() and track whether it's the first run of the operator
        if self.first_run:
            bpy.ops.bim.enable_editing_text()
            self.first_run = False
            return context.window_manager.invoke_props_dialog(self)
        else:
            bpy.ops.bim.edit_text()
            return {"FINISHED"}


class EditText(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_text"
    bl_label = "Edit Text"
    bl_description = "Save changes to the text annotation and\ndisable the text editing options"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_text(tool.Drawing, obj=tool.Blender.get_active_object())
        tool.Blender.update_viewport()


class CopyTextToSelection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_text_to_selection"
    bl_label = "Copy Text To Selection"
    bl_description = "Copy text formatting or literals to selected objects"
    bl_options = {"REGISTER", "UNDO"}
    attribute: bpy.props.StringProperty()

    def _execute(self, context):
        apply_objs = [
            obj
            for obj in tool.Blender.get_selected_objects()
            if (element := tool.Ifc.get_entity(obj))
            and tool.Drawing.is_annotation_object_type(element, ["TEXT", "TEXT_LEADER"])
        ]
        core.copy_text_to_selection(
            tool.Drawing,
            attribute=self.attribute,
            attribute_obj=tool.Blender.get_active_object(),
            apply_objs=apply_objs,
        )
        tool.Blender.update_viewport()


class EnableEditingText(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_text"
    bl_label = "Enable Editing Text"
    bl_description = "Enable the text editing options for this\ntext annotation"

    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        props = tool.Drawing.get_text_props(obj)
        core.enable_editing_text(tool.Drawing, obj=obj)

        text_element = tool.Ifc.get_entity(obj)
        assigned_product_entity = tool.Drawing.get_assigned_product(text_element) if text_element else None
        assigned_product_obj = tool.Ifc.get_object(assigned_product_entity) if assigned_product_entity else None

        if "_bonsai_element_value_rows_backup" in obj:
            try:
                literals_backup = json.loads(obj["_bonsai_element_value_rows_backup"])
                for i, literal_backup in enumerate(literals_backup):
                    if i < len(props.literals):
                        literal_props = props.literals[i]

                        if assigned_product_obj:
                            literal_props.product_used = assigned_product_obj
                        elif "product_used" in literal_backup and literal_backup["product_used"]:
                            product_name = literal_backup["product_used"]
                            if product_name in bpy.data.objects:
                                literal_props.product_used = bpy.data.objects[product_name]

                        literal_props.element_value_rows.clear()
                        if "element_value_rows" in literal_backup:
                            for row_data in literal_backup["element_value_rows"]:
                                new_row = literal_props.element_value_rows.add()
                                new_row.category = row_data.get("category", "")
                                new_row.element_key = row_data.get("element_key", "")
                                new_row.formatted_value = row_data.get("formatted_value", "")
                                new_row.separator = row_data.get("separator", "")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Failed to restore element_value_rows: {e}")
        else:
            if assigned_product_obj:
                for literal_props in props.literals:
                    literal_props.product_used = assigned_product_obj

        return {"FINISHED"}


class DisableEditingText(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_text"
    bl_label = "Disable Editing Text"
    bl_description = "Discard changes to the text annotation\nand disable the text editing options"

    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        core.disable_editing_text(tool.Drawing, obj=obj)

        # force update this object's font size for viewport display
        DecoratorData.data.pop(obj.name, None)
        tool.Blender.update_viewport()


class AddTextLiteral(bpy.types.Operator):
    bl_idname = "bim.add_text_literal"
    bl_label = "Add Text Literal"
    bl_description = "Add another text literal to the\ntext annotation"

    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        assert obj

        # similar to `tool.Drawing.import_text_attributes`
        props = tool.Drawing.get_text_props(obj)
        literal_props = props.literals.add()
        literal_attributes = literal_props.attributes
        literal_attr_values = {
            "Literal": "Literal",
            "Path": "RIGHT",
            "BoxAlignment": "bottom_left",
        }
        # emulates `bonsai.bim.helper.import_attributes(ifc_literal, literal_props.attributes)`
        for attr_name in literal_attr_values:
            attr = literal_attributes.add()
            attr.name = attr_name
            if attr_name == "Path":
                attr.data_type = "enum"
                attr.enum_items = '["DOWN", "LEFT", "RIGHT", "UP"]'
                attr.enum_value = literal_attr_values[attr_name]

            else:
                attr.data_type = "string"
                attr.string_value = literal_attr_values[attr_name]

        literal_props.align_vertical = "bottom"
        literal_props.align_horizontal = "left"
        return {"FINISHED"}


class RemoveTextLiteral(bpy.types.Operator):
    bl_idname = "bim.remove_text_literal"
    bl_label = "Remove Text Literal"
    bl_description = "Delete the text literal from the\ntext annotation"

    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Drawing.get_text_props(obj)
        props.literals.remove(self.literal_prop_id)
        tool.Blender.update_viewport()
        return {"FINISHED"}


class OrderTextLiteralUp(bpy.types.Operator):
    bl_idname = "bim.order_text_literal_up"
    bl_label = "Move Text Literal Up"
    bl_description = "Move the text literal up in the\norder of literals"

    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Drawing.get_text_props(obj)
        props.literals.move(self.literal_prop_id, self.literal_prop_id - 1)
        tool.Blender.update_viewport()
        return {"FINISHED"}


class OrderTextLiteralDown(bpy.types.Operator):
    bl_idname = "bim.order_text_literal_down"
    bl_label = "Move Text Literal Down"
    bl_description = "Move the text literal down in the\norder of literals"

    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Drawing.get_text_props(obj)
        props.literals.move(self.literal_prop_id, self.literal_prop_id + 1)
        tool.Blender.update_viewport()
        return {"FINISHED"}


class AssignSelectedObjectAsProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_selected_as_product"
    bl_label = "Assign Selected Object As Product"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) < 2:
            cls.poll_message_set("At least 2 objects need to be selected")
            return False
        return True

    def _execute(self, context):
        objs = context.selected_objects[:]
        ifc_objs = [(o, tool.Ifc.get_entity(o)) for o in objs if tool.Ifc.get_entity(o)]

        annotations = [(o, e) for o, e in ifc_objs if e.is_a("IfcAnnotation")]
        non_annotations = [(o, e) for o, e in ifc_objs if not e.is_a("IfcAnnotation")]

        if not annotations:
            self.report({"ERROR"}, "At least one selected object must be an IfcAnnotation.")
            return {"CANCELLED"}

        if len(non_annotations) == 1:
            # One product, one or more annotations — assign all annotations to the product.
            product = non_annotations[0][1]
        elif len(non_annotations) == 0 and len(annotations) == 2:
            # Both objects are annotations — use the non-active one as the relating product.
            active_obj = context.active_object
            if annotations[0][0] == active_obj:
                annotation_obj, annotation = annotations[0]
                product = annotations[1][1]
            else:
                annotation_obj, annotation = annotations[1]
                product = annotations[0][1]
            core.edit_assigned_product(tool.Ifc, tool.Drawing, obj=annotation_obj, product=product)
            tool.Blender.update_viewport()
            return
        else:
            self.report(
                {"ERROR"},
                "Select exactly one product object and one or more IfcAnnotation objects.",
            )
            return {"CANCELLED"}

        for annotation_obj, _ in annotations:
            core.edit_assigned_product(tool.Ifc, tool.Drawing, obj=annotation_obj, product=product)

        tool.Blender.update_viewport()


class EditAssignedProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_assigned_product"
    bl_label = "Edit Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        product = None
        assert (obj := context.active_object)
        props = tool.Drawing.get_object_assigned_product_props(obj)
        if props.relating_product:
            product = tool.Ifc.get_entity(props.relating_product)
        core.edit_assigned_product(tool.Ifc, tool.Drawing, obj=obj, product=product)
        tool.Blender.update_viewport()


class EnableEditingAssignedProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_assigned_product"
    bl_label = "Enable Editing Assigned Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        assert context.active_object
        core.enable_editing_assigned_product(tool.Drawing, obj=context.active_object)


class DisableEditingAssignedProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_assigned_product"
    bl_label = "Disable Editing Assigned Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        assert context.active_object
        core.disable_editing_assigned_product(tool.Drawing, obj=context.active_object)


class LoadSheets(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_sheets"
    bl_label = "Load Sheets"
    bl_description = "Load the saved sheets in this IFC project"

    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_sheets(tool.Drawing)

        props = tool.Drawing.get_document_props()
        warnings: list[tool.Drawing.SheetWarningType] = []
        for sheet_prop in props.sheets:
            if not sheet_prop.is_sheet:
                continue

            sheet = tool.Ifc.get().by_id(sheet_prop.ifc_definition_id)
            document_uri = tool.Drawing.get_document_uri(sheet)
            assert document_uri is not None

            filepath = Path(document_uri)
            if not filepath.is_file():
                res = core.regenerate_sheet(tool.Drawing, sheet)
                if res:
                    warnings.extend(res)

        if warnings:
            self.report({"WARNING"}, f"There were warnings loading sheets. See system console for the details.")
            print("-" * 10)
            print("\n".join(str(w) for w in warnings))


class EditSheet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_sheet"
    bl_label = "Edit Sheet / Drawing"
    bl_description = "Edit details of sheet or drawing"
    bl_options = {"REGISTER", "UNDO"}
    identification: bpy.props.StringProperty()
    name: bpy.props.StringProperty()

    document_type: Literal["SHEET", "TITLEBLOCK", "EMBEDDED"]

    def invoke(self, context, event):
        assert context.window_manager
        sheet_item = tool.Drawing.get_active_sheet_item()
        assert sheet_item
        sheet = tool.Ifc.get().by_id(sheet_item.ifc_definition_id)
        if sheet.is_a("IfcDocumentInformation"):
            self.document_type = "SHEET"
            self.name = sheet.Name
            self.identification = sheet.DocumentId if tool.Ifc.get_schema() == "IFC2X3" else sheet.Identification
        elif sheet.is_a("IfcDocumentReference") and tool.Drawing.get_reference_description(sheet) == "TITLEBLOCK":
            self.document_type = "TITLEBLOCK"
        else:
            self.document_type = "EMBEDDED"
            self.identification = sheet.Identification
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        assert self.layout
        props = tool.Drawing.get_document_props()
        if self.document_type == "SHEET":
            row = self.layout.row()
            row.prop(self, "identification", text="Identification")
            row = self.layout.row()
            row.prop(self, "name", text="Name")
        elif self.document_type == "TITLEBLOCK":
            row = self.layout.row()
            row.prop(props, "titleblock", text="Titleblock")
        elif self.document_type == "EMBEDDED":
            row = self.layout.row()
            row.prop(self, "identification", text="Identification")

    def _execute(self, context):
        props = tool.Drawing.get_document_props()
        ifc_file = tool.Ifc.get()
        sheet_item = tool.Drawing.get_active_sheet_item()
        assert sheet_item
        sheet = tool.Ifc.get().by_id(sheet_item.ifc_definition_id)
        if self.document_type == "SHEET":
            core.rename_sheet(tool.Ifc, tool.Drawing, sheet=sheet, identification=self.identification, name=self.name)
        elif self.document_type == "EMBEDDED":
            core.rename_reference(tool.Ifc, tool.Drawing, reference=sheet, identification=self.identification)
        elif self.document_type == "TITLEBLOCK":
            titleblock = props.titleblock
            reference = sheet
            sheet = tool.Drawing.get_reference_document(reference)
            assert sheet
            ifcopenshell.api.document.edit_reference(
                ifc_file,
                reference=reference,
                attributes={"Location": tool.Drawing.get_default_titleblock_path(titleblock)},
            )
            sheet_builder = sheeter.SheetBuilder()
            sheet_builder.change_titleblock(sheet, titleblock)
        tool.Drawing.import_sheets()


class DisableEditingSheets(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_sheets"
    bl_label = "Disable Editing Sheets"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_sheets(tool.Drawing)


class LoadSchedules(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_schedules"
    bl_label = "Load Schedules"
    bl_description = "Load the saved schedules in this IFC project"

    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_schedules(tool.Drawing)


class DisableEditingSchedules(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_schedules"
    bl_label = "Disable Editing Schedules"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_schedules(tool.Drawing)


class LoadReferences(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_references"
    bl_label = "Load References"
    bl_description = "Load the saved references in this IFC project"

    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_references(tool.Drawing)


class DisableEditingReferences(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_references"
    bl_label = "Disable Editing References"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_references(tool.Drawing)


class LoadDrawings(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_drawings"
    bl_label = "Load Drawings"
    bl_description = "Load the saved drawings in this IFC project"

    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # Operator is not accessible through UI if IFC project is not saved,
        # but adding poll check to avoid using Drawings UI in scripts with unsaved project.
        if tool.Ifc.get_path():
            return True
        cls.poll_message_set("IFC project is not saved.")
        return False

    def _execute(self, context):
        core.load_drawings(tool.Drawing)


class DisableEditingDrawings(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_drawings"
    bl_label = "Disable Editing Drawings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_drawings(tool.Drawing)


ToggleOption = Literal["EXPAND", "CONTRACT"]


class ToggleTargetView(bpy.types.Operator):
    bl_idname = "bim.toggle_target_view"
    bl_label = "Toggle Target View"
    bl_options = {"REGISTER", "UNDO"}

    target_view: bpy.props.StringProperty()
    toggle_all: bpy.props.BoolProperty(
        default=False,
        options={"SKIP_SAVE"},
    )
    option: bpy.props.EnumProperty(items=[(i, i, "") for i in get_args(ToggleOption)])

    if TYPE_CHECKING:
        target_view: str
        toggle_all: bool
        option: ToggleOption

    @classmethod
    def description(cls, context, properties) -> str:
        option: ToggleOption = properties.option
        if option == "EXPAND":
            return "Expand target view.\n\nSHIFT+CLICK to expand all view categories."
        else:
            return "Contract target view.\n\nSHIFT+CLICK to contract all view categories."

    def invoke(self, context, event):
        # Toggling all categories on shift+click.
        # Make sure to use SKIP_SAVE on property, otherwise it might get stuck (copied from #4771).
        if event.type == "LEFTMOUSE" and event.shift:
            self.toggle_all = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        expanded = self.option == "EXPAND"
        for drawing in props.drawings:
            if drawing.is_drawing:
                continue
            if self.toggle_all or drawing.target_view == self.target_view:
                drawing.is_expanded = expanded
        core.load_drawings(tool.Drawing)
        return {"FINISHED"}


class ExpandSheet(bpy.types.Operator):
    bl_idname = "bim.expand_sheet"
    bl_label = "Expand Sheet"
    bl_description = "Show views, schedules, references etc\nplaced on this sheet.\n\nShift+click to expand all sheets."
    bl_options = {"REGISTER", "UNDO"}

    sheet: bpy.props.IntProperty()
    expand_all: bpy.props.BoolProperty(name="Expand All", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.shift:
            self.expand_all = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        for sheet in [s for s in props.sheets if self.expand_all or s.ifc_definition_id == self.sheet]:
            sheet.is_expanded = True
        core.load_sheets(tool.Drawing)
        return {"FINISHED"}


class ContractSheet(bpy.types.Operator):
    bl_idname = "bim.contract_sheet"
    bl_label = "Contract Sheet"
    bl_description = (
        "Hide views, schedules, references etc\nplaced on this sheet.\n\nShift+click to contract all sheets."
    )
    bl_options = {"REGISTER", "UNDO"}

    sheet: bpy.props.IntProperty()
    expand_all: bpy.props.BoolProperty(name="Expand All", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.shift:
            self.expand_all = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        for sheet in [s for s in props.sheets if self.expand_all or s.ifc_definition_id == self.sheet]:
            sheet.is_expanded = False
        core.load_sheets(tool.Drawing)
        return {"FINISHED"}


class SelectAssignedProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_assigned_product"
    bl_label = "Select Assigned Product"
    bl_description = "Select the product this element is assigned to"

    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.select_assigned_product(tool.Drawing, context)


class EnableEditingElementFilter(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_element_filter"
    bl_label = "Element Filter Mode"
    bl_options = {"REGISTER", "UNDO"}
    filter_mode: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.filter_mode == "NONE":
            return "Cancel filter"
        return "Enable editing options for the include or exclude filter"

    def _execute(self, context):
        assert context.scene
        obj = context.scene.camera
        if not obj:
            return
        assert (camera := context.scene.camera)
        props = tool.Drawing.get_camera_props(camera)
        props.filter_mode = self.filter_mode
        element = tool.Ifc.get_entity(obj)
        assert element
        if query := ifcopenshell.util.element.get_pset(element, "EPset_Drawing", self.filter_mode.title()):
            filter_groups = tool.Search.get_filter_groups(f"drawing_{self.filter_mode.lower()}")
            try:
                tool.Search.import_filter_query(query, filter_groups)
            except:
                pass


class EditElementFilter(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_element_filter"
    bl_label = "Edit Element Filter"
    bl_description = "Saves the filter"
    bl_options = {"REGISTER", "UNDO"}
    filter_mode: bpy.props.StringProperty()

    def _execute(self, context):
        assert context.scene
        obj = context.scene.camera
        assert obj
        props = tool.Drawing.get_camera_props(obj)
        element = tool.Ifc.get_entity(obj)
        assert element
        pset = tool.Pset.get_element_pset(element, "EPset_Drawing")
        assert pset
        if self.filter_mode == "INCLUDE":
            query = tool.Search.export_filter_query(props.include_filter_groups) or None
            ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Include": query})
        elif self.filter_mode == "EXCLUDE":
            query = tool.Search.export_filter_query(props.exclude_filter_groups) or None
            ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Exclude": query})
        props.filter_mode = "NONE"
        bpy.ops.bim.activate_drawing(drawing=element.id(), should_view_from_camera=False)


class AddReferenceImage(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.add_reference_image"
    bl_label = "Add Reference Image"
    bl_description = "Add or import reference image to the IFC project"

    bl_options = {"REGISTER", "UNDO"}

    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=True)
    filter_image: bpy.props.BoolProperty(default=True, options={"HIDDEN", "SKIP_SAVE"})
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN", "SKIP_SAVE"})
    x_length: bpy.props.FloatProperty(
        name="X Length",
        description="Width of the reference image",
        default=1.0,
        min=0.001,
        soft_min=0.01,
        precision=3,
        unit="LENGTH",
    )
    y_length: bpy.props.FloatProperty(
        name="Y Length",
        description="Height of the reference image",
        default=1.0,
        min=0.001,
        soft_min=0.01,
        precision=3,
        unit="LENGTH",
    )
    show_texture_solid_mode: bpy.props.BoolProperty(
        name="Show Texture in Solid mode (slow)",
        description="Show Texture in Solid mode (slow)",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC project is loaded.")
            return False
        return True

    def invoke(self, context, event):
        self._last_filepath = ""
        return super().invoke(context, event)

    def check(self, context):
        if not hasattr(self, "_last_filepath"):
            self._last_filepath = ""

        if self.filepath and self.filepath != self._last_filepath:
            self._last_filepath = self.filepath

            abs_path = Path(self.filepath).absolute().resolve()
            if abs_path.exists() and abs_path.is_file():
                image = load_image(abs_path.name, str(abs_path.parent), check_existing=False)
                image_width_px = image.size[0]
                image_height_px = image.size[1]
                aspect_ratio = image_width_px / image_height_px

                if aspect_ratio >= 1.0:
                    self.x_length = 1.0
                    self.y_length = 1.0 / aspect_ratio
                else:
                    self.x_length = aspect_ratio
                    self.y_length = 1.0

                bpy.data.images.remove(image)
                return True

        return False

    def draw(self, context):
        layout = self.layout
        if Path(tool.Ifc.get_path()).is_file():
            layout.prop(self, "use_relative_path")
        else:
            self.use_relative_path = False
        layout.prop(self, "show_texture_solid_mode")
        layout.prop(self, "x_length")
        layout.prop(self, "y_length")

    def _execute(self, context):
        project_props = tool.Project.get_project_props()
        project_props.load_indexed_maps = self.show_texture_solid_mode
        space = tool.Blender.get_view3d_space()
        if space.shading.color_type != "TEXTURE":
            space.shading.color_type = "TEXTURE"
            self.report(
                {"WARNING"},
                '"Object Color" for Viewport Shading: Solid changed to "Texture" to see the reference image properly.',
            )

        abs_path = Path(self.filepath).absolute().resolve()
        image_filepath = Path(tool.Ifc.get_uri(self.filepath, use_relative_path=self.use_relative_path))
        ifc_file = tool.Ifc.get()

        image = load_image(abs_path.name, str(abs_path.parent), check_existing=False)

        mesh = bpy.data.meshes.new(image_filepath.stem)
        obj = bpy.data.objects.new(image_filepath.stem, mesh)
        element = tool.Drawing.run_root_assign_class(
            obj=obj, ifc_class="IfcAnnotation", predefined_type="IMAGE", should_add_representation=False
        )

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        hx = self.x_length * 0.5 / unit_scale
        hy = self.y_length * 0.5 / unit_scale
        verts = [(-hx, -hy, 0.0), (hx, -hy, 0.0), (hx, hy, 0.0), (-hx, hy, 0.0)]
        item = builder.mesh(verts, [[0, 1, 2, 3]])

        ifc_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        representation = builder.get_representation(ifc_context, [item])
        ifcopenshell.api.geometry.assign_representation(ifc_file, element, representation)

        style = ifcopenshell.api.style.add_style(tool.Ifc.get(), name=image_filepath.stem)
        ifcopenshell.api.style.assign_representation_styles(
            ifc_file, shape_representation=representation, styles=[style]
        )

        # TODO: IfcSurfaceStyleRendering is unnecessary here, added it only because
        # we don't support IfcSurfaceStyleWithTextures without Rendering yet
        shading_attributes = {
            "SurfaceColour": {"Red": 1.0, "Green": 1.0, "Blue": 1.0},
            "Transparency": 0.0,
            "ReflectanceMethod": "NOTDEFINED",
        }
        ifcopenshell.api.style.add_surface_style(
            tool.Ifc.get(), style=style, ifc_class="IfcSurfaceStyleRendering", attributes=shading_attributes
        )

        if tool.Ifc.get_schema() == "IFC2X3":
            texture = ifc_file.create_entity(
                "IfcImageTexture",
                RepeatS=True,
                RepeatT=True,
                TextureType="TEXTURE",
                UrlReference=image_filepath.as_posix(),
            )
        else:
            texture = ifc_file.create_entity("IfcImageTexture", Mode="DIFFUSE", URLReference=image_filepath.as_posix())
            ifc_file.create_entity("IfcTextureCoordinateGenerator", Maps=[texture], Mode="COORD")

        textures = [texture]
        ifcopenshell.api.style.add_surface_style(
            ifc_file, style=style, ifc_class="IfcSurfaceStyleWithTextures", attributes={"Textures": textures}
        )

        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.create_style(style)

        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)


class ConvertSVGToDXF(bpy.types.Operator):
    bl_idname = "bim.convert_svg_to_dxf"
    bl_label = "Convert SVG to DXF"
    bl_options = {"REGISTER", "UNDO"}
    view: bpy.props.StringProperty()
    bl_description = "Convert selected drawing's .svg to .dxf.\n\nSHIFT+CLICK to convert all shown checked drawings"
    convert_all: bpy.props.BoolProperty(name="Convert All", default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        props = tool.Drawing.get_document_props()
        if not tool.Drawing.get_active_drawing_item():
            cls.poll_message_set("No drawing selected.")
            return False
        return True

    def invoke(self, context, event):
        # convert all drawings on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.convert_all = True
        return self.execute(context)

    def execute(self, context):
        props = tool.Drawing.get_document_props()
        if self.convert_all:
            drawings = [
                tool.Ifc.get().by_id(d.ifc_definition_id) for d in props.drawings if d.is_drawing and d.is_selected
            ]
        else:
            drawings = [tool.Ifc.get().by_id(props.drawings.get(self.view).ifc_definition_id)]

        drawing_uris: list[Path] = []
        drawings_not_found: list[str] = []

        for drawing in drawings:
            drawing_uri = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_document(drawing))
            if drawing_uri is None or not os.path.exists(drawing_uri):
                drawings_not_found.append(drawing.Name)
            else:
                drawing_uris.append(Path(drawing_uri))

        if drawings_not_found:
            msg = "Some drawings .svg files were not found, need to print them first: \n{}.".format(
                "\n".join(drawings_not_found)
            )
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        for drawing_uri in drawing_uris:
            tool.Drawing.convert_svg_to_dxf(drawing_uri, drawing_uri.with_suffix(".dxf"))

        self.report({"INFO"}, f"{len(drawing_uris)} drawings were converted to .dxf.")
        return {"FINISHED"}


class OpenDocumentationWebUi(bpy.types.Operator):
    bl_idname = "bim.open_documentation_web_ui"
    bl_label = "Open Documentation Web UI"
    bl_description = "Open the documentation web UI page"

    def execute(self, context):
        if not tool.Web.get_web_props().is_connected:
            bpy.ops.bim.connect_websocket_server(page="documentation")
        else:
            bpy.ops.bim.open_web_browser(page="documentation")
        return {"FINISHED"}


class ExcludeAnnotation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.exclude_annotation"
    bl_label = "Exclude Annotation"
    bl_description = "Excludes the automatic annotation reference from the drawing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        if not (obj := bpy.context.scene.camera) or not (drawing := tool.Ifc.get_entity(obj)):
            return
        for obj in tool.Blender.get_selected_objects(include_active=False):
            if (element := tool.Ifc.get_entity(obj)) and tool.Drawing.is_auto_annotation(element):
                if referenced_element := tool.Drawing.get_annotation_element(element):
                    tool.Drawing.exclude_annotation_from_drawing(referenced_element, drawing)
        core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=drawing)


class ActivateDrawingByAnnotation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.activate_drawing_by_annotation"
    bl_label = "Activate Drawing"
    bl_description = "Activate the drawing corresponding to the selected annotation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # Check if an annotation object is selected
        if not context.selected_objects:
            cls.poll_message_set("No object selected")
            return False

        active_obj = context.active_object
        if not active_obj:
            cls.poll_message_set("No active object")
            return False

        element = tool.Ifc.get_entity(active_obj)
        if not element:
            cls.poll_message_set("Selected object is not an IFC element")
            return False

        # Check if it's an IfcAnnotation with ObjectType = "SECTION" or "ELEVATION"
        if not element.is_a("IfcAnnotation") or element.ObjectType not in ["SECTION", "ELEVATION"]:
            cls.poll_message_set("Selected object is not a drawing annotation")
            return False

        return True

    def _execute(self, context):
        active_obj = context.active_object
        element = tool.Ifc.get_entity(active_obj)

        if not element or not element.is_a("IfcAnnotation") or element.ObjectType not in ["SECTION", "ELEVATION"]:
            self.report({"ERROR"}, "Selected object is not a drawing annotation")
            return {"CANCELLED"}

        # Find the drawing/camera element that this annotation references
        drawing_element = self.find_drawing_from_annotation(element)

        if not drawing_element:
            self.report({"ERROR"}, "Could not find drawing element for this annotation")
            return {"CANCELLED"}

        # Use the existing ActivateDrawing operator with the drawing element's ID
        bpy.ops.bim.activate_drawing(drawing=drawing_element.id())

        return {"FINISHED"}

    def find_drawing_from_annotation(self, annotation_element):
        """Find the drawing/camera element that this annotation references."""
        ifc = tool.Ifc.get()

        # Check IfcRelAssignsToProduct relationships
        for rel in ifc.get_inverse(annotation_element):
            if rel.is_a("IfcRelAssignsToProduct") and rel.RelatingProduct:
                if rel.RelatingProduct.is_a("IfcAnnotation"):
                    # Found the drawing element!
                    return rel.RelatingProduct

        return None


class SelectSimilarTextLiteralValue(bpy.types.Operator):
    bl_idname = "bim.select_similar_text_literal_value"
    bl_label = ""
    bl_description = "Click to select all text annotations with this value\n\nSHIFT+CLICK to remove from selection"
    bl_options = {"REGISTER", "UNDO"}

    literal_value: bpy.props.StringProperty()
    literal_index: bpy.props.IntProperty(default=0)
    attribute_type: bpy.props.StringProperty(default="text")
    display_text: bpy.props.StringProperty()
    remove_from_selection: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if hasattr(event, "type") and event.type == "LEFTMOUSE":
            self.remove_from_selection = event.shift
        elif hasattr(event, "shift"):
            self.remove_from_selection = event.shift

        return self.execute(context)

    def execute(self, context):
        if not self.literal_value and self.attribute_type in ["text", "path", "box_alignment", "font_size"]:
            return {"CANCELLED"}

        editing_status = {}
        for obj in context.visible_objects:
            obj_props = tool.Drawing.get_text_props(obj)
            editing_status[obj] = obj_props.is_editing if hasattr(obj_props, "is_editing") else False

        count = 0
        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not tool.Drawing.is_annotation_object_type(element, ["TEXT", "TEXT_LEADER"]):
                continue

            obj_props = tool.Drawing.get_text_props(obj)
            should_select = False

            if self.attribute_type in ["text", "path", "box_alignment", "font_size", "literal", "resolved_text"]:
                was_editing = obj_props.is_editing if hasattr(obj_props, "is_editing") else False
                if not was_editing:
                    core.enable_editing_text(tool.Drawing, obj=obj)

                if self.attribute_type == "font_size":
                    should_select = str(obj_props.font_size) == self.literal_value
                elif self.attribute_type == "literal":
                    for idx, literal in enumerate(obj_props.literals):
                        if len(literal.attributes) > 0:
                            if literal.attributes[0].string_value == self.literal_value:
                                should_select = True
                                break
                elif self.attribute_type == "resolved_text":
                    for idx, literal in enumerate(obj_props.literals):
                        if len(literal.attributes) > 0:
                            raw_value = literal.attributes[0].string_value
                            assigned_element = tool.Drawing.get_assigned_product(element) or element
                            resolved_value = tool.Drawing.replace_text_literal_variables(raw_value, assigned_element)
                            if resolved_value == self.literal_value:
                                should_select = True
                                break
                else:
                    for idx, literal in enumerate(obj_props.literals):
                        if self.attribute_type == "text" and len(literal.attributes) > 0:
                            raw_value = literal.attributes[0].string_value
                            assigned_element = tool.Drawing.get_assigned_product(element) or element
                            resolved_value = tool.Drawing.replace_text_literal_variables(raw_value, assigned_element)
                            if resolved_value == self.literal_value:
                                should_select = True
                                break
                        elif self.attribute_type == "path" and len(literal.attributes) > 1:
                            attr = literal.attributes[1]
                            if attr.data_type == "enum":
                                if attr.enum_value == self.literal_value:
                                    should_select = True
                                    break
                            else:
                                if attr.string_value == self.literal_value:
                                    should_select = True
                                    break
                        elif self.attribute_type == "box_alignment":
                            if literal.get_box_alignment() == self.literal_value:
                                should_select = True
                                break

            if should_select:
                obj.select_set(not self.remove_from_selection)
                count += 1

        for obj, was_editing in editing_status.items():
            obj_props = tool.Drawing.get_text_props(obj)
            if hasattr(obj_props, "is_editing"):
                if was_editing and not obj_props.is_editing:
                    core.enable_editing_text(tool.Drawing, obj=obj)
                elif not was_editing and obj_props.is_editing:
                    core.disable_editing_text(tool.Drawing, obj=obj)

        if self.attribute_type in ["text", "path", "box_alignment"]:
            result = f'literal[{self.literal_index}].{self.attribute_type} = "{self.literal_value}"'
        else:
            result = f'{self.attribute_type} = "{self.literal_value}"'

        verb = "Deselected" if self.remove_from_selection else "Selected"
        self.report(
            {"INFO"},
            f"{verb} {count} objects with {self.attribute_type} '{self.literal_value}'.",
        )

        return {"FINISHED"}


class FilterSelectedObjectsIfIntersectedByCamera(bpy.types.Operator):
    bl_idname = "bim.filter_selected_objects_if_intersected_by_camera"
    bl_label = "Filter Selected Objects If Intersected by Camera"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Deselect objects that are not intersected by the active camera view"

    @classmethod
    def poll(cls, context):
        return context.scene.camera is not None and len(context.selected_objects) > 0

    def execute(self, context):
        self.filter_selected_objects_if_intersected_by_camera(context)
        return {"FINISHED"}

    def filter_selected_objects_if_intersected_by_camera(self, context: bpy.types.Context) -> None:
        camera_obj = context.scene.camera
        if not camera_obj:
            return

        camera = camera_obj.data
        if not isinstance(camera, bpy.types.Camera):
            return

        cam_matrix = camera_obj.matrix_world
        cam_origin = cam_matrix.translation
        cam_direction = cam_matrix.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        plane_normal = cam_direction.normalized()
        plane_point = cam_origin

        def point_plane_distance(point):
            return (point - plane_point).dot(plane_normal)

        selected_objects = [obj for obj in context.selected_objects if obj != camera_obj]

        deselected = 0
        for obj in selected_objects:
            bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            distances = [point_plane_distance(p) for p in bbox_world]
            min_d = min(distances)
            max_d = max(distances)

            intersects = (min_d <= 0.0 <= max_d) or (max_d <= 0.0 <= min_d)

            if not intersects:
                obj.select_set(False)
                deselected += 1

        remaining_selected = len([obj for obj in context.selected_objects if obj != camera_obj])
        self.report(
            {"INFO"}, f"Filtered to {remaining_selected} object(s) intersecting camera plane (deselected {deselected})"
        )
        return {"FINISHED"}


class SelectElementValues(bpy.types.Operator):
    bl_idname = "bim.select_element_values"
    bl_label = "Select Element Values"
    bl_description = "Select a property or quantity from the assigned product to insert into the text literal"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()
    expanded_category: bpy.props.StringProperty(default="Basic")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        assigned_product = tool.Drawing.get_assigned_product(element)
        if not assigned_product:
            self.layout.label(text="No product assigned to this annotation", icon="ERROR")
            return

        if not ElementValuesData.is_loaded:
            ElementValuesData.load()
        available_keys = ElementValuesData.get_available_element_value_keys(assigned_product)

        for category_name, keys in available_keys.items():
            if not keys:
                continue

            box = self.layout.box()
            box.label(text=category_name, icon=self.get_category_icon(category_name))

            for key, description in keys:
                row = box.row()
                row.label(text=description)

    def execute(self, context):
        return {"FINISHED"}

    def get_category_icon(self, category_name):
        icons = {
            "Basic": "OBJECT_DATA",
            "Attributes": "PROPERTIES",
            "Property Sets": "PROPERTIES",
            "Quantity Sets": "SNAP_VOLUME",
            "Type": "OUTLINER_OB_MESH",
            "Spatial": "HOME",
            "Parent": "FILE_PARENT",
            "Classification": "BOOKMARKS",
            "Groups": "GROUP",
            "Systems": "SYSTEM",
            "Zones": "MESH_CIRCLE",
            "Material": "MATERIAL",
            "Coordinates": "EMPTY_ARROWS",
        }
        return icons.get(category_name, "DOT")


class ToggleElementValuesPanel(bpy.types.Operator):
    bl_idname = "bim.toggle_element_values_panel"
    bl_label = "Toggle Element Values Panel"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]

        current_state = getattr(literal_props, "show_element_values", False)
        literal_props.show_element_values = not current_state

        return {"FINISHED"}


class ToggleElementValuesCategory(bpy.types.Operator):
    bl_idname = "bim.toggle_element_values_category"
    bl_label = "Toggle Element Values Category"
    bl_options = {"REGISTER", "UNDO"}

    category_name: bpy.props.StringProperty()
    literal_prop_id: bpy.props.IntProperty()
    is_currently_expanded: bpy.props.BoolProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]

        if self.is_currently_expanded:
            literal_props.expanded_category = ""
        else:
            literal_props.expanded_category = self.category_name

        return {"FINISHED"}


class InsertFormattedLiteralPopup(bpy.types.Operator):
    bl_idname = "bim.insert_formatted_literal_popup"
    bl_label = "Insert Formatted Element Value"
    bl_description = "Insert element value with formatting options"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()
    element_value_key: bpy.props.StringProperty()
    value_number: bpy.props.IntProperty()

    formatting_type: bpy.props.EnumProperty(
        name="Formatting",
        items=[
            ("NONE", "No Formatting", "Insert value as-is"),
            ("UPPER", "Uppercase", "Convert to uppercase"),
            ("LOWER", "Lowercase", "Convert to lowercase"),
            ("TITLE", "Title Case", "Convert to title case"),
            ("ROUND", "Round Number", "Round to specified precision"),
            ("INT", "Integer", "Truncate decimal part"),
            ("NUMBER", "Format Number", "Format with separators"),
            ("METRIC_LENGTH", "Metric Length", "Format as metric length"),
            ("IMPERIAL_LENGTH", "Imperial Length", "Format as imperial length"),
            ("CUSTOM", "Custom Expression", "Create custom expression with functions"),
        ],
        default="NONE",
    )

    round_precision: bpy.props.StringProperty(
        name="Precision", description="Rounding precision (e.g. 0.1, 0.01, 0.001, 1, 10, 100)", default="0.01"
    )

    decimal_separator: bpy.props.StringProperty(
        name="Decimal Separator", description="Decimal separator character", default=".", maxlen=1
    )

    thousands_separator: bpy.props.StringProperty(
        name="Thousands Separator", description="Thousands separator character", default=",", maxlen=1
    )

    metric_decimals: bpy.props.IntProperty(
        name="Decimal Places", description="Number of decimal places to show", default=2, min=0, max=10
    )

    metric_precision: bpy.props.StringProperty(
        name="Metric Precision",
        description="Rounding precision for metric length (e.g. 0.1, 0.01, 0.001)",
        default="0.01",
    )

    imperial_precision: bpy.props.IntProperty(
        name="Fraction Precision", description="Imperial fraction precision (1/N)", default=4, min=1, max=64
    )

    imperial_input_unit: bpy.props.EnumProperty(
        name="Input Unit",
        items=[
            ("foot", "Feet", "Input value is in feet"),
            ("inch", "Inches", "Input value is in inches"),
        ],
        default="foot",
    )

    imperial_output_unit: bpy.props.EnumProperty(
        name="Output Format",
        items=[
            ("foot", "Feet and Inches", "Display as feet and inches"),
            ("inch", "Inches Only", "Display as inches only"),
        ],
        default="foot",
    )

    custom_expression: bpy.props.StringProperty(
        name="Custom Expression",
        description=(
            "Custom expression using functions like concat(), upper(), round(), etc.\n"
            "Use {{value}} as placeholder for the selected element value.\n"
            "Examples:\n"
            '- concat("Name: ", {{value}})\n'
            '- upper(concat("Type: ", {{value}}))'
        ),
        default='concat({{value}}, " - additional text")',
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text=f"Element Value: {self.element_value_key}", icon="PROPERTIES")

        layout.prop(self, "formatting_type")

        if self.formatting_type == "ROUND":
            layout.prop(self, "round_precision")
        elif self.formatting_type == "NUMBER":
            col = layout.column()
            col.prop(self, "decimal_separator")
            col.prop(self, "thousands_separator")
        elif self.formatting_type == "METRIC_LENGTH":
            col = layout.column()
            col.prop(self, "metric_precision")
            col.prop(self, "metric_decimals")
        elif self.formatting_type == "IMPERIAL_LENGTH":
            col = layout.column()
            col.prop(self, "imperial_precision")
            col.prop(self, "imperial_input_unit")
            col.prop(self, "imperial_output_unit")
        elif self.formatting_type == "CUSTOM":
            col = layout.column()
            col.prop(self, "custom_expression", text="")

            obj = bpy.context.active_object
            if obj:
                element = tool.Ifc.get_entity(obj)

                props = tool.Drawing.get_text_props(obj)
                product = None

                if props.literals:
                    for literal_props in props.literals:
                        if hasattr(literal_props, "product_used") and literal_props.product_used:
                            product = tool.Ifc.get_entity(literal_props.product_used)
                            break

                if not product:
                    product = tool.Drawing.get_assigned_product(element)

                if not product:
                    product = element

                if product:
                    all_categories = ElementValuesData.get_available_element_value_keys(product)

                    available_keys = []
                    for cat_name, cat_keys in all_categories.items():
                        for cat_key, cat_desc in cat_keys:
                            available_keys.append(
                                (
                                    cat_key,
                                    f"[{cat_name}] {cat_desc.split(': ', 1)[-1] if ': ' in cat_desc else cat_desc}",
                                )
                            )

                    if available_keys:
                        help_box = col.box()
                        help_box.scale_y = 0.7
                        help_box.label(text="Available attributes:", icon="INFO")

                        for i, (key, desc) in enumerate(available_keys[:5]):
                            help_box.label(text="{{value{}}} = {} ({})".format(i + 1, key, desc))

                        if len(available_keys) > 5:
                            help_box.label(text=f"... and {len(available_keys) - 5} more attributes")

            help_box = col.box()
            help_box.scale_y = 0.8
            help_box.label(text="Available functions:", icon="INFO")
            help_box.label(text="• concat(text1, text2, ...) - combine values")
            help_box.label(text="• upper(value) - uppercase")
            help_box.label(text="• lower(value) - lowercase")
            help_box.label(text="• round(value, precision) - round number")
            help_box.label(text="• Use {{value}} for current element value")

        preview_box = layout.box()
        preview_box.label(text="Preview:", icon="PROPERTIES")
        formatted_syntax = self._generate_formatted_syntax()

        preview_text = formatted_syntax
        if len(preview_text) > 60:
            words = preview_text.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + " " + word) > 60 and current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = (current_line + " " + word).strip()
            if current_line:
                lines.append(current_line)

            for line in lines:
                preview_box.label(text=line)
        else:
            preview_box.label(text=preview_text)

    def _get_all_available_keys(self, element):
        """Get all available element value keys in a flat list with their descriptions"""
        available_keys = []

        all_categories = ElementValuesData.get_available_element_value_keys(element)

        for category_name, keys in all_categories.items():
            for key, description in keys:
                available_keys.append(
                    (key, f"[{category_name}] {description.split(': ', 1)[-1] if ': ' in description else description}")
                )

        return available_keys

    def _generate_formatted_syntax(self) -> str:
        """Generate the formatted selector syntax based on current settings"""
        base_value = f"{{{{{self.element_value_key}}}}}"

        if self.formatting_type == "NONE":
            return base_value
        elif self.formatting_type == "UPPER":
            return f"``upper({base_value})`` "
        elif self.formatting_type == "LOWER":
            return f"``lower({base_value})`` "
        elif self.formatting_type == "TITLE":
            return f"``title({base_value})`` "
        elif self.formatting_type == "ROUND":
            return f"``round({base_value}, {self.round_precision})`` "
        elif self.formatting_type == "INT":
            return f"``int({base_value})`` "
        elif self.formatting_type == "NUMBER":
            return f"``number({base_value}, {self.decimal_separator}, {self.thousands_separator})`` "
        elif self.formatting_type == "METRIC_LENGTH":
            return f"``metric_length({base_value}, {self.metric_precision}, {self.metric_decimals})`` "
        elif self.formatting_type == "IMPERIAL_LENGTH":
            return f'``imperial_length({base_value}, {self.imperial_precision}, "{self.imperial_input_unit}", "{self.imperial_output_unit}")`` '
        elif self.formatting_type == "CUSTOM":
            custom_expr = self.custom_expression.replace("{{value}}", base_value)
            return f"``{custom_expr}``"

        return base_value

    def execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Drawing.get_text_props(obj)
        literal_props = props.literals[self.literal_prop_id]

        formatted_syntax = self._generate_formatted_syntax()

        for attr in literal_props.attributes:
            if attr.name == "Literal":
                current_text = attr.string_value or ""

                if current_text:
                    attr.string_value = f"{current_text} {formatted_syntax}"
                else:
                    attr.string_value = formatted_syntax
                break

        tool.Blender.update_viewport()
        return {"FINISHED"}


class ShowCategoryHelp(bpy.types.Operator):
    bl_idname = "bim.show_category_help"
    bl_label = "Category Help"
    bl_description = "Show help for this element value category"
    bl_options = {"REGISTER"}

    category_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = self.layout

        category_help = {
            "Basic": {
                "title": "BASIC KEYS",
                "icon": "DOT",
                "items": [
                    ("id", "IFC entity ID", "{{id}} → '12345'"),
                    ("class", "IFC class name", "{{class}} → 'IfcWall'"),
                    ("predefined_type", "Predefined type", "{{predefined_type}} → 'SOLIDWALL'"),
                ],
            },
            "Attributes": {
                "title": "ATTRIBUTES",
                "icon": "PROPERTIES",
                "items": [
                    ("Name", "Element name", "{{Name}} → 'Wall-001'"),
                    ("Description", "Element description", "{{Description}} → 'Exterior wall'"),
                    ("Tag", "Element tag", "{{Tag}} → 'W-01'"),
                    ("ObjectType", "Object type", "{{ObjectType}} → 'Load Bearing'"),
                ],
                "note": "All IFC attributes are accessible by their name",
            },
            "Property Sets": {
                "title": "PROPERTY SETS",
                "icon": "ALIGN_JUSTIFY",
                "items": [
                    ("Pset_*.PropertyName", "Property value", "{{Pset_WallCommon.FireRating}} → 'REI 120'"),
                    ("Pset_*.IsExternal", "Boolean property", "{{Pset_WallCommon.IsExternal}} → 'True'"),
                ],
                "note": "Access any property from any property set using Pset_Name.PropertyName syntax",
            },
            "Quantity Sets": {
                "title": "QUANTITY SETS",
                "icon": "ALIGN_JUSTIFY",
                "items": [
                    ("Qto_*.QuantityName", "Quantity value", "{{Qto_WallBaseQuantities.NetArea}} → '45.5'"),
                    ("Qto_*.NetVolume", "Volume quantity", "{{Qto_WallBaseQuantities.NetVolume}} → '9.1'"),
                ],
                "note": "Access any quantity from quantity sets using Qto_Name.QuantityName syntax",
            },
            "Type": {
                "title": "TYPE INFORMATION",
                "icon": "OUTLINER_OB_MESH",
                "items": [
                    ("type.Name", "Type element name", "{{type.Name}} → 'WT-200mm-Concrete'"),
                    ("types.count", "Number of instances of this type", "{{types.count}} → '15'"),
                    ("occurrences.count", "Same as types.count", "{{occurrences.count}} → '15'"),
                ],
                "example": "Type: {{type.Name}} ({{types.count}} instances)",
            },
            "Spatial": {
                "title": "SPATIAL HIERARCHY",
                "icon": "HOME",
                "items": [
                    ("container.Name", "Immediate spatial container", "{{container.Name}} → 'Level 2'"),
                    ("space.Name", "Containing space", "{{space.Name}} → 'Office 205'"),
                    ("storey.Name", "Building storey", "{{storey.Name}} → 'Level 2'"),
                    ("building.Name", "Building", "{{building.Name}} → 'Building A'"),
                    ("site.Name", "Site", "{{site.Name}} → 'Main Campus'"),
                ],
                "example": "{{building.Name}} / {{storey.Name}} / {{space.Name}}",
            },
            "Parent": {
                "title": "PARENT (AGGREGATION)",
                "icon": "OUTLINER_DATA_GP_LAYER",
                "items": [
                    ("parent.name", "Aggregate parent element", "{{parent.name}} → 'Curtain Wall-01'"),
                ],
                "note": "Used for aggregated elements like mullions in curtain walls",
            },
            "Material": {
                "title": "MATERIALS",
                "icon": "MATERIAL",
                "items": [
                    ("material.Name", "Material name", "{{material.Name}} → 'Concrete'"),
                    ("materials.count", "Number of layers/profiles", "{{materials.count}} → '3'"),
                    (
                        "material.item.Material.Name.0",
                        "First layer material",
                        "{{material.item.Material.Name.0}} → 'Brick'",
                    ),
                    (
                        "material.item.Material.Name.1",
                        "Second layer material",
                        "{{material.item.Material.Name.1}} → 'Insulation'",
                    ),
                    ("material.item.0.LayerThickness", "Layer thickness", "{{material.item.0.LayerThickness}} → '0.1'"),
                ],
                "example": "{{materials.count}} layers: {{material.item.Material.Name.0}}",
            },
            "Styles": {
                "title": "PRESENTATION STYLES",
                "icon": "COLOR",
                "items": [
                    ("styles.count", "Number of styles", "{{styles.count}} → '1'"),
                    ("styles.0.Name", "Style name (indexed)", "{{styles.0.Name}} → 'Red'"),
                    ("styles.0.Color", "RGB color value", "{{styles.0.Color}} → 'RGB(1.00, 0.00, 0.00)'"),
                ],
            },
            "Profiles": {
                "title": "PROFILES",
                "icon": "OUTLINER_DATA_CURVES",
                "items": [
                    ("profiles.count", "Number of profiles", "{{profiles.count}} → '2'"),
                    ("profiles.0.ProfileName", "Profile name (indexed)", "{{profiles.0.ProfileName}} → 'HEA200'"),
                    ("profiles.0.ProfileType", "Profile type (indexed)", "{{profiles.0.ProfileType}} → 'AREA'"),
                    ("profile.ProfileName", "Single swept profile", "{{profile.ProfileName}} → 'Rectangle'"),
                ],
            },
            "Groups": {
                "title": "GROUPS",
                "icon": "OUTLINER_OB_GROUP_INSTANCE",
                "items": [
                    ("group.Name", "Group name", "{{group.Name}} → 'Phase 1'"),
                    ("groups.count", "Number of group assignments", "{{groups.count}} → '2'"),
                ],
            },
            "Systems": {
                "title": "SYSTEMS",
                "icon": "OUTLINER_OB_GROUP_INSTANCE",
                "items": [
                    ("system.Name", "System name", "{{system.Name}} → 'HVAC-01'"),
                    ("systems.count", "Number of system assignments", "{{systems.count}} → '1'"),
                ],
            },
            "Zones": {
                "title": "ZONES",
                "icon": "OUTLINER_OB_GROUP_INSTANCE",
                "items": [
                    ("zone.Name", "Zone name", "{{zone.Name}} → 'Fire Zone A'"),
                    ("zones.count", "Number of zone assignments", "{{zones.count}} → '1'"),
                ],
            },
            "Classification": {
                "title": "CLASSIFICATION",
                "icon": "PRESET",
                "items": [
                    ("classification.0.Name", "Classification name (indexed)", "{{classification.0.Name}} → 'Walls'"),
                    (
                        "classification.0.Identification",
                        "Classification code (indexed)",
                        "{{classification.0.Identification}} → 'E20'",
                    ),
                    ("classification.count", "Number of classification references", "{{classification.count}} → '2'"),
                ],
            },
            "Coordinates": {
                "title": "COORDINATES",
                "icon": "ORIENTATION_VIEW",
                "items": [
                    ("x", "Local X coordinate", "{{x}} → '10.5'"),
                    ("y", "Local Y coordinate", "{{y}} → '5.2'"),
                    ("z", "Local Z coordinate", "{{z}} → '3.0'"),
                    ("easting", "Map easting coordinate", "{{easting}} → '500123.45'"),
                    ("northing", "Map northing coordinate", "{{northing}} → '6750234.56'"),
                    ("elevation", "Map elevation", "{{elevation}} → '123.45'"),
                ],
            },
        }

        if self.category_name in category_help:
            info = category_help[self.category_name]
            layout.label(text=info["title"], icon=info["icon"])

            box = layout.box()
            for key, desc, example in info["items"]:
                col = box.column(align=True)
                col.scale_y = 0.85
                col.label(text=f"{key} - {desc}")
                col.label(text=f"  {example}")
                box.separator(factor=0.3)

            if "note" in info:
                note_box = layout.box()
                note_box.label(text="Note:", icon="INFO")
                note_box.label(text=info["note"])

            if "example" in info:
                ex_box = layout.box()
                ex_box.label(text="Example:", icon="SCRIPTPLUGINS")
                ex_box.label(text=info["example"])
        else:
            layout.label(text=f"No help available for '{self.category_name}'")

    def execute(self, context):
        return {"FINISHED"}


class AddElementValueRow(bpy.types.Operator):
    bl_idname = "bim.add_element_value_row"
    bl_label = "Add Element Value Row"
    bl_description = "Add a new element value row"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]
        new_row = literal_props.element_value_rows.add()
        new_row.category = literal_props.category_for_adding
        new_row.element_key = ""
        new_row.formatted_value = ""

        if len(literal_props.element_value_rows) == 1:
            new_row.separator = ""
        else:
            new_row.separator = " - "

        return {"FINISHED"}


class RemoveElementValueRow(bpy.types.Operator):
    bl_idname = "bim.remove_element_value_row"
    bl_label = "Remove Element Value Row"
    bl_description = "Remove this element value row"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()
    row_index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]
        if self.row_index < len(literal_props.element_value_rows):
            literal_props.element_value_rows.remove(self.row_index)

        return {"FINISHED"}


class ElementValueSuggestionsPopup(bpy.types.Operator):
    bl_idname = "bim.element_value_suggestions_popup"
    bl_label = "Element Value Suggestions"
    bl_description = "Show suggestions for element values in the selected category"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()
    row_index: bpy.props.IntProperty()
    category: bpy.props.StringProperty()
    search_query: bpy.props.StringProperty(name="Search", description="Search for element values")

    collection_keys: bpy.props.CollectionProperty(type=StrProperty)
    collection_descriptions: bpy.props.CollectionProperty(type=StrProperty)

    selected_key: bpy.props.StringProperty()

    def invoke(self, context, event):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]
        current_product = get_current_product_for_element_values(obj, literal_props)

        if not current_product:
            self.report({"ERROR"}, "No product selected. Use eyedropper to select an object.")
            return {"CANCELLED"}

        element = tool.Ifc.get_entity(current_product)
        if not element:
            self.report({"ERROR"}, "Selected object has no IFC data")
            return {"CANCELLED"}

        if not ElementValuesData.is_loaded:
            ElementValuesData.load()

        available_keys = ElementValuesData.get_available_element_value_keys(element)

        if self.category not in available_keys:
            self.report({"ERROR"}, f"Category '{self.category}' not found")
            return {"CANCELLED"}

        keys = available_keys[self.category]
        if not keys:
            self.report({"INFO"}, f"No values available for category '{self.category}'")
            return {"CANCELLED"}

        self.collection_keys.clear()
        self.collection_descriptions.clear()
        for key, description in keys:
            self.collection_keys.add().name = key
            self.collection_descriptions.add().name = description

        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout

        layout.prop_search(self, "selected_key", self, "collection_descriptions", text="Value")

    def execute(self, context):
        if not self.selected_key:
            return {"CANCELLED"}

        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]
        if self.row_index >= len(literal_props.element_value_rows):
            return {"CANCELLED"}

        value_row = literal_props.element_value_rows[self.row_index]

        for idx, desc_item in enumerate(self.collection_descriptions):
            if desc_item.name == self.selected_key:
                actual_key = self.collection_keys[idx].name
                value_row.element_key = actual_key
                value_row.formatted_value = f"{{{{{actual_key}}}}}"
                break

        return {"FINISHED"}


class FormatElementValueRow(bpy.types.Operator):
    bl_idname = "bim.format_element_value_row"
    bl_label = "Format Element Value"
    bl_description = "Format element value with functions"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()
    row_index: bpy.props.IntProperty()

    formatting_type: bpy.props.EnumProperty(
        name="Formatting",
        items=[
            ("NONE", "No Formatting", "Insert value as-is"),
            ("UPPER", "Uppercase", "Convert to uppercase"),
            ("LOWER", "Lowercase", "Convert to lowercase"),
            ("TITLE", "Title Case", "Convert to title case"),
            ("ROUND", "Round Number", "Round to specified precision"),
            ("INT", "Integer", "Truncate decimal part"),
            ("NUMBER", "Format Number", "Format with separators"),
            ("METRIC_LENGTH", "Metric Length", "Format as metric length"),
            ("IMPERIAL_LENGTH", "Imperial Length", "Format as imperial length"),
            ("CUSTOM", "Custom Expression", "Create custom expression with functions"),
        ],
        default="NONE",
    )

    round_precision: bpy.props.StringProperty(
        name="Precision", description="Rounding precision (e.g. 0.1, 0.01, 0.001, 1, 10, 100)", default="0.01"
    )

    decimal_separator: bpy.props.StringProperty(
        name="Decimal Separator", description="Decimal separator character", default=".", maxlen=1
    )

    thousands_separator: bpy.props.StringProperty(
        name="Thousands Separator", description="Thousands separator character", default=",", maxlen=1
    )

    metric_decimals: bpy.props.IntProperty(
        name="Decimal Places", description="Number of decimal places to show", default=2, min=0, max=10
    )

    metric_precision: bpy.props.StringProperty(
        name="Metric Precision",
        description="Rounding precision for metric length (e.g. 0.1, 0.01, 0.001)",
        default="0.01",
    )

    imperial_precision: bpy.props.IntProperty(
        name="Fraction Precision", description="Imperial fraction precision (1/N)", default=4, min=1, max=64
    )

    imperial_input_unit: bpy.props.EnumProperty(
        name="Input Unit",
        items=[
            ("foot", "Feet", "Input value is in feet"),
            ("inch", "Inches", "Input value is in inches"),
        ],
        default="foot",
    )

    imperial_output_unit: bpy.props.EnumProperty(
        name="Output Format",
        items=[
            ("foot", "Feet and Inches", "Display as feet and inches"),
            ("inch", "Inches Only", "Display as inches only"),
        ],
        default="foot",
    )

    custom_expression: bpy.props.StringProperty(
        name="Custom Expression",
        description=("Custom expression using functions\n" "Use {{value}} as placeholder for the current row's value."),
        default='concat({{value}}, " - additional text")',
    )

    def invoke(self, context, event):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]
        if self.row_index >= len(literal_props.element_value_rows):
            return {"CANCELLED"}

        row = literal_props.element_value_rows[self.row_index]
        self._load_formatting_from_row(row)

        return context.window_manager.invoke_props_dialog(self, width=450)

    def _load_formatting_from_row(self, row):
        """Parse the formatted_value to load existing formatting settings"""
        import re

        formatted_value = row.formatted_value

        if not formatted_value or formatted_value == f"{{{{{row.element_key}}}}}":
            self.formatting_type = "NONE"
            return

        if formatted_value.startswith("``") and formatted_value.endswith("``"):
            expression = formatted_value[2:-2].strip()
        else:
            self.formatting_type = "NONE"
            return

        if match := re.match(r"upper\(\{\{[^}]+\}\}\)", expression):
            self.formatting_type = "UPPER"

        elif match := re.match(r"lower\(\{\{[^}]+\}\}\)", expression):
            self.formatting_type = "LOWER"

        elif match := re.match(r"title\(\{\{[^}]+\}\}\)", expression):
            self.formatting_type = "TITLE"

        elif match := re.match(r"int\(\{\{[^}]+\}\}\)", expression):
            self.formatting_type = "INT"

        elif match := re.match(r"round\(\{\{[^}]+\}\},\s*([^)]+)\)", expression):
            self.formatting_type = "ROUND"
            self.round_precision = match.group(1).strip()

        elif match := re.match(r"number\(\{\{[^}]+\}\},\s*([^,]+),\s*([^)]+)\)", expression):
            self.formatting_type = "NUMBER"
            self.decimal_separator = match.group(1).strip()
            self.thousands_separator = match.group(2).strip()

        elif match := re.match(r"metric_length\(\{\{[^}]+\}\},\s*([^,]+),\s*([^)]+)\)", expression):
            self.formatting_type = "METRIC_LENGTH"
            self.metric_precision = match.group(1).strip()
            self.metric_decimals = int(match.group(2).strip())

        elif match := re.match(r'imperial_length\(\{\{[^}]+\}\},\s*(\d+),\s*"([^"]+)",\s*"([^"]+)"\)', expression):
            self.formatting_type = "IMPERIAL_LENGTH"
            self.imperial_precision = int(match.group(1).strip())
            self.imperial_input_unit = match.group(2).strip()
            self.imperial_output_unit = match.group(3).strip()

        else:
            self.formatting_type = "CUSTOM"
            self.custom_expression = expression

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        props = tool.Drawing.get_text_props(obj)
        literal_props = props.literals[self.literal_prop_id]
        row = literal_props.element_value_rows[self.row_index]

        box = layout.box()
        box.label(text=f"Element Value: {row.element_key}", icon="PROPERTIES")

        layout.prop(self, "formatting_type")

        if self.formatting_type == "ROUND":
            layout.prop(self, "round_precision")
        elif self.formatting_type == "NUMBER":
            col = layout.column()
            col.prop(self, "decimal_separator")
            col.prop(self, "thousands_separator")
        elif self.formatting_type == "METRIC_LENGTH":
            col = layout.column()
            col.prop(self, "metric_precision")
            col.prop(self, "metric_decimals")
        elif self.formatting_type == "IMPERIAL_LENGTH":
            col = layout.column()
            col.prop(self, "imperial_precision")
            col.prop(self, "imperial_input_unit")
            col.prop(self, "imperial_output_unit")
        elif self.formatting_type == "CUSTOM":
            col = layout.column()
            col.prop(self, "custom_expression", text="")

        preview_box = layout.box()
        preview_box.label(text="Preview:", icon="PROPERTIES")
        formatted_syntax = self._generate_formatted_syntax(row.element_key)
        preview_box.label(text=formatted_syntax)

    def _generate_formatted_syntax(self, element_key: str) -> str:
        """Generate the formatted selector syntax based on current settings"""
        base_value = f"{{{{{element_key}}}}}"

        if self.formatting_type == "NONE":
            return base_value
        elif self.formatting_type == "UPPER":
            return f"``upper({base_value})``"
        elif self.formatting_type == "LOWER":
            return f"``lower({base_value})``"
        elif self.formatting_type == "TITLE":
            return f"``title({base_value})``"
        elif self.formatting_type == "ROUND":
            return f"``round({base_value}, {self.round_precision})``"
        elif self.formatting_type == "INT":
            return f"``int({base_value})``"
        elif self.formatting_type == "NUMBER":
            return f"``number({base_value}, {self.decimal_separator}, {self.thousands_separator})``"
        elif self.formatting_type == "METRIC_LENGTH":
            return f"``metric_length({base_value}, {self.metric_precision}, {self.metric_decimals})``"
        elif self.formatting_type == "IMPERIAL_LENGTH":
            return f'``imperial_length({base_value}, {self.imperial_precision}, "{self.imperial_input_unit}", "{self.imperial_output_unit}")``'
        elif self.formatting_type == "CUSTOM":
            custom_expr = self.custom_expression.replace("{{value}}", base_value)
            return f"``{custom_expr}``"

        return base_value

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        literal_props = props.literals[self.literal_prop_id]
        row = literal_props.element_value_rows[self.row_index]

        formatted_syntax = self._generate_formatted_syntax(row.element_key)
        row.formatted_value = formatted_syntax

        tool.Blender.update_viewport()
        return {"FINISHED"}


class ApplyElementValueRowsToLiteral(bpy.types.Operator):
    bl_idname = "bim.apply_element_value_rows_to_literal"
    bl_label = "Apply Element Values to Literal"
    bl_description = "Concatenate all element value rows and apply to the literal"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        if not obj:
            return {"CANCELLED"}

        props = tool.Drawing.get_text_props(obj)
        if self.literal_prop_id >= len(props.literals):
            return {"CANCELLED"}

        literal_props = props.literals[self.literal_prop_id]

        parts = []
        for row in literal_props.element_value_rows:
            if row.element_key:
                if row.category == "Custom String":
                    parts.append(row.element_key)
                else:
                    if row.formatted_value and row.formatted_value != f"{{{{{row.element_key}}}}}":
                        updated_formatted = self._update_formatted_value(row.element_key, row.formatted_value)
                        row.formatted_value = updated_formatted
                        value_part = updated_formatted
                    else:
                        default_format = f"{{{{{row.element_key}}}}}"
                        row.formatted_value = default_format
                        value_part = default_format

                    parts.append(row.separator + value_part)

        concatenated_value = "".join(parts)

        for attr in literal_props.attributes:
            if attr.name == "Literal":
                attr.string_value = concatenated_value
                break

        tool.Blender.update_viewport()
        return {"FINISHED"}

    def _update_formatted_value(self, new_element_key: str, old_formatted_value: str) -> str:
        """
        Update formatted value by replacing old element key placeholders with new one.
        This preserves formatting functions like upper(), round(), etc.
        """
        import re

        pattern = r"\{\{[^}]+\}\}"

        new_base_value = f"{{{{{new_element_key}}}}}"
        updated_value = re.sub(pattern, new_base_value, old_formatted_value)

        return updated_value


class ShowElementValuesInstructions(bpy.types.Operator):
    bl_idname = "bim.show_element_values_instructions"
    bl_label = "Element Values - Quick Start Guide"
    bl_description = "Show general tips and formatting instructions for element values"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=700)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Element Values - Building Custom Literals", icon="INFO")

        box = layout.box()
        row = box.row()
        row.label(text="Full Documentation:", icon="URL")
        row.operator("wm.url_open", text="IFC Selector Syntax Guide", icon="URL").url = (
            "https://docs.ifcopenshell.org/ifcopenshell-python/selector_syntax.html#getting-element-values"
        )

        box = layout.box()
        box.label(text="WORKFLOW: BUILDING LITERALS WITH ROWS", icon="SEQUENCE")
        col = box.column(align=True)
        col.scale_y = 0.85
        col.label(text="1. Select a category from the dropdown (Basic, Property Sets, etc.)")
        col.label(text="2. Click 'Add Element' to create a new row")
        col.label(text="3. Use the magnifying glass icon to browse available values for that category")
        col.label(text="4. Optionally, click the format icon (star) to apply formatting (uppercase, round, etc.)")
        col.label(text="5. Repeat to add more rows, each with its own separator text")
        col.label(text="6. Click 'Apply to Literal' to concatenate all rows into the final text")

        box = layout.box()
        box.label(text="SEPARATORS & CUSTOM TEXT", icon="THREE_DOTS")
        col = box.column(align=True)
        col.scale_y = 0.85
        col.label(text="• Each row has a separator field (shown before the value)")
        col.label(text="• Default separator is ' - ' but you can change it to spaces, commas, newlines, etc.")
        col.label(text="• Use 'Custom String' category to add plain text without any element key")
        col.label(text="• Example: 'Custom String' row with 'Wall: ' → 'Custom String' with 'Type-' → 'Name' key")
        col.label(text="• Result: 'Wall: Type-WALL-001' (combining custom text with element values)")

        box = layout.box()
        box.label(text="SELECTING SOURCE ELEMENT", icon="EYEDROPPER")
        col = box.column(align=True)
        col.scale_y = 0.85
        col.label(text="• By default, uses the assigned product (if any) or the text annotation object itself")
        col.label(text="• Use the eyedropper next to 'Element Values:' to select a different object")
        col.label(text="• Useful for referencing values from related elements (like types, spaces, storeys)")
        col.label(text="• The 'Source:' label shows which object is currently being used")

        box = layout.box()
        box.label(text="FORMATTING FUNCTIONS (click star icon on any row)", icon="SHADERFX")
        col = box.column(align=True)
        col.scale_y = 0.8

        col.label(text="Text Case:")
        col.label(text="  • Uppercase, Lowercase, Title Case")
        col.label(text="  Example: upper({{Name}}) → 'WALL-001'")

        col.separator(factor=0.5)
        col.label(text="Numbers:")
        col.label(text="  • Round - Round to precision (0.01, 0.1, 1, 10, etc.)")
        col.label(text="  • Integer - Remove decimal part")
        col.label(text="  • Number - Format with separators (1,234.56)")

        col.separator(factor=0.5)
        col.label(text="Lengths:")
        col.label(text="  • Metric Length - Format as metric with units (45.50 m²)")
        col.label(text="  • Imperial Length - Format as feet-inches (10'-6\")")

        col.separator(factor=0.5)
        col.label(text="Custom Expression:")
        col.label(text="  • Write your own using functions: concat(), upper(), round(), etc.")
        col.label(text="  • Use {{value}} as placeholder for the current row's value")

        box = layout.box()
        box.label(text="TIPS & ADVANCED USAGE", icon="LIGHTPROBE_VOLUME")
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="• Category counts show available values: 'Property Sets (12)'")
        col.label(text="• Regex patterns work in property set names: /Pset_.*Common/")
        col.label(text="• Combine multiple formatted rows for complex labels")
        col.label(text="• Each row remembers its own formatting when you re-edit it")

    def execute(self, context):
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Parametric dimension operators
# ---------------------------------------------------------------------------


class DrawParametricDimension(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    """Draw a parametric dimension string anchored to IFC element geometry.

    Click on IFC element faces to place dimension vertices one by one using the
    same snap system as wall and slab drawing.  Each confirmed point is stored
    as a parametric anchor in ``BBIM_Dimension`` so the dimension
    recomputes automatically when the referenced elements move.

    RMB or ENTER to finish; ESC to cancel without creating an annotation.
    """

    bl_idname = "bim.draw_parametric_dimension"
    bl_label = "Draw Parametric Dimension"
    bl_options = {"REGISTER", "UNDO"}

    _SNAP_MODES = ("FACE", "LAYER", "EDGE", "VERTEX")

    if TYPE_CHECKING:
        _anchors: list
        _shape_cache: dict
        _snap_mode: str
        _ifc_snap_candidate: object  # Optional[dict]
        _draw_handler: object  # SpaceView3D draw handler handle

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file loaded.")
            return False
        if not context.scene.camera or not tool.Ifc.get_entity(context.scene.camera):
            cls.poll_message_set("No active drawing.")
            return False
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self._anchors = []
        self._shape_cache = {}
        self._force_perpendicular = False
        self._anchor0_normal = None   # (nx, ny, nz) world-space face normal of anchor[0]
        self._anchor0_pt = None       # (x, y, z) world-space position of anchor[0]
        self._snap_mode = "FACE"
        self._ifc_snap_candidate = None
        self._draw_handler = None
        self._snap_cand_obj_ptr: int = -1   # Blender object pointer for cached snap cands
        self._snap_cand_cache: list = []    # cached get_layer/profile_snap_candidates result
        self._snap_cand_multi_cache: dict = {}  # ptr → candidates for coplanar-edge nearby objects

    # ------------------------------------------------------------------
    # Snap → anchor bridge

    def _snap_to_anchor(self, snap: dict) -> dict:
        """Convert a PolylineOperator snap candidate to a BBIM_Dimension anchor dict."""
        import ifcopenshell.api.drawing as drawing_api

        obj = snap.get("object")
        element = tool.Ifc.get_entity(obj) if obj else None
        pt_world = snap["point"]

        if element and hasattr(element, "GlobalId") and obj.data and hasattr(obj.data, "polygons"):
            hit_m = (float(pt_world.x), float(pt_world.y), float(pt_world.z))

            face_index = snap.get("face_index")
            if face_index is None or face_index >= len(obj.data.polygons):
                # Vertex / edge snap: seed from closest face.
                local_pt = obj.matrix_world.inverted() @ pt_world
                ok, _loc, _n, face_index = obj.closest_point_on_mesh(local_pt)
                if not ok:
                    face_index = None

            # Prefer faces perpendicular to the camera rather than faces that
            # directly face the camera (e.g. top of a wall in plan view).
            face_index = _prefer_perp_face_index(obj, pt_world, face_index)

            if face_index is not None and face_index < len(obj.data.polygons):
                normal_local = obj.data.polygons[face_index].normal
            else:
                normal_local = Vector((0.0, 0.0, 1.0))

            normal_world = (obj.matrix_world.to_3x3() @ normal_local).normalized()
            normal_m = (float(normal_world.x), float(normal_world.y), float(normal_world.z))
            placement_override = {element.id(): np.array(obj.matrix_world)}

            return drawing_api.build_anchor_from_hit(
                tool.Ifc.get(), element, hit_m, normal_m,
                shape_cache=self._shape_cache,
                placement_override=placement_override,
            )

        # Axis / plane snap, or non-IFC object: store a free world point.
        import ifcopenshell.api.drawing as drawing_api
        return drawing_api.make_world_anchor([float(pt_world.x), float(pt_world.y), float(pt_world.z)])

    # ------------------------------------------------------------------
    # Point insertion — capture anchor in sync with polyline point

    def handle_inserting_polyline(self, context, event):
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        count_before = len(polyline_data[0].polyline_points) if polyline_data else 0

        # Capture snap state BEFORE super() so we have it even if event processing clears it.
        snap = self.snapping_points[0] if self.snapping_points else None
        is_mouse_click = (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type == "LEFTMOUSE"
        )

        super().handle_inserting_polyline(context, event)

        if not polyline_data:
            return
        count_after = len(polyline_data[0].polyline_points)

        if count_after > count_before:
            # A point was inserted — build its anchor.
            if is_mouse_click and self._ifc_snap_candidate:
                self._anchors.append(self._build_ifc_anchor(self._ifc_snap_candidate))
            elif is_mouse_click and snap and snap.get("type") not in {"Axis", "Plane"}:
                self._anchors.append(self._snap_to_anchor(snap))
            else:
                # Keyboard-typed coordinate or close-loop: world anchor at the stored point.
                import ifcopenshell.api.drawing as drawing_api
                pt = polyline_data[0].polyline_points[-1]
                self._anchors.append(drawing_api.make_world_anchor([float(pt.x), float(pt.y), float(pt.z)]))

            # After anchor[0] is set, extract its face normal for the perp constraint.
            if self._force_perpendicular and len(self._anchors) == 1:
                self._update_perp_constraint()
        elif count_after < count_before and self._anchors:
            # BACKSPACE removed a point.
            self._anchors.pop()
            # Reset constraint if we backspaced past anchor[0].
            if len(self._anchors) == 0:
                self._anchor0_normal = None
                self._anchor0_pt = None

    # ------------------------------------------------------------------
    # Perpendicular-to-face constraint helpers

    def _update_perp_constraint(self) -> None:
        """Extract the face normal from anchor[0] and store it as the constraint axis."""
        import math
        from mathutils import Vector
        a = self._anchors[0] if self._anchors else None
        if not a or a.get("type") != "FACE":
            return
        addr = a.get("addr") or {}
        pt = a.get("pt")
        if not pt:
            return

        method = addr.get("method", "FACE_NORMAL")
        guid = a.get("guid")

        if method == "LAYER_BOUNDARY":
            # Derive the thickness-axis normal from the element's LayerSetDirection.
            if not guid:
                return
            try:
                file = tool.Ifc.get()
                element = file.by_guid(guid)
                import ifcopenshell.util.element as _ifc_elem
                usage = _ifc_elem.get_material(element, should_inherit=True)
                if not usage or not usage.is_a("IfcMaterialLayerSetUsage"):
                    return
                axis = getattr(usage, "LayerSetDirection", None) or "AXIS2"
                if axis == "AXIS1":
                    normal_local = (1.0, 0.0, 0.0)
                elif axis == "AXIS3":
                    normal_local = (0.0, 0.0, 1.0)
                else:
                    normal_local = (0.0, 1.0, 0.0)
                obj = tool.Ifc.get_object(element)
                if obj:
                    nw = obj.matrix_world.to_3x3() @ Vector(normal_local)
                    nw.normalize()
                    n: tuple = (nw.x, nw.y, nw.z)
                else:
                    n = normal_local
            except Exception:
                return
        else:
            normal_local = addr.get("normal_local")
            if not normal_local:
                return
            n = normal_local
            if guid:
                try:
                    file = tool.Ifc.get()
                    element = file.by_guid(guid)
                    obj = tool.Ifc.get_object(element)
                    if obj:
                        nw = obj.matrix_world.to_3x3() @ Vector(normal_local)
                        nw.normalize()
                        n = (nw.x, nw.y, nw.z)
                except Exception:
                    pass

        mag = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        if mag < 1e-12:
            return
        self._anchor0_normal = (n[0] / mag, n[1] / mag, n[2] / mag)
        self._anchor0_pt = tuple(pt)

    def _apply_perp_constraint(self) -> None:
        """Project the current snap point onto the constraint line when active."""
        if not self._force_perpendicular or not self._anchor0_normal or not self._anchor0_pt:
            return
        if not self._anchors:   # constraint not yet active (no anchor[0] yet)
            return
        if not self.snapping_points:
            return
        snap = self.snapping_points[0]
        if not snap or not snap.get("point"):
            return
        p = snap["point"]
        base = self._anchor0_pt
        n = self._anchor0_normal
        t = (p.x - base[0]) * n[0] + (p.y - base[1]) * n[1] + (p.z - base[2]) * n[2]
        constrained = Vector((base[0] + t * n[0], base[1] + t * n[1], base[2] + t * n[2]))
        snap["point"] = constrained

    # ------------------------------------------------------------------
    # IFC-native snap for LAYER / VERTEX / EDGE modes

    @staticmethod
    def _snap_on_coplanar_faces(obj, hit_pt_world, tol_z=1e-3):
        """Return FACE snap candidates for vertical mesh faces with an edge at hit_pt_world's Z.

        Finds faces that are edge-on to the camera (perpendicular to the floor plane) and
        whose bottom edge is coplanar with the hovered floor surface, then projects the
        hit point onto each such face's plane to get the snap position.
        """
        from mathutils import Vector
        mx = obj.matrix_world
        mesh = obj.data
        target_z = float(hit_pt_world.z)
        hit_pt = Vector(hit_pt_world)
        candidates = []
        for poly in mesh.polygons:
            normal_w = (mx.to_3x3() @ poly.normal).normalized()
            if abs(normal_w.z) > 0.9:
                continue
            verts_w = [mx @ mesh.vertices[vi].co for vi in poly.vertices]
            n = len(verts_w)
            has_coplanar_edge = any(
                abs(verts_w[i].z - target_z) <= tol_z and abs(verts_w[(i + 1) % n].z - target_z) <= tol_z
                for i in range(n)
            )
            if not has_coplanar_edge:
                continue
            face_center_w = sum(verts_w, Vector((0.0, 0.0, 0.0))) / n
            dist = (hit_pt - face_center_w).dot(normal_w)
            snapped_pt = hit_pt - normal_w * dist
            candidates.append({
                "type": "FACE",
                "snap_world": (snapped_pt.x, snapped_pt.y, snapped_pt.z),
                "snap": "FACE",
                "face_verts": [tuple(v) for v in verts_w],
            })
        return candidates

    @staticmethod
    def _pt_in_obj_bbox(obj, pt_world, tol=1e-3):
        """Return True if pt_world is inside obj's world-space bounding box."""
        try:
            local_pt = obj.matrix_world.inverted() @ pt_world
        except Exception:
            return False
        bb = obj.bound_box  # 8 corners in local space
        xs = [v[0] for v in bb]
        ys = [v[1] for v in bb]
        zs = [v[2] for v in bb]
        return (
            min(xs) - tol <= local_pt.x <= max(xs) + tol
            and min(ys) - tol <= local_pt.y <= max(ys) + tol
            and min(zs) - tol <= local_pt.z <= max(zs) + tol
        )

    def _compute_ifc_snap_candidate(self, context, event) -> "Optional[dict]":
        """Return an IFC-native snap candidate for the current snap mode, or None."""
        if not self.snapping_points:
            return None

        snap = self.snapping_points[0]
        hit_obj = snap.get("object")
        hit_pt = snap.get("point")

        from bpy_extras.view3d_utils import location_3d_to_region_2d
        import ifcopenshell.api.drawing as drawing_api

        region = context.region
        rv3d = context.region_data
        mx, my = event.mouse_region_x, event.mouse_region_y

        # ----------------------------------------------------------------
        # FACE mode: no IFC snap on the primary hit object, but look for
        # coplanar-edge candidates from nearby objects (e.g. a wall whose
        # bottom edge is coplanar with the hovered floor surface).
        # Uses direct mesh edge projection rather than get_profile_snap_candidates
        # so the snap tracks cursor position along the edge, not just fixed vertices.
        # ----------------------------------------------------------------
        if self._snap_mode == "FACE":
            if hit_pt is None or not self.objs_2d_bbox:
                return None
            nearby_cands = []
            extra_count = 0
            for obj, _bbox2d in self.objs_2d_bbox:
                if extra_count >= 4:
                    break
                if obj is hit_obj:
                    continue
                if obj.data is None or not isinstance(obj.data, bpy.types.Mesh):
                    continue
                extra_elem = tool.Ifc.get_entity(obj)
                if not extra_elem or not hasattr(extra_elem, "GlobalId"):
                    continue
                in_bbox = self._pt_in_obj_bbox(obj, hit_pt)
                if not in_bbox:
                    continue
                face_cands = self._snap_on_coplanar_faces(obj, hit_pt)
                nearby_cands.extend((c, extra_elem, obj) for c in face_cands)
                extra_count += 1

            _FACE_THRESH_D2 = 30 * 30
            best_cand, best_elem, best_obj, best_d2 = None, None, None, float("inf")
            for cand, elem, obj in nearby_cands:
                sp = location_3d_to_region_2d(region, rv3d, Vector(cand["snap_world"]))
                if sp is None:
                    continue
                d2 = (sp.x - mx) ** 2 + (sp.y - my) ** 2
                if d2 < best_d2 and d2 < _FACE_THRESH_D2:
                    best_d2 = d2
                    best_cand = cand
                    best_elem = elem
                    best_obj = obj
            if best_cand is None:
                return None
            result = dict(best_cand)
            result["element"] = best_elem
            result["obj"] = best_obj
            return result

        # ----------------------------------------------------------------
        # LAYER / VERTEX / EDGE modes
        # ----------------------------------------------------------------
        if not hit_obj:
            return None
        element = tool.Ifc.get_entity(hit_obj)
        if not element or not hasattr(element, "GlobalId"):
            return None

        # Recompute expensive candidate geometry only when the hovered object changes.
        obj_ptr = hit_obj.as_pointer()
        if obj_ptr != self._snap_cand_obj_ptr:
            file = tool.Ifc.get()
            placement_override = {element.id(): np.array(hit_obj.matrix_world)}
            if self._snap_mode == "LAYER":
                self._snap_cand_cache = drawing_api.get_layer_snap_candidates(file, element, placement_override)
            else:
                self._snap_cand_cache = drawing_api.get_profile_snap_candidates(file, element, placement_override)
            self._snap_cand_obj_ptr = obj_ptr

        if self._snap_mode == "LAYER":
            all_layer_cands = [(c, element, hit_obj) for c in self._snap_cand_cache]
            if hit_pt is not None and self.objs_2d_bbox:
                file = tool.Ifc.get()
                extra_count = 0
                for obj, _bbox2d in self.objs_2d_bbox:
                    if extra_count >= 4:
                        break
                    if obj is hit_obj:
                        continue
                    if obj.data is None or not isinstance(obj.data, bpy.types.Mesh):
                        continue
                    extra_elem = tool.Ifc.get_entity(obj)
                    if not extra_elem or not hasattr(extra_elem, "GlobalId"):
                        continue
                    if not self._pt_in_obj_bbox(obj, hit_pt):
                        continue
                    extra_ptr = obj.as_pointer()
                    if extra_ptr not in self._snap_cand_multi_cache:
                        placement_override = {extra_elem.id(): np.array(obj.matrix_world)}
                        self._snap_cand_multi_cache[extra_ptr] = drawing_api.get_layer_snap_candidates(
                            file, extra_elem, placement_override
                        )
                    all_layer_cands.extend((c, extra_elem, obj) for c in self._snap_cand_multi_cache[extra_ptr])
                    extra_count += 1
            best_cand, best_elem, best_obj, best_d2 = None, None, None, float("inf")
            for cand, elem, obj in all_layer_cands:
                sp = location_3d_to_region_2d(region, rv3d, Vector(cand["snap_world"]))
                if sp is None:
                    continue
                d2 = (sp.x - mx) ** 2 + (sp.y - my) ** 2
                if d2 < best_d2:
                    best_d2 = d2
                    best_cand = cand
                    best_elem = elem
                    best_obj = obj
            if best_cand is None:
                return None
            result = dict(best_cand)
            result["method"] = "LAYER_BOUNDARY"
            result["element"] = best_elem
            result["obj"] = best_obj
            return result

        # VERTEX or EDGE — profile-based candidates.
        # Build a tagged list of (candidate, element, obj) so the best match from
        # any object carries the right element reference into _build_ifc_anchor.
        all_cands = [(c, element, hit_obj) for c in self._snap_cand_cache]

        # Also query nearby objects whose 3D bbox contains the hit point.
        if hit_pt is not None and self.objs_2d_bbox:
            file = tool.Ifc.get()
            extra_count = 0
            for obj, _bbox2d in self.objs_2d_bbox:
                if extra_count >= 4:
                    break
                if obj is hit_obj:
                    continue
                if obj.data is None or not isinstance(obj.data, bpy.types.Mesh):
                    continue
                extra_elem = tool.Ifc.get_entity(obj)
                if not extra_elem or not hasattr(extra_elem, "GlobalId"):
                    continue
                in_bbox = self._pt_in_obj_bbox(obj, hit_pt)
                if not in_bbox:
                    continue
                extra_ptr = obj.as_pointer()
                if extra_ptr not in self._snap_cand_multi_cache:
                    placement_override = {extra_elem.id(): np.array(obj.matrix_world)}
                    self._snap_cand_multi_cache[extra_ptr] = drawing_api.get_profile_snap_candidates(
                        file, extra_elem, placement_override
                    )
                all_cands.extend((c, extra_elem, obj) for c in self._snap_cand_multi_cache[extra_ptr])
                extra_count += 1

        best_cand, best_elem, best_obj, best_d2 = None, None, None, float("inf")
        for cand, elem, obj in all_cands:
            if cand["type"] != self._snap_mode:
                continue
            sp = location_3d_to_region_2d(region, rv3d, Vector(cand["snap_world"]))
            if sp is None:
                continue
            d2 = (sp.x - mx) ** 2 + (sp.y - my) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best_cand = cand
                best_elem = elem
                best_obj = obj
        if best_cand is None:
            return None
        result = dict(best_cand)
        result["element"] = best_elem
        result["obj"] = best_obj
        return result

    def _build_ifc_anchor(self, candidate: dict) -> dict:
        """Build the correct anchor type from an IFC snap candidate."""
        import ifcopenshell.api.drawing as drawing_api
        element = candidate.get("element")
        if not element:
            pt = candidate.get("snap_world", (0.0, 0.0, 0.0))
            return drawing_api.make_world_anchor(list(pt))
        file = tool.Ifc.get()
        if candidate.get("method") == "LAYER_BOUNDARY":
            return drawing_api.build_anchor_from_layer_boundary(file, element, candidate)
        snap_kind = candidate.get("snap")
        if snap_kind == "VERTEX" and candidate.get("profile_x_m") is not None:
            return drawing_api.build_anchor_from_profile_vert(file, element, candidate)
        if snap_kind == "EDGE" and candidate.get("profile_x_m") is not None:
            return drawing_api.build_anchor_from_profile_edge(file, element, candidate)
        pt = candidate.get("snap_world", (0.0, 0.0, 0.0))
        return drawing_api.make_world_anchor(list(pt))

    def _update_snap_draw_data(self) -> None:
        """Populate _snap_draw_data so _draw_snap_indicator_global draws the right indicator."""
        _snap_draw_data.clear()

        if self._ifc_snap_candidate:
            cand = self._ifc_snap_candidate
            if cand.get("method") == "LAYER_BOUNDARY":
                _snap_draw_data.update({
                    "type": "LAYER",
                    "seam_corners": cand.get("seam_corners", []),
                    "snap_world": cand.get("snap_world"),
                })
            elif cand.get("snap") == "FACE":
                _snap_draw_data.update({
                    "type": "FACE",
                    "face_verts": cand.get("face_verts", []),
                    "snap_world": cand.get("snap_world"),
                })
            elif cand.get("snap") == "EDGE":
                _snap_draw_data.update({
                    "type": "EDGE",
                    "v0": cand.get("v0"),
                    "v1": cand.get("v1"),
                    "snap_world": cand.get("snap_world"),
                })
            else:
                _snap_draw_data.update({
                    "type": "VERTEX",
                    "snap_world": cand.get("snap_world"),
                })
            return

        # FACE mode: outline the hovered face polygon
        if not self.snapping_points:
            return
        snap = self.snapping_points[0]
        hit_obj = snap.get("object")
        if not hit_obj or not hasattr(hit_obj.data, "polygons"):
            return
        pt_world = snap.get("point")
        face_index = snap.get("face_index")
        if face_index is None or face_index >= len(hit_obj.data.polygons):
            if pt_world is not None:
                local_pt = hit_obj.matrix_world.inverted() @ pt_world
                try:
                    ok, _loc, _n, face_index = hit_obj.closest_point_on_mesh(local_pt)
                except RuntimeError:
                    return
                if not ok:
                    return
        face_index = _prefer_perp_face_index(hit_obj, pt_world, face_index)
        if face_index is None or face_index >= len(hit_obj.data.polygons):
            return
        face = hit_obj.data.polygons[face_index]
        mx = hit_obj.matrix_world
        face_verts = [tuple(mx @ hit_obj.data.vertices[vi].co) for vi in face.vertices]
        _snap_draw_data.update({"type": "FACE", "face_verts": face_verts})

    def _cleanup(self, context) -> None:
        _snap_draw_data.clear()
        if self._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, "WINDOW")
            self._draw_handler = None
        context.workspace.status_text_set(None)

    def _set_status(self, context) -> None:
        mode_label = self._snap_mode.capitalize()
        context.workspace.status_text_set(
            f"[Snap: {mode_label}]  TAB: cycle snap  |  LMB: place point"
            "  |  0-9: enter value  |  BACKSPACE: undo last  |  RMB/ENTER: finish  |  ESC: cancel"
        )

    # ------------------------------------------------------------------
    # Finalize: create IfcAnnotation + BBIM_Dimension pset

    def _create_dimension_from_polyline(self, context) -> None:
        import ifcopenshell.api.drawing as drawing_api

        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        if not polyline_data or len(polyline_data[0].polyline_points) < 2:
            self.report({"WARNING"}, "Need at least 2 points for a dimension.")
            return

        polyline_points = list(polyline_data[0].polyline_points)

        dprops = tool.Drawing.get_document_props()
        drawing = dprops.get_active_drawing()
        if not drawing:
            self.report({"WARNING"}, "No active drawing.")
            return

        props = tool.Drawing.get_annotation_props()
        relating_type = (
            tool.Ifc.get().by_id(int(props.relating_type_id))
            if props.relating_type_id and props.relating_type_id != "0"
            else None
        )

        obj = core.add_annotation(
            tool.Ifc, tool.Collector, tool.Drawing,
            drawing=drawing,
            object_type="DIMENSION",
            relating_type=relating_type,
            enable_editing=False,
        )
        if not obj:
            return

        annotation = tool.Ifc.get_entity(obj)
        if not annotation:
            return

        # World-space metres points straight from the polyline.
        resolved_pts_m = [(pt.x, pt.y, pt.z) for pt in polyline_points]

        # Update Blender curve spline AND the IFC IfcIndexedPolyCurve/IfcPolyline.
        _update_blender_curve(annotation, resolved_pts_m)

        # Pad anchors to match point count (e.g. if first point was keyboard-typed
        # before any snap data was available).
        anchors = list(self._anchors)
        while len(anchors) < len(resolved_pts_m):
            anchors.append(drawing_api.make_world_anchor(list(resolved_pts_m[len(anchors)])))

        file = tool.Ifc.get()
        pset_data = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
        if not pset_data:
            ifcopenshell.api.run("pset.add_pset", file, product=annotation, name="BBIM_Dimension")
            pset_data = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
        pset_entity = file.by_id(pset_data["id"])
        pset_props = {"Anchors": json.dumps(anchors)}
        if self._force_perpendicular:
            pset_props["ForcePerpendicularToFace"] = True
        ifcopenshell.api.run("pset.edit_pset", file, pset=pset_entity, properties=pset_props)

        if self._force_perpendicular:
            placement_override: dict = {}
            for a in anchors:
                guid = a.get("guid")
                if not guid:
                    continue
                try:
                    elem = file.by_guid(guid)
                    elem_obj = tool.Ifc.get_object(elem)
                    if elem_obj:
                        placement_override[elem.id()] = np.array(elem_obj.matrix_world)
                except Exception:
                    pass
            resolved_pts = drawing_api.regenerate_dimension(
                file, annotation,
                shape_cache=getattr(self, "_shape_cache", None),
                placement_override=placement_override,
            )
            if resolved_pts:
                _update_blender_curve(annotation, resolved_pts)

        from bonsai.bim.module.drawing import handler as _drawing_handler
        _drawing_handler.invalidate_dim_index()

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        context.view_layer.objects.active = obj

    # ------------------------------------------------------------------
    # Modal loop — same pattern as DrawPolylineWall

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_mouse_move(context, event)
        self.choose_axis(event)
        self.handle_snap_selection(context, event)
        self._apply_perp_constraint()

        # TAB: cycle snap mode when not in keyboard-input mode.
        # Consume both PRESS and RELEASE so the RELEASE never reaches
        # handle_keyboard_input (which would activate input mode on TAB RELEASE).
        # When is_input_on is True, TAB passes through to cycle input fields as usual.
        if event.type == "TAB" and not self.tool_state.is_input_on:
            if event.value == "PRESS":
                cur = self._SNAP_MODES.index(self._snap_mode)
                self._snap_mode = self._SNAP_MODES[(cur + 1) % len(self._SNAP_MODES)]
                self._ifc_snap_candidate = None
                self._snap_cand_obj_ptr = -1       # invalidate cache: LAYER vs VERTEX/EDGE differ
                self._snap_cand_multi_cache = {}   # invalidate nearby-object cache too
                self._set_status(context)
            return {"RUNNING_MODAL"}

        # For LAYER / VERTEX / EDGE modes, compute an IFC-native snap candidate and
        # override the polyline cursor position so the visual tracks the IFC point.
        # Only recompute on mouse moves — key events don't change the hit object.
        if event.type == "MOUSEMOVE":
            self._ifc_snap_candidate = self._compute_ifc_snap_candidate(context, event)
        if self._ifc_snap_candidate and self.snapping_points:
            wp = self._ifc_snap_candidate.get("snap_world")
            if wp:
                self.snapping_points[0]["point"] = Vector(wp)

        self._update_snap_draw_data()

        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            self._create_dimension_from_polyline(context)
            self.tool_state.plane_method = None
            PolylineDecorator.uninstall()
            tool.Polyline.clear_polyline()
            self._cleanup(context)
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)
        self.handle_inserting_polyline(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            self._cleanup(context)
            return cancel

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _init_snapping_points(self, context, event):
        """Skip the full BVH snap at startup — use a plane-intersection placeholder.

        handle_mouse_move populates snapping_points properly after the first few
        MOUSEMOVE events, so this placeholder only needs to survive until then.
        We must also populate snap_mouse_point (a Blender prop collection) because
        calculate_distance_and_angle accesses it immediately after invoke.
        """
        from mathutils import Vector
        plane_pt = tool.Raycast.ray_cast_to_plane(context, event, Vector((0, 0, 0)), Vector((0, 0, 1)))
        snap = {"type": "Plane", "point": plane_pt, "object": None, "group": "Plane", "distance": 10}
        self.snapping_points = [snap]
        tool.Snap.update_snapping_point(plane_pt, "Plane")

    def _invoke(self, context, event):
        super().invoke(context, event)
        self._force_perpendicular = tool.Drawing.get_annotation_props().force_perpendicular_to_face
        _snap_draw_data.clear()
        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            _draw_snap_indicator_global, (), "WINDOW", "POST_VIEW"
        )
        self._set_status(context)
        return {"RUNNING_MODAL"}


def _prefer_perp_face_index(
    obj: "bpy.types.Object",
    hit_world: "Vector",
    current_index: "Optional[int]",
    world_matrix=None,
) -> "Optional[int]":
    """Return the polygon index most perpendicular to the camera near *hit_world*.

    If the camera is unavailable or the current face is already sufficiently
    perpendicular (|dot| < 0.5), returns *current_index* unchanged.
    *world_matrix* overrides ``obj.matrix_world``; useful when *obj* is a mesh
    inside a collection instance whose effective transform differs from its own
    ``matrix_world``.
    """
    camera = bpy.context.scene.camera
    if not camera or not obj.data or not hasattr(obj.data, "polygons"):
        return current_index

    cam_view = (camera.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    mx = world_matrix if world_matrix is not None else obj.matrix_world
    mx3 = mx.to_3x3()

    if current_index is not None and current_index < len(obj.data.polygons):
        current_n = (mx3 @ obj.data.polygons[current_index].normal).normalized()
        if abs(current_n.dot(cam_view)) < 0.5:
            return current_index

    best_idx = current_index
    best_score = -1.0
    for i, poly in enumerate(obj.data.polygons):
        n_world = (mx3 @ poly.normal).normalized()
        perp = 1.0 - abs(n_world.dot(cam_view))
        if perp < 0.5:
            continue
        dist = (mx @ poly.center - hit_world).length
        score = perp - dist / 4.0
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


# Module-level draw data so the GPU callback never touches the operator RNA struct.
_snap_draw_data: dict = {}



def _draw_snap_indicator_global():
    """GPU draw callback (POST_VIEW) — draws face outline, edge, or vertex dot."""
    data = _snap_draw_data
    if not data or not data.get("type"):
        return
    import gpu
    from gpu_extras.batch import batch_for_shader
    try:
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("ALWAYS")
        snap_type = data["type"]

        if snap_type == "FACE":
            verts = data.get("face_verts", [])
            if len(verts) >= 3:
                lines = []
                for i in range(len(verts)):
                    lines.append(verts[i])
                    lines.append(verts[(i + 1) % len(verts)])
                shader.bind()
                shader.uniform_float("color", (0.2, 0.55, 1.0, 0.9))
                gpu.state.line_width_set(4.0)
                batch_for_shader(shader, "LINES", {"pos": lines}).draw(shader)

        elif snap_type == "EDGE":
            v0, v1 = data.get("v0"), data.get("v1")
            if v0 and v1:
                shader.bind()
                shader.uniform_float("color", (1.0, 0.65, 0.0, 1.0))
                gpu.state.line_width_set(6.0)
                batch_for_shader(shader, "LINES", {"pos": [v0, v1]}).draw(shader)
                gpu.state.point_size_set(12.0)
                batch_for_shader(shader, "POINTS", {"pos": [v0, v1]}).draw(shader)

        elif snap_type == "VERTEX":
            pt = data.get("snap_world")
            if pt:
                shader.bind()
                shader.uniform_float("color", (1.0, 0.2, 0.4, 1.0))
                gpu.state.point_size_set(20.0)
                batch_for_shader(shader, "POINTS", {"pos": [pt]}).draw(shader)

        elif snap_type == "LAYER":
            corners = data.get("seam_corners", [])
            pt = data.get("snap_world")
            shader.bind()
            shader.uniform_float("color", (0.2, 0.9, 0.5, 1.0))
            n = len(corners)
            if n >= 2:
                lines = []
                for i in range(n):
                    lines.append(corners[i])
                    lines.append(corners[(i + 1) % n])
                gpu.state.line_width_set(5.0)
                batch_for_shader(shader, "LINES", {"pos": lines}).draw(shader)
                gpu.state.point_size_set(10.0)
                batch_for_shader(shader, "POINTS", {"pos": corners}).draw(shader)
            if pt:
                gpu.state.point_size_set(20.0)
                batch_for_shader(shader, "POINTS", {"pos": [pt]}).draw(shader)

    except Exception:
        pass
    finally:
        try:
            gpu.state.depth_test_set("LESS_EQUAL")
            gpu.state.blend_set("NONE")
            gpu.state.line_width_set(1.0)
        except Exception:
            pass


class SetDimensionAnchor(bpy.types.Operator, tool.Ifc.Operator):
    """Interactively anchor dimension vertices to IFC element faces.

    Two-phase modal workflow (all in Object Mode):
      1. Run the operator with a dimension annotation selected.
      2. Click a vertex ON the dimension line to select it.
      3. Hover over IFC elements — the nearest candidate is highlighted.
         TAB cycles through overlapping candidates under the cursor.
         Click to anchor the highlighted element face to that vertex.
         ALT+Click sets a free world-point anchor instead.
      4. Repeat steps 2-3 for more vertices.
      5. RMB or ESC to finish.
    """

    bl_idname = "bim.set_dimension_anchor"
    bl_label = "Set Dimension Anchor"
    bl_options = {"REGISTER", "UNDO"}

    anchor_index: bpy.props.IntProperty(default=-1)  # -1 = begin with vertex-pick phase

    if TYPE_CHECKING:
        anchor_index: int

    _annotation: Optional[ifcopenshell.entity_instance] = None
    _annotation_obj: Optional[bpy.types.Object] = None
    _phase: str = "PICK_VERTEX"   # "PICK_VERTEX" | "PICK_FACE"
    _active_vertex_idx: int = -1
    _shape_cache: dict
    _region: Optional[bpy.types.Region] = None
    _rv3d: Optional[bpy.types.RegionView3D] = None

    # Hover-cycle state (active during PICK_FACE phase)
    _hover_candidates: list   # [(ifc_obj, hit_mesh, hit_mesh_mx, location, normal, face_index), ...]
    _hover_index: int         # which element candidate is currently highlighted
    _hover_last_px: tuple     # last cursor pixel position where candidates were computed
    _hover_highlighted_obj: Optional[bpy.types.Object]  # object currently selected for highlight

    # Snap-mode cycle state (FACE → EDGE → VERTEX, TAB)
    _snap_mode: str           # "FACE" | "EDGE" | "VERTEX"
    _draw_handler: object     # SpaceView3D draw handler handle

    _VERTEX_PICK_RADIUS_PX = 20
    _HOVER_THROTTLE_PX_SQ = 144  # 12 px — enough to feel responsive without per-pixel recompute
    _SNAP_MODES = ("FACE", "LAYER", "EDGE", "VERTEX")

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file loaded.")
            return False
        obj = context.active_object
        if not obj:
            cls.poll_message_set("No active object.")
            return False
        if context.mode != "OBJECT":
            cls.poll_message_set("Must be in Object Mode.")
            return False
        element = tool.Ifc.get_entity(obj)
        if not element or not element.is_a("IfcAnnotation"):
            cls.poll_message_set("Active object must be an IfcAnnotation.")
            return False
        ptype = ifcopenshell.util.element.get_predefined_type(element)
        if ptype not in ("DIMENSION", "RADIUS", "DIAMETER", "ANGLE", "PLAN_LEVEL", "SECTION_LEVEL"):
            cls.poll_message_set("Annotation must be a dimension type.")
            return False
        return True

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _invoke(self, context, event):
        obj = context.active_object
        self._annotation = tool.Ifc.get_entity(obj)
        self._annotation_obj = obj
        self._shape_cache = {}
        if self.anchor_index >= 0:
            self._phase = "PICK_FACE"
            self._active_vertex_idx = self.anchor_index
            from bonsai.bim.module.drawing.gizmos import set_active_anchor
            set_active_anchor(self.anchor_index, obj)
        else:
            self._phase = "PICK_VERTEX"
            self._active_vertex_idx = -1
        self._hover_candidates = []
        self._hover_index = 0
        self._hover_last_px = (-9999, -9999)
        self._hover_highlighted_obj = None
        self._snap_mode = "FACE"
        _snap_draw_data.clear()
        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            _draw_snap_indicator_global, (), "WINDOW", "POST_VIEW"
        )

        # When invoked from a panel, context.region_data is None.
        # Walk the screen areas to find the actual 3D viewport region.
        self._region, self._rv3d = None, None
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        self._region = region
                        break
                if area.spaces and area.spaces[0].type == "VIEW_3D":
                    self._rv3d = area.spaces[0].region_3d
                break

        self._set_status(context)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def _modal(self, context, event):
        # Undo while the modal is running can free the annotation object.
        try:
            _ = self._annotation_obj.name
        except ReferenceError:
            self._cleanup(context)
            return {"FINISHED"}

        if event.type == "ESC" or (event.type == "RIGHTMOUSE" and event.value == "PRESS"):
            self._clear_hover_highlight(context)
            context.workspace.status_text_set(None)
            _snap_draw_data.clear()
            if self._draw_handler:
                bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, "WINDOW")
                self._draw_handler = None
            from bonsai.bim.module.drawing.gizmos import set_active_anchor
            set_active_anchor(-1)
            obj = context.active_object
            if obj:
                obj.select_set(False)
                context.view_layer.objects.active = None
            return {"FINISHED"}

        # Hover — recompute candidates as cursor moves (PICK_FACE phase only)
        if event.type == "MOUSEMOVE" and self._phase == "PICK_FACE":
            self._handle_hover(context, event)
            return {"RUNNING_MODAL"}

        # Tab — cycle through candidates under cursor
        if event.type == "TAB" and event.value == "PRESS" and self._phase == "PICK_FACE":
            self._cycle_hover(context)
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            if self._phase == "PICK_VERTEX":
                self._handle_vertex_pick(context, event)
            else:
                wrote = self._handle_face_pick(context, event)
                if wrote:
                    # Finish here so this anchor write is its own undo step.
                    # The dimension stays selected so the user can click
                    # another dot immediately.
                    self._cleanup(context)
                    return {"FINISHED"}
            self._set_status(context)
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _cleanup(self, context):
        self._clear_hover_highlight(context)
        context.workspace.status_text_set(None)
        _snap_draw_data.clear()
        if self._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, "WINDOW")
            self._draw_handler = None
        from bonsai.bim.module.drawing.gizmos import set_active_anchor
        set_active_anchor(-1)
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
                break

    # ------------------------------------------------------------------
    # Status bar

    def _set_status(self, context):
        if self._phase == "PICK_VERTEX":
            context.workspace.status_text_set(
                "Click a dimension vertex  |  RMB / ESC: Finish"
            )
        else:
            # In PICK_FACE the hover handler writes a richer status; this is the
            # fallback shown when no candidates have been computed yet.
            context.workspace.status_text_set(
                f"Vertex {self._active_vertex_idx} — hover over element  |  "
                "TAB: cycle candidates  |  Click: anchor  |  ALT+Click: free point  |  RMB/ESC: Finish"
            )

    # ------------------------------------------------------------------
    # Phase 1: pick a vertex on the dimension curve

    def _handle_vertex_pick(self, context, event):
        from bpy_extras import view3d_utils

        region = self._region
        rv3d = self._rv3d
        if not region or not rv3d:
            return

        # event.mouse_region_x/y is relative to the event's region (e.g. N-panel),
        # not our stored 3D viewport region.  Use absolute coords minus region offset.
        coord = (event.mouse_x - region.x, event.mouse_y - region.y)
        obj = self._annotation_obj

        best_idx = None
        best_dist_sq = self._VERTEX_PICK_RADIUS_PX ** 2

        if obj.data and hasattr(obj.data, "splines"):
            for spline in obj.data.splines:
                for i, pt in enumerate(spline.points):
                    world_co = obj.matrix_world @ pt.co.xyz
                    screen_co = view3d_utils.location_3d_to_region_2d(region, rv3d, world_co)
                    if screen_co is None:
                        continue
                    dist_sq = (screen_co.x - coord[0]) ** 2 + (screen_co.y - coord[1]) ** 2
                    if dist_sq < best_dist_sq:
                        best_dist_sq = dist_sq
                        best_idx = i

        if best_idx is None:
            self.report({"WARNING"}, f"Click closer to a dimension vertex (within {self._VERTEX_PICK_RADIUS_PX}px)")
            return

        self._active_vertex_idx = best_idx
        self._phase = "PICK_FACE"
        from bonsai.bim.module.drawing.gizmos import set_active_anchor
        set_active_anchor(best_idx, obj)

    # ------------------------------------------------------------------
    # Phase 2: pick a face on an IFC element

    def _handle_face_pick(self, context, event):
        from mathutils import Vector

        region = self._region
        rv3d = self._rv3d
        if not region or not rv3d:
            return

        # ALT+click → free world-point anchor at any mesh surface.
        if event.alt:
            self._clear_hover_highlight(context)
            origin, direction = self._unproject_coord(
                (event.mouse_x - region.x, event.mouse_y - region.y)
            )
            best_dist = float("inf")
            alt_loc = None
            for obj in context.scene.objects:
                if obj.type != "MESH":
                    continue
                try:
                    mx_inv = obj.matrix_world.inverted()
                except Exception:
                    continue
                ok, loc_l, _, _ = obj.ray_cast(
                    mx_inv @ origin, (mx_inv.to_3x3() @ direction).normalized()
                )
                if ok:
                    loc_w = obj.matrix_world @ loc_l
                    d = (loc_w - origin).length
                    if d < best_dist:
                        best_dist = d
                        alt_loc = loc_w
            pt_m = list(alt_loc) if alt_loc else list(origin + direction * 5.0)
            import ifcopenshell.api.drawing as drawing_api
            anchor = drawing_api.make_world_anchor(pt_m)
            _do_write_anchor(self._annotation, self._annotation_obj, anchor, self._active_vertex_idx, self._shape_cache)
            self.report({"INFO"}, f"Vertex {self._active_vertex_idx} → free world point")
            return True

        # Normal click — use whichever candidate is currently highlighted.
        self._clear_hover_highlight(context)

        coord = (event.mouse_x - region.x, event.mouse_y - region.y)
        dx = coord[0] - self._hover_last_px[0]
        dy = coord[1] - self._hover_last_px[1]
        if dx * dx + dy * dy > self._HOVER_THROTTLE_PX_SQ or not self._hover_candidates:
            self._hover_candidates = self._compute_candidates(context, coord)
            self._hover_index = 0

        if not self._hover_candidates:
            self.report({"WARNING"}, "Nothing under cursor — click on a model element")
            return

        idx = min(self._hover_index, len(self._hover_candidates) - 1)
        hit_obj, hit_mesh, hit_mesh_mx, location, normal, face_index = self._hover_candidates[idx]

        element = tool.Ifc.get_entity(hit_obj)
        if not element:
            self.report({"WARNING"}, f"'{hit_obj.name}' is not an IFC element")
            return

        file = tool.Ifc.get()
        placement_override = {element.id(): np.array(hit_obj.matrix_world)}

        # Recompute snap geometry at the exact click position for accuracy.
        snap = self._compute_snap_geom(hit_obj, face_index, coord)
        snap_type = snap.get("type", "FACE")

        import ifcopenshell.api.drawing as drawing_api
        try:
            if snap_type == "LAYER" and snap.get("method") == "LAYER_BOUNDARY":
                anchor = drawing_api.build_anchor_from_layer_boundary(file, element, snap)
            elif snap_type == "VERTEX" and snap.get("profile_x_m") is not None:
                anchor = drawing_api.build_anchor_from_profile_vert(file, element, snap)
            elif snap_type == "EDGE" and snap.get("profile_x_m") is not None:
                anchor = drawing_api.build_anchor_from_profile_edge(file, element, snap)
            elif snap_type in ("VERTEX", "EDGE") and snap.get("snap_world") is not None:
                # Tessellation fallback — no IFC profile data available.
                # Use the snap position as a static WORLD anchor rather than a
                # FACE fingerprint, so the endpoint stays at the correct vertex/
                # edge position instead of drifting to the face centre.
                sw = snap["snap_world"]
                anchor = drawing_api.make_world_anchor([float(sw[0]), float(sw[1]), float(sw[2])])
            else:
                hit_m = (float(location.x), float(location.y), float(location.z))
                normal_m = (float(normal.x), float(normal.y), float(normal.z))
                anchor = drawing_api.build_anchor_from_hit(
                    file, element, hit_m, normal_m,
                    shape_cache=self._shape_cache,
                    placement_override=placement_override,
                )
        except Exception as exc:
            import traceback
            traceback.print_exc()
            self.report({"ERROR"}, f"build_anchor failed: {exc}")
            return

        _do_write_anchor(self._annotation, self._annotation_obj, anchor, self._active_vertex_idx, self._shape_cache)
        self.report(
            {"INFO"},
            f"Vertex {self._active_vertex_idx} → {element.is_a()}/{element.Name or element.GlobalId} [{anchor.get('type')}]",
        )
        return True

    # ------------------------------------------------------------------
    # Hover / cycle helpers

    def _unproject_coord(self, coord):
        """Return (origin, direction) world-space ray for a region pixel coord."""
        from mathutils import Vector

        rv3d = self._rv3d
        region = self._region
        persinv = rv3d.perspective_matrix.inverted()
        dx = (2.0 * coord[0] / region.width) - 1.0
        dy = (2.0 * coord[1] / region.height) - 1.0
        near_h = persinv @ Vector((dx, dy, -1.0, 1.0))
        far_h = persinv @ Vector((dx, dy, 1.0, 1.0))
        origin = near_h.xyz / near_h.w
        far_pt = far_h.xyz / far_h.w
        direction = (far_pt - origin).normalized()
        if not rv3d.is_perspective:
            origin = origin - direction * 1e4
        return origin, direction

    def _compute_candidates(self, context, coord):
        """Cast a ray from *coord* and return a ranked list of hit candidates.

        Each entry: (ifc_obj, hit_mesh, hit_mesh_mx, location, normal, face_index)
        Sorted closest-first for direct hits; by proximity distance for near-misses.
        """
        import math as _math
        from mathutils import Vector

        origin, direction = self._unproject_coord(coord)
        depsgraph = context.evaluated_depsgraph_get()

        # Scene-BVH pierce-through: O(log N) vs the previous O(N) per-object loop.
        # Each iteration steps past the last hit surface to reach the next object.
        direct: list = []
        ray_origin = Vector(origin)
        _EPS = 1e-4

        for _ in range(8):
            result, loc_w, nrm_w, fi, hit_obj_eval, hit_mx = context.scene.ray_cast(
                depsgraph, ray_origin, direction
            )
            if not result:
                break
            ray_origin = loc_w + direction * _EPS
            ifc_obj = getattr(hit_obj_eval, "original", hit_obj_eval)
            if ifc_obj == self._annotation_obj:
                continue
            if not ifc_obj.visible_get():
                continue
            if ifc_obj.type != "MESH":
                continue
            if not tool.Ifc.get_entity(ifc_obj):
                continue
            mx = ifc_obj.matrix_world
            fi = _prefer_perp_face_index(ifc_obj, loc_w, fi, world_matrix=mx)
            normal = (
                (mx.to_3x3() @ ifc_obj.data.polygons[fi].normal).normalized()
                if fi is not None
                else nrm_w.normalized()
            )
            dist = (loc_w - origin).length
            direct.append((dist, ifc_obj, ifc_obj, mx, loc_w, normal, fi))
        if direct:
            direct.sort(key=lambda c: c[0])
            return [(o, m, mmx, l, n, f) for _, o, m, mmx, l, n, f in direct]

        # Proximity fallback — collect ALL candidates within TOL, sorted by perp distance.
        TOL = 0.05

        def _perp(v):
            return v - v.dot(direction) * direction

        prox: list = []
        for ifc_obj in context.scene.objects:
            if ifc_obj == self._annotation_obj:
                continue
            if not ifc_obj.visible_get():
                continue
            if not tool.Ifc.get_entity(ifc_obj):
                continue
            if ifc_obj.type != "MESH":
                continue
            mx = ifc_obj.matrix_world
            try:
                mx_inv = mx.inverted()
            except Exception:
                continue
            bb_world = [mx @ Vector(c) for c in ifc_obj.bound_box]
            bb_proj = [_perp(v) for v in bb_world]
            op = _perp(origin)
            sx = max(min(v.x for v in bb_proj) - op.x, 0.0, op.x - max(v.x for v in bb_proj))
            sy = max(min(v.y for v in bb_proj) - op.y, 0.0, op.y - max(v.y for v in bb_proj))
            sz = max(min(v.z for v in bb_proj) - op.z, 0.0, op.z - max(v.z for v in bb_proj))
            perp_dist = _math.sqrt(sx * sx + sy * sy + sz * sz)
            if perp_dist > TOL:
                continue
            bb_ctr = sum((v for v in bb_world), Vector()) / 8
            t = (bb_ctr - origin).dot(direction)
            query_w = origin + t * direction
            try:
                found, loc_l, nrm_l, fi = ifc_obj.closest_point_on_mesh(mx_inv @ query_w, distance=100.0)
            except RuntimeError:
                continue
            if not found:
                continue
            loc_w = mx @ loc_l
            fi = _prefer_perp_face_index(ifc_obj, loc_w, fi, world_matrix=mx)
            normal = (mx.to_3x3() @ ifc_obj.data.polygons[fi].normal).normalized() if fi is not None else (mx.to_3x3() @ nrm_l).normalized()
            prox.append((perp_dist, ifc_obj, ifc_obj, mx, loc_w, normal, fi))

        prox.sort(key=lambda c: c[0])
        return [(o, m, mmx, l, n, f) for _, o, m, mmx, l, n, f in prox]

    def _handle_hover(self, context, event):
        """Recompute candidates when cursor moves; highlight the current one."""
        if not self._region:
            return
        coord = (event.mouse_x - self._region.x, event.mouse_y - self._region.y)
        dx = coord[0] - self._hover_last_px[0]
        dy = coord[1] - self._hover_last_px[1]
        if dx * dx + dy * dy < self._HOVER_THROTTLE_PX_SQ:
            return
        self._hover_last_px = coord
        self._hover_candidates = self._compute_candidates(context, coord)
        self._hover_index = 0
        self._apply_hover_highlight(context)

    def _cycle_hover(self, context):
        """Cycle snap mode (FACE → EDGE → VERTEX); advance element on wrap-around."""
        if not self._hover_candidates:
            return
        modes = self._SNAP_MODES
        cur = modes.index(self._snap_mode)
        nxt = (cur + 1) % len(modes)
        self._snap_mode = modes[nxt]
        if nxt == 0 and len(self._hover_candidates) > 1:
            self._hover_index = (self._hover_index + 1) % len(self._hover_candidates)
        self._apply_hover_highlight(context)

    def _apply_hover_highlight(self, context):
        """Select the current candidate object; compute snap geometry; update status."""
        if not self._hover_candidates:
            self._clear_hover_highlight(context)
            _snap_draw_data.clear()
            return

        ifc_obj, _, _, _, _, face_index = self._hover_candidates[self._hover_index]

        # Only update selection when the highlighted object changes.
        if ifc_obj != self._hover_highlighted_obj:
            if self._hover_highlighted_obj:
                try:
                    self._hover_highlighted_obj.select_set(False)
                except Exception:
                    pass
            self._hover_highlighted_obj = ifc_obj
            try:
                ifc_obj.select_set(True)
                context.view_layer.objects.active = ifc_obj
            except Exception:
                pass

        _snap_draw_data.clear()
        _snap_draw_data.update(self._compute_snap_geom(ifc_obj, face_index, self._hover_last_px))

        entity = tool.Ifc.get_entity(ifc_obj)
        label = (entity.Name or entity.GlobalId) if entity else ifc_obj.name
        n = len(self._hover_candidates)
        mode_label = self._snap_mode.capitalize()
        elem_hint = f" ({self._hover_index + 1}/{n})" if n > 1 else ""
        context.workspace.status_text_set(
            f"Dim vertex {self._active_vertex_idx} — {label}  [{mode_label}{elem_hint}]"
            "  |  TAB: cycle snap  |  Click: anchor  |  ALT+Click: free  |  RMB/ESC: Finish"
        )
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
                break

    def _clear_hover_highlight(self, context):
        """Deselect the highlighted object and restore the annotation as active."""
        if self._hover_highlighted_obj:
            try:
                self._hover_highlighted_obj.select_set(False)
            except Exception:
                pass
            self._hover_highlighted_obj = None
        try:
            self._annotation_obj.select_set(True)
            context.view_layer.objects.active = self._annotation_obj
        except Exception:
            pass

    def cancel(self, context):
        """Called when the operator is cancelled externally — clean up GPU handler."""
        _snap_draw_data.clear()
        if self._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, "WINDOW")
            self._draw_handler = None
        from bonsai.bim.module.drawing.gizmos import set_active_anchor
        set_active_anchor(-1)
        obj = context.active_object
        if obj:
            obj.select_set(False)
            context.view_layer.objects.active = None

    # ------------------------------------------------------------------
    # Snap geometry helpers

    def _compute_snap_geom(self, hit_obj, face_index, coord) -> dict:
        """Return snap draw-data dict for the current snap mode and hit face.

        When the hit element has an IfcExtrudedAreaSolid, VERTEX and EDGE snaps
        are resolved from the IFC profile geometry (stable across mesh reloads)
        rather than from Blender tessellation vertex indices.

        ``coord`` is a (x, y) tuple in region-local pixels.  Returns an empty
        dict when the face index is invalid or the region is unavailable.
        """
        from bpy_extras.view3d_utils import location_3d_to_region_2d

        region = self._region
        rv3d = self._rv3d
        if not region or not rv3d or face_index is None:
            return {}
        try:
            face = hit_obj.data.polygons[face_index]
        except (IndexError, AttributeError):
            return {}

        mx = hit_obj.matrix_world
        face_verts_world = [tuple(mx @ hit_obj.data.vertices[vi].co) for vi in face.vertices]

        if self._snap_mode == "FACE":
            return {"type": "FACE", "face_verts": face_verts_world}

        # Try profile-based snap candidates first (IFC-native, index-stable).
        if self._snap_mode in ("VERTEX", "EDGE"):
            element = tool.Ifc.get_entity(hit_obj)
            if element:
                import ifcopenshell.api.drawing as drawing_api
                placement_override = {element.id(): np.array(mx)}
                candidates = drawing_api.get_profile_snap_candidates(
                    tool.Ifc.get(), element, placement_override=placement_override
                )
                want_type = self._snap_mode
                best_cand = None
                best_d2 = float("inf")
                for cand in candidates:
                    if cand["type"] != want_type:
                        continue
                    sp = location_3d_to_region_2d(region, rv3d, cand["snap_world"])
                    if sp is None:
                        continue
                    dx, dy = sp.x - coord[0], sp.y - coord[1]
                    d2 = dx * dx + dy * dy
                    if d2 < best_d2:
                        best_d2, best_cand = d2, cand
                if best_cand is not None:
                    return best_cand

            # Fallback: Blender tessellation snap for elements without an
            # IfcExtrudedAreaSolid profile.  Returns snap_world for the visual
            # indicator; no pt_idx so the click handler creates a face anchor.
            screen_pts = [location_3d_to_region_2d(region, rv3d, wv) for wv in face_verts_world]
            n = len(face_verts_world)

            if self._snap_mode == "VERTEX":
                best_i, best_d2 = 0, float("inf")
                for i, sp in enumerate(screen_pts):
                    if sp is not None:
                        dx, dy = sp.x - coord[0], sp.y - coord[1]
                        d2 = dx * dx + dy * dy
                        if d2 < best_d2:
                            best_d2, best_i = d2, i
                return {"type": "VERTEX", "snap_world": face_verts_world[best_i]}

            if self._snap_mode == "EDGE":
                best_e, best_d2 = 0, float("inf")
                for i in range(n):
                    j = (i + 1) % n
                    sp0, sp1 = screen_pts[i], screen_pts[j]
                    if sp0 is not None and sp1 is not None:
                        mid_x = (sp0.x + sp1.x) * 0.5
                        mid_y = (sp0.y + sp1.y) * 0.5
                        dx, dy = mid_x - coord[0], mid_y - coord[1]
                        d2 = dx * dx + dy * dy
                        if d2 < best_d2:
                            best_d2, best_e = d2, i
                i0, i1 = best_e, (best_e + 1) % n
                v0_w, v1_w = face_verts_world[i0], face_verts_world[i1]
                mid_w = ((v0_w[0] + v1_w[0]) * 0.5, (v0_w[1] + v1_w[1]) * 0.5, (v0_w[2] + v1_w[2]) * 0.5)
                return {"type": "EDGE", "v0": v0_w, "v1": v1_w, "snap_world": mid_w}

        if self._snap_mode == "LAYER":
            element = tool.Ifc.get_entity(hit_obj)
            if element:
                import ifcopenshell.api.drawing as drawing_api
                placement_override = {element.id(): np.array(mx)}
                candidates = drawing_api.get_layer_snap_candidates(
                    tool.Ifc.get(), element, placement_override=placement_override
                )
                best_cand = None
                best_d2 = float("inf")
                for cand in candidates:
                    sp = location_3d_to_region_2d(region, rv3d, cand["snap_world"])
                    if sp is None:
                        continue
                    dx, dy = sp.x - coord[0], sp.y - coord[1]
                    d2 = dx * dx + dy * dy
                    if d2 < best_d2:
                        best_d2, best_cand = d2, cand
                if best_cand is not None:
                    result = dict(best_cand)
                    result["type"] = "LAYER"
                    result["method"] = "LAYER_BOUNDARY"
                    return result
            return {"type": "FACE", "face_verts": face_verts_world}

        return {}


def _do_write_anchor(annotation, annotation_obj, new_anchor: dict, vertex_index: int, shape_cache=None) -> None:
    """Write one anchor into the BBIM_Dimension pset and regenerate the curve."""
    file = tool.Ifc.get()

    pset_data = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")

    if pset_data and pset_data.get("Anchors"):
        try:
            anchors: list = json.loads(pset_data["Anchors"])
        except Exception:
            anchors = []
    else:
        anchors = _anchors_from_spline(annotation_obj, file)

    while len(anchors) <= vertex_index:
        idx = len(anchors)
        if annotation_obj and annotation_obj.data and hasattr(annotation_obj.data, "splines") and annotation_obj.data.splines:
            pts = annotation_obj.data.splines[0].points
            if idx < len(pts):
                co = annotation_obj.matrix_world @ pts[idx].co.xyz
                import ifcopenshell.api.drawing as drawing_api
                anchors.append(drawing_api.make_world_anchor([float(co.x), float(co.y), float(co.z)]))
                continue
        import ifcopenshell.api.drawing as drawing_api
        anchors.append(drawing_api.make_world_anchor([0.0, 0.0, 0.0]))

    anchors[vertex_index] = new_anchor
    anchors_json = json.dumps(anchors)

    if pset_data:
        pset_entity = file.by_id(pset_data["id"])
        ifcopenshell.api.run("pset.edit_pset", file, pset=pset_entity, properties={"Anchors": anchors_json})
    else:
        ifcopenshell.api.run("pset.add_pset", file, product=annotation, name="BBIM_Dimension")
        pset_data = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
        pset_entity = file.by_id(pset_data["id"])
        ifcopenshell.api.run("pset.edit_pset", file, pset=pset_entity, properties={"Anchors": anchors_json})

    from bonsai.bim.module.drawing import handler as _drawing_handler
    _drawing_handler.invalidate_dim_index()

    placement_override: dict = {}
    for a in anchors:
        guid = a.get("guid")
        if not guid:
            continue
        try:
            elem = file.by_guid(guid)
            elem_obj = tool.Ifc.get_object(elem)
            if elem_obj:
                placement_override[elem.id()] = np.array(elem_obj.matrix_world)
        except Exception:
            pass

    import ifcopenshell.api.drawing as drawing_api
    resolved_pts = drawing_api.regenerate_dimension(
        file,
        annotation,
        shape_cache=shape_cache,
        placement_override=placement_override,
    )
    if resolved_pts:
        _update_blender_curve(annotation, resolved_pts)



class RegenerateDimensions(bpy.types.Operator, tool.Ifc.Operator):
    """Regenerate all parametric dimension annotations in the project.

    For every IfcAnnotation that has a BBIM_Dimension pset, resolve all
    anchor references from live element geometry and update the annotation's
    curve vertices and linked IfcMetric values.
    """

    bl_idname = "bim.regenerate_dimensions"
    bl_label = "Regenerate Dimensions"
    bl_description = (
        "Recompute all parametric dimension annotations from current element geometry.\n"
        "Updates curve vertex positions and IfcMetric segment values."
    )
    bl_options = {"REGISTER", "UNDO"}

    active_only: bpy.props.BoolProperty(
        name="Active Only",
        description="Only regenerate the currently selected dimension annotation",
        default=False,
    )

    if TYPE_CHECKING:
        active_only: bool

    @classmethod
    def poll(cls, context):
        return bool(tool.Ifc.get())

    def _execute(self, context):
        import ifcopenshell.api.drawing as drawing_api
        import ifcopenshell.geom

        file = tool.Ifc.get()

        geom_settings = ifcopenshell.geom.settings()
        geom_settings.set("APPLY_DEFAULT_MATERIALS", False)
        shape_cache: dict = {}

        if self.active_only:
            obj = context.active_object
            if not obj:
                self.report({"WARNING"}, "No active object.")
                return
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcAnnotation"):
                self.report({"WARNING"}, "Active object is not an IfcAnnotation.")
                return
            candidates = [element]
        else:
            candidates = [
                a for a in file.by_type("IfcAnnotation")
                if ifcopenshell.util.element.get_pset(a, "BBIM_Dimension")
            ]

        from bonsai.bim.module.drawing.handler import _sync_dimension_anchors_to_curve

        updated = 0
        for annotation in candidates:
            pset = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
            if not pset:
                continue

            # Sync anchor count to curve vertex count in case the user added or
            # removed vertices in Edit Mode since the last regeneration.
            ann_obj = tool.Ifc.get_object(annotation)
            if ann_obj and ann_obj.type == "CURVE":
                _sync_dimension_anchors_to_curve(file, annotation, ann_obj)

            # Build a placement override from each referenced element's current
            # Blender matrix_world.  Bonsai only syncs ObjectPlacement to the IFC
            # file when the user explicitly clicks "Edit Object Placement" — so the
            # IFC entity may be stale after a viewport G-move.  Using matrix_world
            # ensures we always see the current element position.
            placement_override: dict[int, "np.ndarray"] = {}
            try:
                anchors_raw = json.loads(pset.get("Anchors") or "[]")
                for anchor in anchors_raw:
                    guid = anchor.get("guid")
                    if not guid:
                        continue
                    try:
                        elem = file.by_guid(guid)
                        elem_id = elem.id()
                        if elem_id in placement_override:
                            continue
                        elem_obj = tool.Ifc.get_object(elem)
                        if elem_obj:
                            placement_override[elem_id] = np.array(elem_obj.matrix_world)
                    except Exception:
                        pass
            except Exception:
                pass

            resolved_pts = drawing_api.regenerate_dimension(
                file, annotation,
                settings=geom_settings,
                shape_cache=shape_cache,
                placement_override=placement_override,
            )
            if not resolved_pts:
                continue

            _update_blender_curve(annotation, resolved_pts)
            updated += 1

        self.report({"INFO"}, f"Regenerated {updated} parametric dimension(s).")


# ---------------------------------------------------------------------------
# Helpers for dimension operators
# ---------------------------------------------------------------------------


def _anchors_from_spline(obj: bpy.types.Object, file: ifcopenshell.file) -> list:
    """Build a list of WORLD anchors from the current spline points of obj.

    Coordinates are stored in metres (Blender world space), which matches the
    output of ifcopenshell.geom.create_shape regardless of IFC project unit.
    """
    import ifcopenshell.api.drawing as drawing_api

    anchors = []
    if not obj or not obj.data or not hasattr(obj.data, "splines") or not obj.data.splines:
        return anchors

    for pt in obj.data.splines[0].points:
        world_co = obj.matrix_world @ pt.co.xyz
        # Store in metres (Blender world space)
        pt_m = [float(world_co.x), float(world_co.y), float(world_co.z)]
        anchors.append(drawing_api.make_world_anchor(pt_m))

    return anchors


def _update_blender_curve(
    annotation: ifcopenshell.entity_instance,
    resolved_pts_m: list,
) -> None:
    """Update a Blender curve object's spline points AND the backing IFC IfcPolyline.

    :param resolved_pts_m: Points in metres (Blender world space).

    Both the Blender curve data and the IFC representation are updated so that
    entering Edit Mode (which reloads geometry from IFC via import_representation_items)
    does not reset the curve back to pre-regeneration positions.
    """
    obj = tool.Ifc.get_object(annotation)
    if not obj or not obj.data or not hasattr(obj.data, "splines"):
        return

    curve_data: bpy.types.Curve = obj.data
    inv_world = obj.matrix_world.inverted()
    n = len(resolved_pts_m)

    if not curve_data.splines:
        spline = curve_data.splines.new("POLY")
        spline.points.add(n - 1)
    else:
        spline = curve_data.splines[0]
        if len(spline.points) != n:
            curve_data.splines.remove(spline)
            spline = curve_data.splines.new("POLY")
            spline.points.add(n - 1)

    is_2d = _annotation_is_2d(annotation)
    for i, pt_m in enumerate(resolved_pts_m):
        blender_world = Vector((float(pt_m[0]), float(pt_m[1]), float(pt_m[2])))
        local_pt = inv_world @ blender_world
        # For 2D (plan-view) annotations, project onto the annotation plane by
        # zeroing local Z — matching the Annotator.add_line_to_annotation pattern.
        if is_2d:
            spline.points[i].co = (local_pt.x, local_pt.y, 0.0, 1.0)
        else:
            spline.points[i].co = (*local_pt, 1.0)

    # Also update the IFC IfcPolyline so Edit Mode reloads reflect the new positions.
    try:
        _update_ifc_polyline(tool.Ifc.get(), annotation, obj, resolved_pts_m)
    except Exception as e:
        pass


def _annotation_is_2d(annotation: ifcopenshell.entity_instance) -> bool:
    """Return True if the annotation's representation uses 2D coordinates (plan view)."""
    if not getattr(annotation, "Representation", None):
        return False
    for rep in annotation.Representation.Representations:
        curve = _find_curve_item(rep)
        if curve is None:
            continue
        if curve.is_a("IfcIndexedPolyCurve"):
            return curve.Points.is_a("IfcCartesianPointList2D")
        if curve.is_a("IfcPolyline") and curve.Points:
            return len(curve.Points[0].Coordinates) == 2
    return False


def _update_ifc_polyline(
    file: ifcopenshell.file,
    annotation: ifcopenshell.entity_instance,
    obj: bpy.types.Object,
    resolved_pts_m: list,
) -> None:
    """Update the curve coordinates in the annotation's IFC representation.

    Converts world-space metres points → annotation-local IFC project units and
    writes them into the existing IfcIndexedPolyCurve or IfcPolyline entities.
    Handles both 2D (IfcCartesianPointList2D) and 3D representations.
    """
    if not resolved_pts_m or not getattr(annotation, "Representation", None):
        return

    import ifcopenshell.util.unit as ifc_unit

    unit_scale = ifc_unit.calculate_unit_scale(file)
    inv_world = obj.matrix_world.inverted()

    def _to_ifc_local(pt_m: tuple) -> tuple:
        blender_local = inv_world @ Vector((float(pt_m[0]), float(pt_m[1]), float(pt_m[2])))
        return (
            float(blender_local.x) / unit_scale,
            float(blender_local.y) / unit_scale,
            float(blender_local.z) / unit_scale,
        )

    new_coords = [_to_ifc_local(pt) for pt in resolved_pts_m]

    for rep in annotation.Representation.Representations:
        curve = _find_curve_item(rep)
        if curve is None:
            continue

        if curve.is_a("IfcIndexedPolyCurve"):
            pts_list = curve.Points  # IfcCartesianPointList2D or 3D
            n_dims = 2 if pts_list.is_a("IfcCartesianPointList2D") else 3
            pts_list.CoordList = tuple(coords[:n_dims] for coords in new_coords)
            # Rebuild Segments to cover all consecutive pairs.  Bonsai creates
            # explicit IfcLineIndex entries per segment; leaving a stale Segments
            # list (e.g. [IfcLineIndex([1,2])]) after adding a 3rd point means
            # the extra point is silently ignored on geometry reload.
            n_pts = len(new_coords)
            if n_pts >= 2:
                curve.Segments = [file.createIfcLineIndex([i + 1, i + 2]) for i in range(n_pts - 1)]
            else:
                curve.Segments = None
            return

        if curve.is_a("IfcPolyline"):
            existing = list(curve.Points)
            if len(existing) == len(new_coords):
                for ifc_pt, coords in zip(existing, new_coords):
                    n_dims = len(ifc_pt.Coordinates)
                    ifc_pt.Coordinates = coords[:n_dims]
            else:
                dim = len(existing[0].Coordinates) if existing else 3
                curve.Points = [
                    file.create_entity("IfcCartesianPoint", Coordinates=coords[:dim])
                    for coords in new_coords
                ]
            return


def _find_curve_item(rep: ifcopenshell.entity_instance) -> Optional[ifcopenshell.entity_instance]:
    """Return the first IfcPolyline or IfcIndexedPolyCurve in a shape representation."""
    for item in rep.Items:
        result = _find_curve_in_item(item)
        if result is not None:
            return result
    return None


def _find_curve_in_item(item: ifcopenshell.entity_instance) -> Optional[ifcopenshell.entity_instance]:
    if item.is_a("IfcPolyline") or item.is_a("IfcIndexedPolyCurve"):
        return item
    if item.is_a("IfcGeometricCurveSet"):
        for element in item.Elements:
            result = _find_curve_in_item(element)
            if result is not None:
                return result
    return None




class ClickNearestDimensionAnchor(bpy.types.Operator):
    """LMB fallback: fire SetDimensionAnchor when cursor is within RADIUS pixels of an anchor dot.

    The gizmo handles exact hits; this catches near-misses where the cursor
    is close to a dot but didn't land inside the gizmo hit shape.
    """

    bl_idname = "bim.click_nearest_dimension_anchor"
    bl_label = "Click Nearest Dimension Anchor"

    RADIUS_PX = 60

    def invoke(self, context, event):
        from bpy_extras.view3d_utils import location_3d_to_region_2d

        if not tool.Ifc.get():
            return {"PASS_THROUGH"}

        # Always use the 3D viewport WINDOW region — context.region may be a header,
        # sidebar, or toolbar depending on where the click landed in the area.
        region = None
        rv3d = None
        for area in context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for r in area.regions:
                if r.type == "WINDOW":
                    region = r
                    break
            if region:
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        rv3d = space.region_3d
                        break
                break

        if not region or not rv3d:
            return {"PASS_THROUGH"}

        # Convert absolute mouse position to WINDOW region-local coordinates.
        cx = event.mouse_x - region.x
        cy = event.mouse_y - region.y

        import ifcopenshell.util.element as _ue

        r2 = self.RADIUS_PX ** 2
        best_obj = None
        best_idx = -1
        best_dist_sq = float("inf")

        # Scan all visible dimension annotations — not just selected ones.
        # view3d.select may deselect the annotation before this operator runs.
        for obj in context.scene.objects:
            if obj.type != "CURVE":
                continue
            if not obj.visible_get():
                continue
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcAnnotation"):
                continue
            pset = _ue.get_pset(element, "BBIM_Dimension")
            if not pset or not pset.get("Anchors"):
                continue
            if not obj.data.splines:
                continue

            for i, pt in enumerate(obj.data.splines[0].points):
                world_pos = obj.matrix_world @ pt.co.to_3d()
                sp = location_3d_to_region_2d(region, rv3d, world_pos)
                if not sp:
                    continue
                dx, dy = cx - sp.x, cy - sp.y
                d2 = dx * dx + dy * dy
                if d2 < r2 and d2 < best_dist_sq:
                    best_dist_sq = d2
                    best_idx = i
                    best_obj = obj

        if best_obj is None:
            return {"PASS_THROUGH"}

        for o in list(context.selected_objects):
            o.select_set(False)
        best_obj.select_set(True)
        context.view_layer.objects.active = best_obj
        from bonsai.bim.module.drawing.gizmos import set_active_anchor
        set_active_anchor(best_idx, best_obj)
        # Force viewport redraw so gizmo colors update before the modal starts.
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
                break
        bpy.ops.bim.set_dimension_anchor("INVOKE_DEFAULT", anchor_index=best_idx)
        return {"FINISHED"}


class DebugDimensionClicks(bpy.types.Operator):
    """Debug modal: logs every LMB click in the 3D viewport vs anchor gizmo positions.

    Run from the Python console:
        bpy.ops.bim.debug_dimension_clicks('INVOKE_DEFAULT')
    Press ESC or RMB to stop.
    """

    bl_idname = "bim.debug_dimension_clicks"
    bl_label = "Debug Dimension Clicks"

    def modal(self, context, event):
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            # Use absolute window coords — mouse_region_x/y is relative to whichever
            # region caught the event, which may differ from the 3D viewport region.
            click_x = event.mouse_x
            click_y = event.mouse_y

            # Find the 3D viewport region — context.region_data is None in modal.
            region = None
            rv3d = None
            for area in context.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                for r in area.regions:
                    if r.type == "WINDOW":
                        region = r
                        break
                if region:
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            rv3d = space.region_3d
                            break
                    break

            obj = context.active_object
            if obj and obj.type == "CURVE" and obj.data and obj.data.splines and region and rv3d:
                from bpy_extras.view3d_utils import location_3d_to_region_2d

                print(f"[ClickDebug] LMB at abs ({click_x}, {click_y})  region_offset=({region.x},{region.y})")
                for i, pt in enumerate(obj.data.splines[0].points):
                    world_pos = obj.matrix_world @ pt.co.to_3d()
                    screen_pos = location_3d_to_region_2d(region, rv3d, world_pos)
                    if screen_pos:
                        # Convert region-local pos to absolute window coords for comparison.
                        abs_x = screen_pos.x + region.x
                        abs_y = screen_pos.y + region.y
                        dist = ((click_x - abs_x) ** 2 + (click_y - abs_y) ** 2) ** 0.5
                        print(f"  anchor[{i}]  abs={abs_x:.0f},{abs_y:.0f}  dist={dist:.1f}px")
                    else:
                        print(f"  anchor[{i}]  (off screen)")
            else:
                print(f"[ClickDebug] LMB at abs ({click_x}, {click_y}) — no active curve or no 3D region")
            return {"PASS_THROUGH"}

        if event.type in {"ESC", "RIGHTMOUSE"}:
            print("[ClickDebug] Stopped.")
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        print("[ClickDebug] Dimension click logger started. Click near anchor dots; press ESC to stop.")
        return {"RUNNING_MODAL"}
