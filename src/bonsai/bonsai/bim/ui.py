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
#
# This file was modified with the assistance of an AI coding tool.

import os
import platform
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

import bpy
import platformdirs
from bpy.props import BoolProperty, StringProperty
from bpy.types import Panel
from ifcopenshell.util.doc import (
    get_entity_doc,
    get_property_set_doc,
    get_type_doc,
)
from ifcopenshell.util.file import IfcHeaderExtractor
from natsort import natsorted

import bonsai.bim
import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.ifc import is_cache_locked_by_other_process
from bonsai.bim.module.bsdd.prop import BIMBSDDProperties, BSDDProperty
from bonsai.bim.module.model import prop as _model_prop
from bonsai.bim.module.model import ui as _model_ui
from bonsai.bim.module.pset.prop import IfcProperty
from bonsai.bim.prop import Attribute

if TYPE_CHECKING:
    from bonsai.bim.module.project.prop import BIMProjectProperties
    from bonsai.bim.prop import ObjProperty


class IFCFileSelector:
    layout: bpy.types.UILayout

    # Avoid overriding blender prop annotations at runtime.
    if TYPE_CHECKING:
        filepath: str
        use_relative_path: bool

    def is_existing_ifc_file(self, filepath: Optional[str] = None) -> bool:
        """Check if file path exists and if it's an IFC file.

        If `filepath` is not provided, will use filepath property from the current operator.
        """
        if filepath is None:
            path = self.get_filepath_abs()
        else:
            path = Path(filepath)
        return path.exists() and path.is_file() and "ifc" in path.suffix.lower()

    def get_filepath_abs(self) -> Path:
        # self.filepath filled by fileselect_add is absolute
        # but we support relative paths provided by custom scripts.
        filepath = Path(self.filepath)
        if not filepath.is_absolute():
            filepath = Path(bpy.path.abspath("//")) / filepath
        return filepath

    def get_filepath(self) -> str:
        """get filepath taking into account relative paths"""
        filepath = self.get_filepath_abs()

        if self.use_relative_path:
            filepath = filepath.relative_to(bpy.path.abspath("//"))
        return filepath.as_posix().replace("\\", "/")

    def draw(self, context: bpy.types.Context) -> None:
        assert isinstance(context.space_data, bpy.types.SpaceFileBrowser)
        # Access filepath & Directory https://blender.stackexchange.com/a/207665
        params = context.space_data.params
        assert params
        # Decode byte string https://stackoverflow.com/a/47737082/
        directory = Path(params.directory.decode("utf-8"))
        filepath = os.path.join(directory, params.filename)
        layout = self.layout
        if self.is_existing_ifc_file(filepath):
            box = layout.box()
            box.label(text="IFC Header Specifications", icon="INFO")
            header_data = IfcHeaderExtractor(filepath).extract()
            for key, value in header_data.items():
                if value != "":
                    split = box.split()
                    split.label(text=key.title().replace("_", " "))
                    split.label(text=str(value))
                    if key.lower() == "schema_name" and filepath[-4:].lower() == ".ifc":
                        schema_lower = str(value).lower()
                        if schema_lower == "ifc2x3":
                            row = box.row()
                            op = row.operator("bim.run_migrate_patch", text="Upgrade to IFC4")
                            op.infile = filepath
                            op.outfile = filepath[0:-4] + "-IFC4.ifc"
                            op.schema = "IFC4"
                        elif schema_lower == "ifc4":
                            row = box.row()
                            op = row.operator("bim.run_migrate_patch", text="Upgrade to IFC4X3")
                            op.infile = filepath
                            op.outfile = filepath[0:-4] + "-IFC4X3.ifc"
                            op.schema = "IFC4X3"

        if bpy.data.is_saved:
            layout.prop(self, "use_relative_path")
        else:
            self.use_relative_path = False
            layout.label(text="Save the .blend file first ")
            layout.label(text="to use relative paths for .ifc.")


class BIM_PT_section_plane(Panel):
    bl_idname = "BIM_PT_section_plane"
    bl_label = "Temporary Section Cutaways"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        assert self.layout
        layout = self.layout
        layout.use_property_split = True
        props = tool.Blender.get_bim_props()

        layout.prop(props, "should_section_selected_objects")
        layout.prop(props, "section_plane_colour")
        layout.prop(props, "section_line_decorator_width")

        row = layout.row(align=True)
        row.operator("bim.add_section_plane")
        row.operator("bim.remove_section_plane")


class BIM_PT_section_with_cappings(Panel):
    bl_idname = "BIM_PT_section_with_cappings"
    bl_label = "Section Cutaways With Cappings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        assert self.layout
        layout = self.layout
        wm = context.window_manager
        row = layout.row(align=True)
        row.operator("bim.clipping_plane_cut_with_cappings", icon="XRAY", text="Cut")
        row.operator("bim.revert_clipping_plane_cut", icon="FILE_REFRESH", text="Revert Cut")

        props = tool.Project.get_project_props()
        box = layout.box()
        header = box.row(align=True)
        header.label(text="Clipping Planes")
        header.operator("bim.save_clipping_planes", text="", icon="EXPORT")
        header.operator("bim.load_clipping_planes", text="", icon="IMPORT")
        header.operator("bim.create_clipping_plane", text="", icon="ADD")

        box.template_list(
            "BIM_UL_clipping_plane",
            "",
            props,
            "clipping_planes",
            props,
            "clipping_planes_active_index",
        )

        if active_clipping_plane := props.active_clipping_plane:
            active_clipping_plane_obj = active_clipping_plane.obj
            box.prop(active_clipping_plane_obj, "location")
            box.prop(active_clipping_plane_obj, "rotation_euler")


class BIM_UL_clipping_plane(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: "BIMProjectProperties",
        item: "ObjProperty",
        icon,
        active_data,
        active_propname,
    ) -> None:
        if item and item.obj:
            obj = item.obj
            row = layout.row(align=True)
            row.prop(obj, "name", text="", emboss=False)
            row.operator("bim.select_object", text="", icon="RESTRICT_SELECT_OFF").obj_name = obj.name
            row.context_pointer_set("active_object", obj)
            row.operator("bim.flip_clipping_plane", text="", icon="PASTEFLIPDOWN")
            row.operator("bim.delete_object", text="", icon="TRASH").obj_name = obj.name
        else:
            layout.label(text="", translate=False)


class BIM_UL_generic(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: bpy.types.PropertyGroup,
        item: bpy.types.PropertyGroup,
        icon,
        active_data,
        active_propname,
    ) -> None:
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_tab_visibilities(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: bpy.types.PropertyGroup,
        item: bpy.types.PropertyGroup,
        icon,
        active_data,
        active_propname,
    ) -> None:
        row = layout.row()
        row.prop(item, "name", text="", emboss=False)
        row.prop(item, "is_visible", text="", icon="HIDE_OFF" if item.is_visible else "HIDE_ON", emboss=False)


class BIM_UL_panel_visibilities(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: bpy.types.PropertyGroup,
        item: bpy.types.PropertyGroup,
        icon,
        active_data,
        active_propname,
    ) -> None:
        row = layout.row()
        row.prop(item, "label", text="", emboss=False)
        row.prop(item, "is_visible", text="", icon="HIDE_OFF" if item.is_visible else "HIDE_ON", emboss=False)
        row.prop(item, "is_bookmarked", text="", icon="SOLO_ON" if item.is_bookmarked else "SOLO_OFF", emboss=False)


class GizmoPreferences(bpy.types.PropertyGroup):
    """Aggregator for parametric gizmo visibility settings. One flat bool per
    parametric feature; controls whether that feature's gizmo group polls
    visible in the viewport.

    The per-feature ``<name>: BoolProperty`` fields are derived from
    ``tool.Parametric.EDIT_TYPES`` at module load — adding a new parametric
    type to the registry automatically surfaces its toggle here, with no
    parallel hand-maintained list to keep in sync."""

    draw_gizmos_in_3d_viewport: BoolProperty(
        name="Draw Gizmos In 3D Viewport",
        default=True,
        description="Show interactive gizmos in the 3D viewport for parametric elements",
    )

    if TYPE_CHECKING:
        draw_gizmos_in_3d_viewport: bool


for _gizmo_pref_entry in tool.Parametric.EDIT_TYPES:
    GizmoPreferences.__annotations__[_gizmo_pref_entry.name] = BoolProperty(
        name=_gizmo_pref_entry.name.replace("_", " ").title(),
        default=True,
    )
del _gizmo_pref_entry


class DocPreferences(bpy.types.PropertyGroup):
    sheets_dir: StringProperty(
        default=os.path.join("sheets") + os.path.sep,
        name="Default Sheets Directory",
    )
    layouts_dir: StringProperty(
        default=os.path.join("layouts") + os.path.sep,
        name="Default Layouts Directory",
    )
    titleblocks_dir: StringProperty(
        default=os.path.join("layouts", "titleblocks") + os.path.sep,
        name="Default Titleblocks Directory",
    )
    drawings_dir: StringProperty(
        default=os.path.join("drawings") + os.path.sep,
        name="Default Drawings Directory",
    )
    stylesheet_path: StringProperty(
        default=os.path.join("drawings", "assets", "default.css"),
        name="Default Stylesheet",
    )
    schedules_stylesheet_path: StringProperty(
        default=os.path.join("drawings", "assets", "schedule.css"),
        name="Default Stylesheet for Schedules",
    )
    markers_path: StringProperty(
        default=os.path.join("drawings", "assets", "markers.svg"),
        name="Default Markers",
    )
    symbols_path: StringProperty(
        default=os.path.join("drawings", "assets", "symbols.svg"),
        name="Default Symbols",
    )
    patterns_path: StringProperty(
        default=os.path.join("drawings", "assets", "patterns.svg"),
        name="Default Patterns",
    )
    shadingstyles_path: StringProperty(
        default=os.path.join("drawings", "assets", "shading_styles.json"),
        name="Default Shading Styles",
    )
    shadingstyle_default: StringProperty(
        default="Blender Default",
        name="Default Shading Style",
    )
    drawing_font: StringProperty(
        default="OpenGost Type B TT.ttf",
        name="Drawing Font",
    )
    magic_font_scale: bpy.props.FloatProperty(
        default=0.004118616,
        name="Font Scale Factor",
    )
    imperial_precision: StringProperty(
        default="1/32",
        name="Imperial Precision",
    )
    tolerance: bpy.props.FloatProperty(
        default=0.00001,
        name="A tolerance used when selecting objects",
    )
    classes_to_wireframe: StringProperty(
        default="IfcVirtualElement",
        name="Classes to Wireframe",
        description="Upon import, these classes will display as wireframe.\nEx: IfcVirtualElement, IfcSpace",
    )
    classes_no_cut: StringProperty(
        default="IfcVirtualElement, IfcSpace",
        name="Classes that are not cut",
        description="The cut decorator will be turned off for these classes\nEx: IfcVirtualElement, IfcSpace",
    )

    if TYPE_CHECKING:
        sheets_dir: str
        layouts_dir: str
        titleblocks_dir: str
        drawings_dir: str
        stylesheet_path: str
        schedules_stylesheet_path: str
        markers_path: str
        symbols_path: str
        patterns_path: str
        shadingstyles_path: str
        shadingstyle_default: str
        drawing_font: str
        magic_font_scale: float
        imperial_precision: str
        tolerance: float
        classes_to_wireframe: str
        classes_no_cut: str


class DefaultParameters(bpy.types.PropertyGroup):
    """Per-type preset values used to seed new parametric instances.

    The ``<name>: PointerProperty`` fields are derived from the subset of
    ``tool.Parametric.EDIT_TYPES`` flagged ``has_default_parameters=True``,
    each pointing at the matching ``BIM<Name>Properties`` class. Adding a
    new entry with that flag automatically surfaces a preferences section
    and gives the create operator a preset to copy from."""


for _default_params_entry in tool.Parametric.EDIT_TYPES:
    if not _default_params_entry.has_default_parameters:
        continue
    DefaultParameters.__annotations__[_default_params_entry.name] = bpy.props.PointerProperty(
        type=getattr(_model_prop, _default_params_entry.props_attr),
    )
del _default_params_entry


class BIM_ADDON_preferences(bpy.types.AddonPreferences):
    bl_idname = tool.Blender.get_blender_addon_package_name()
    svg2pdf_command: StringProperty(
        name="SVG to PDF Command",
        description=(
            "print sheet to pdf together with svg. Leave blank svg is just created, "
            'E.g. [["path to application eg. /Applications/Inkscape.app/Contents/MacOS/inkscape", "svg", "-o", "pdf"]]'
            '\n `"svg"`, `"pdf"` will be replaced automatically.'
        ),
    )
    svg2dxf_command: StringProperty(
        name="SVG to DXF Command",
        description=(
            'E.g. `[["inkscape", "svg", "-o", "eps"], '
            '["pstoedit", "-dt", "-f", "dxf:-polyaslines -mm", "eps", "dxf", "-psarg", "-dNOSAFER"]]`'
            '\n `"svg"`, `"eps"`, `"dxf"` will be replaced automatically.'
        ),
    )
    svg_command: StringProperty(
        name="SVG Command",
        description=(
            "Software to open generated drawing and sheets. Leave blank system default for .svg is used "
            'E.g. [["path to application eg. /Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "path"]]'
            '\n `"path"` will be replaced with the path to the generated .svg file.'
        ),
    )
    layout_svg_command: StringProperty(
        name="Layout SVG Command",
        description=(
            "Software to open layouts, before generated. Leave blank system default for .svg is used. "
            'E.g. `[["path to application eg. /Applications/Inkscape.app/Contents/MacOS/inkscape", "path"]]`'
            '\n `"path"` will be replaced with the path to the generated .svg file.'
        ),
    )
    pdf_command: StringProperty(
        name="PDF Command",
        description=(
            "Software to open .pdf, leave blank uses system default. "
            'E.g. `[["path to application eg. /Applications/Inkscape.app/Contents/MacOS/inkscape", "path"]]`'
            '\n `"path"` will be replaced with the path to the generated .pdf file.'
        ),
    )
    spreadsheet_command: StringProperty(
        name="Spreadsheet Command",
        description=(
            'E.g. [["libreoffice", "path"]]'
            '\n `"path"` will be replaced with the path to the generated spreadsheet file.'
        ),
    )
    should_hide_empty_props: BoolProperty(
        name="Hide Empty Properties",
        default=True,
        description="If disabled, this will show empty properties when displaying property sets contents",
    )
    should_setup_workspace: BoolProperty(
        name="Setup Workspace Layout for BIM",
        default=True,
        description=(
            "If enabled, this will add a default workspace dedicated to working with BIM models.\n"
            "It is recommended to keep this `Enabled`"
        ),
    )
    activate_workspace: BoolProperty(
        name="Activate BIM Workspace on Startup",
        default=True,
        description=(
            "If enabled, this will automatically activate the BIM workspace when opening a project.\n"
            "It is recommended to keep this `Enabled`"
        ),
    )
    should_setup_toolbar: BoolProperty(
        name="Always Show Toolbar In 3D Viewport",
        default=True,
        description="If disabled, the toolbar will only load when an IFC model is active",
    )
    should_use_snap: BoolProperty(
        name="Enable Snapping on Startup",
        default=True,
        description=(
            "If enabled, snapping will be enabled on new sessions.\n" "It is recommended to keep this `Enabled`"
        ),
    )
    should_play_chaching_sound: BoolProperty(name="Play A Cha-Ching Sound When Project Costs Updates", default=False)
    tmp_dir: StringProperty(
        name="Temporary Directory",
        description="Path to create and store temporary files. If left blank, a system default will be used.",
        subtype="DIR_PATH",
    )
    decorations_colour: bpy.props.FloatVectorProperty(
        name="Decorations Color", subtype="COLOR", default=(1, 1, 1, 1), min=0.0, max=1.0, size=4
    )
    decorator_color_selected: bpy.props.FloatVectorProperty(
        name="Selected Elements Color",
        subtype="COLOR",
        default=(0.545, 0.863, 0, 1),  # green
        min=0.0,
        max=1.0,
        size=4,
        description="Color of selected verts/edges (used in profile editing mode)",
    )
    decorator_color_unselected: bpy.props.FloatVectorProperty(
        name="Not Selected Elements Color",
        subtype="COLOR",
        default=(1, 1, 1, 1),  # white
        min=0.0,
        max=1.0,
        size=4,
        description="Color of not selected verts/edges (used in profile editing mode)",
    )
    clip_box_cap_color: bpy.props.FloatVectorProperty(
        name="Clip Box Caps Color",
        subtype="COLOR",
        default=(0.0, 0.0, 0.0, 1.0),
        min=0.0,
        max=1.0,
        size=4,
        description="Fill color of clip-box cross-section caps",
    )
    decorator_color_special: bpy.props.FloatVectorProperty(
        name="Special Elements Color",
        subtype="COLOR",
        default=(0.157, 0.565, 1, 1),  # blue
        min=0.0,
        max=1.0,
        size=4,
        description="Color of derived, parametric, or invisible geometry",
    )
    decorator_color_error: bpy.props.FloatVectorProperty(
        name="Warning Elements Color",
        subtype="COLOR",
        default=(1, 0.2, 0.322, 1),  # red
        min=0.0,
        max=1.0,
        size=4,
        description="Color of warning, error, or problem overlays",
    )
    decorator_color_background: bpy.props.FloatVectorProperty(
        name="Background Elements Color",
        subtype="COLOR",
        default=(0.2, 0.2, 0.2, 1),  # grey
        min=0.0,
        max=1.0,
        size=4,
        description="Color of background overlays",
    )
    opening_focus_opacity: bpy.props.IntProperty(
        default=100,
        min=0,
        max=100,
        subtype="PERCENTAGE",
        name="Non-Openings Opacity",
        description=(
            "When modifying openings, other elements of the model will display with some transparency.\n"
            "0 is fully transparent and 100 is fully opaque"
        ),
    )

    bsdd_load_preview_dictionaries: BoolProperty(
        name="Load Preview Dictionaries", description="Load dictionaries marked as Preview status", default=False
    )
    bsdd_load_inactive_dictionaries: BoolProperty(
        name="Load Inactive Dictionaries", description="Load dictionaries marked as Inactive status", default=False
    )
    bsdd_load_test_dictionaries: BoolProperty(
        name="Load Test Dictionaries", description="Load dictionaries that are for testing only", default=False
    )
    bsdd_baseurl: StringProperty(
        name="bSDD API Base URL",
        description="Base URL for data dictionary API requests, e.g. https://api.bsdd.buildingsmart.org/api/",
        default="https://api.bsdd.buildingsmart.org/api/",
    )
    should_disable_undo_on_save: BoolProperty(
        name="Disable Undo When Saving (Faster saves, no undo for you!)", default=False
    )

    def update_autosave_settings(self, context: bpy.types.Context) -> None:
        if self.autosave_enabled:
            tool.Autosave.reset_timer()
        else:
            tool.Autosave.cancel_timer()

    autosave_enabled: BoolProperty(
        name="Enable IFC Autosave Timer",
        description="Periodically remind you to save or automatically create a backup copy of the IFC file",
        default=False,
        update=update_autosave_settings,
    )
    autosave_interval_minutes: bpy.props.IntProperty(
        name="Autosave Interval (Minutes)",
        description="Time between autosave reminders or backups. The timer resets whenever you open or save a project",
        default=10,
        min=1,
        max=1440,
        update=update_autosave_settings,
    )
    autosave_mode: bpy.props.EnumProperty(
        name="Autosave Mode",
        items=[
            (
                "PROMPT",
                "Prompt to Save",
                "Show a dialog offering to save the IFC project when the timer expires",
            ),
            (
                "BACKUP",
                "Automatic Backup",
                "Save a backup copy as filename_autosaved.ifc when the timer expires",
            ),
        ],
        default="PROMPT",
    )
    should_stream: BoolProperty(name="Stream Data From IFC-SPF (Only for advanced users)", default=False)
    should_always_cache: BoolProperty(
        name="Always Cache Geometry",
        description="Whether to always cache geometry regardless of 'Cache' setting during Advanced Project Load.",
    )
    occurrence_name_style: bpy.props.EnumProperty(
        items=[("CLASS", "By Class", ""), ("TYPE", "By Type", ""), ("CUSTOM", "Custom", "")],
        name="Occurrence Name Style",
    )
    occurrence_name_function: bpy.props.StringProperty(
        name="Occurrence Name Function",
        description="Code that will be evaluated to generate occurrence name for CUSTOM occurrence name style",
    )
    gizmos: bpy.props.PointerProperty(type=GizmoPreferences)

    def update_data_dir(self, context: bpy.types.Context) -> None:
        import bonsai.bim.schema

        bonsai.bim.schema.ifc.data_dir = self.data_dir

    def update_cache_dir(self, context: bpy.types.Context) -> None:
        import bonsai.bim.schema

        bonsai.bim.schema.ifc.cache_dir = self.cache_dir

    data_dir: StringProperty(
        default=(platformdirs.user_data_path("bonsai", roaming=True, ensure_exists=True) / "data").__str__(),
        name="Data Directory",
        update=update_data_dir,
        subtype="DIR_PATH",
    )
    cache_dir: StringProperty(
        default=platformdirs.user_cache_dir("bonsai"),
        name="Cache Directory",
        update=update_cache_dir,
        subtype="DIR_PATH",
    )

    pset_dir: StringProperty(
        default=os.path.join("psets") + os.path.sep,
        name="Default Psets Directory",
        subtype="DIR_PATH",
    )
    doc: bpy.props.PointerProperty(type=DocPreferences)
    default_parameters: bpy.props.PointerProperty(
        type=DefaultParameters,
        name="Default Parameters",
        description="Default parameters for BIM elements",
    )

    container_hide_show_isolate: BoolProperty(
        name="Container hide/show/isolate",
        description="Enable container hide/show/isolate feature in the UI",
        default=False,
    )

    chain_filter_with_set_operations: BoolProperty(
        name="NEW Filter mode: Enable chained filters with set operations",
        description=(
            "Enable chaining search filters with set operations: "
            "ADD (union: combine sets), SUBTRACT (difference: remove from set), "
            "FILTER (intersection: only elements in both sets), with autocomplete suggestions for filter values"
        ),
        default=False,
    )

    save_metadata_blend_file: BoolProperty(
        name="Save non ifc data to metadata blend File",
        description=(
            "Save session data (window layout, settings) to a metadata blend file alongside the IFC file. "
            "This file is automatically loaded when opening the project."
        ),
        default=False,
    )
    metadata_blend_file_suffix: StringProperty(
        name="Metadata File Suffix",
        description="Custom suffix for the metadata blend file. Will be appended to the filename (without .ifc).",
        default=".ifc.metadata.blend",
    )

    decorator_font_scale: bpy.props.FloatProperty(
        name="Decorator Font Scale",
        description="Scale factor for decorator font size.",
        default=1.0,
    )

    if TYPE_CHECKING:
        svg2pdf_command: str
        svg2dxf_command: str
        svg_command: str
        layout_svg_command: str
        pdf_command: str
        spreadsheet_command: str
        should_hide_empty_props: bool
        should_setup_workspace: bool
        activate_workspace: bool
        should_setup_toolbar: bool
        should_use_snap: bool
        should_play_chaching_sound: bool
        tmp_dir: str
        decorations_colour: tuple[float, float, float, float]
        decorator_color_selected: tuple[float, float, float, float]
        decorator_color_unselected: tuple[float, float, float, float]
        decorator_color_special: tuple[float, float, float, float]
        decorator_color_error: tuple[float, float, float, float]
        decorator_color_background: tuple[float, float, float, float]
        opening_focus_opacity: int
        bsdd_load_preview_dictionaries: bool
        bsdd_load_inactive_dictionaries: bool
        bsdd_load_test_dictionaries: bool
        bsdd_baseurl: str
        should_disable_undo_on_save: bool
        autosave_enabled: bool
        autosave_interval_minutes: int
        autosave_mode: Literal["PROMPT", "BACKUP"]
        should_stream: bool
        should_always_cache: bool
        occurrence_name_style: Literal["CLASS", "TYPE", "CUSTOM"]
        occurrence_name_function: str
        gizmos: GizmoPreferences
        data_dir: str
        cache_dir: str
        pset_dir: str
        doc: DocPreferences
        default_parameters: DefaultParameters
        container_hide_show_isolate: bool
        chain_filter_with_set_operations: bool
        save_metadata_blend_file: bool
        metadata_blend_file_suffix: str
        decorator_font_scale: float

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        row = layout.row()
        row.operator("bim.open_upstream", text="Visit Homepage").page = "home"
        row.operator("bim.open_upstream", text="Visit Documentation").page = "docs"
        row = layout.row()
        row.operator("bim.open_upstream", text="Visit Wiki").page = "wiki"
        row.operator("bim.open_upstream", text="Visit Community").page = "community"

        row = layout.row()
        if platform.system() == "Darwin":
            row.operator("bim.create_mac_bonsai_app", icon="LOCKVIEW_ON")
        else:
            row.operator("bim.file_associate", icon="LOCKVIEW_ON")
            row.operator("bim.file_unassociate", icon="LOCKVIEW_OFF")

        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Interface", self.draw_interface_settings)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Command Paths", self.draw_commands)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Model", self.draw_model_settings)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Colors", self.draw_decorator_colors)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Directories", self.draw_directories)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Drawing", self.draw_drawing_settings)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Other", self.draw_other_settings)
        bonsai.bim.helper.draw_expandable_panel(self.layout, context, "Extras", self.draw_extras_settings)

    def draw_commands(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "svg2pdf_command")
        layout.prop(self, "svg2dxf_command")
        layout.prop(self, "svg_command")
        layout.prop(self, "layout_svg_command")
        layout.prop(self, "pdf_command")
        layout.prop(self, "spreadsheet_command")

    def draw_interface_settings(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "should_hide_empty_props")
        layout.prop(self, "should_setup_workspace")
        layout.prop(self, "activate_workspace")
        layout.prop(self, "should_setup_toolbar")
        layout.prop(self, "should_use_snap")
        layout.prop(self, "should_play_chaching_sound")

        layout.prop(self.gizmos, "draw_gizmos_in_3d_viewport")
        if self.gizmos.draw_gizmos_in_3d_viewport:
            bonsai.bim.helper.draw_expandable_panel(
                layout,
                context,
                "Gizmos Parameters",
                self.draw_gizmo_parameters,
            )

    def draw_gizmo_parameters(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        """Render one enabled-toggle per parametric feature."""
        layout.label(text="Toggle visibility of gizmos in editing mode")
        box = layout.box()
        annotations = type(self.gizmos).__annotations__
        for feature in tool.Parametric.EDIT_TYPES:
            if feature.name in annotations:
                box.prop(self.gizmos, feature.name)

    def draw_model_settings(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "occurrence_name_style")
        if self.occurrence_name_style == "CUSTOM":
            layout.prop(self, "occurrence_name_function")
        bonsai.bim.helper.draw_expandable_panel(
            layout,
            context,
            "Default Parameters",
            self.draw_default_parameters,
        )

    def draw_directories(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "data_dir")
        layout.prop(self, "cache_dir")
        layout.prop(self, "tmp_dir")

    def draw_drawing_settings(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "pset_dir")
        dprops = self.doc
        layout.prop(dprops, "sheets_dir")
        layout.prop(dprops, "layouts_dir")
        layout.prop(dprops, "titleblocks_dir")
        layout.prop(dprops, "drawings_dir")
        layout.prop(dprops, "stylesheet_path")
        layout.prop(dprops, "schedules_stylesheet_path")
        layout.prop(dprops, "markers_path")
        layout.prop(dprops, "symbols_path")
        layout.prop(dprops, "patterns_path")
        layout.prop(dprops, "shadingstyles_path")
        layout.prop(dprops, "shadingstyle_default")
        row = layout.row()
        row.prop(dprops, "drawing_font")
        row.prop(dprops, "magic_font_scale")
        layout.prop(dprops, "imperial_precision")
        layout.prop(dprops, "tolerance")
        layout.prop(dprops, "classes_to_wireframe")
        layout.prop(dprops, "classes_no_cut")

    def draw_decorator_colors(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.row().prop(self, "decorations_colour")
        layout.row().prop(self, "decorator_color_selected")
        layout.row().prop(self, "decorator_color_unselected")
        layout.row().prop(self, "decorator_color_special")
        layout.row().prop(self, "decorator_color_error")
        layout.row().prop(self, "decorator_color_background")
        bonsai.bim.helper.draw_expandable_panel(
            layout,
            context,
            "Clip Box",
            self.draw_clip_box_colors,
        )

    def draw_clip_box_colors(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.row().prop(self, "clip_box_cap_color")

    def draw_default_parameters(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        box = layout.box()
        for entry in tool.Parametric.EDIT_TYPES:
            if not entry.has_default_parameters:
                continue
            props = getattr(self.default_parameters, entry.name)
            draw_props = getattr(_model_ui, f"draw_{entry.name}_properties")
            bonsai.bim.helper.draw_expandable_panel(
                box,
                context,
                entry.name.replace("_", " ").title(),
                lambda _layout, _context, _draw=draw_props, _props=props: _draw(_layout, _props),
            )

    def draw_other_settings(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "opening_focus_opacity")
        layout.prop(self, "should_disable_undo_on_save")
        layout.separator()
        layout.label(text="Autosave:")
        layout.prop(self, "autosave_enabled")
        if self.autosave_enabled:
            layout.prop(self, "autosave_interval_minutes")
            layout.prop(self, "autosave_mode")
        layout.prop(self, "should_stream")
        layout.prop(self, "should_always_cache")
        layout.label(text="bSDD:")
        layout.prop(self, "bsdd_load_preview_dictionaries")
        layout.prop(self, "bsdd_load_inactive_dictionaries")
        layout.prop(self, "bsdd_load_test_dictionaries")
        layout.prop(self, "bsdd_baseurl")

    def draw_extras_settings(self, layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
        layout.prop(self, "container_hide_show_isolate")
        row = layout.row(align=True)
        row.prop(self, "chain_filter_with_set_operations")
        row.operator("bim.open_uri", text="", icon="HELP").uri = "https://community.osarch.org/discussion/3270"
        layout.prop(self, "save_metadata_blend_file")
        if self.save_metadata_blend_file:
            row = layout.row()
            row.separator()
            row.prop(self, "metadata_blend_file_suffix")

            bprops = tool.Blender.get_bim_props()
            if tab_visibilities := bprops.tab_visibilities:
                row = layout.row()
                row.operator("bim.reset_ui_layout", icon="LOOP_BACK")
                row = layout.row(align=True)
                row.template_list(
                    "BIM_UL_tab_visibilities", "", bprops, "tab_visibilities", bprops, "active_tab_visibility_index"
                )
                row.template_list(
                    "BIM_UL_panel_visibilities",
                    "",
                    bprops,
                    "panel_visibilities",
                    bprops,
                    "active_panel_visibility_index",
                )
            else:
                row = layout.row()
                row.operator("bim.manage_tab_visibility", icon="PREFERENCES")
        layout.prop(self, "decorator_font_scale")


# Scene panel groups
class BIM_PT_tabs(Panel):
    bl_idname = "BIM_PT_tabs"
    bl_label = "Bonsai"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 0
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        if not UIData.is_loaded:
            UIData.load()
        aprops = tool.Blender.get_active_area_props(context)

        row = self.layout.row()
        row.alignment = "CENTER"
        for tab in UIData.data["tabs"]:
            self.draw_tab_entry(row, tab[1], tab[0], tab[2], aprops.tab == tab[0])
        row.operator("bim.switch_tab", text="", emboss=False, icon="UV_SYNC_SELECT")

        row = self.layout.row()
        # Yes, that's right.
        row.alignment = "CENTER"
        row.scale_y = 0.2

        for tab in UIData.data["tabs"]:
            # Draw a little underscore below the active tab icon.
            if aprops.tab == tab[0]:
                row.prop(aprops, "active_tab", text="", icon="BLANK1")
            else:
                row.prop(aprops, "inactive_tab", text="", icon="BLANK1", emboss=False)
        row.prop(aprops, "inactive_tab", text="", icon="BLANK1", emboss=False)  # space for Switch

        row = self.layout.row()
        row.prop(aprops, "tab", text="")

        if bonsai.REINSTALLED_BBIM_VERSION:
            box = self.layout.box()
            box.alert = True
            box.label(text="Bonsai requires Blender to restart.", icon="ERROR")
            box.label(text="Bonsai was reinstalled in the current session:")
            box.label(text=f"{bonsai.FIRST_INSTALLED_BBIM_VERSION} -> {bonsai.REINSTALLED_BBIM_VERSION}")
            box.operator("bim.restart_blender", text="Restart Blender", icon="BLENDER")

        if bonsai.last_error:
            box = self.layout.box()
            box.alert = True
            row = box.row(align=True)
            row.label(text="Bonsai experienced an error :(", icon="ERROR")
            row.operator("bim.close_error", text="", icon="CANCEL")
            if platform.system() == "Windows":
                box.operator("wm.console_toggle", text="View the console for full logs.", icon="CONSOLE")
            else:
                box.label(text="View the console for full logs.", icon="CONSOLE")
            box.operator("bim.copy_debug_information", text="Copy Error Message To Clipboard")
            op = box.operator("bim.open_uri", text="How Can I Fix This?")
            op.uri = "https://docs.bonsaibim.org/guides/troubleshooting.html"

        if not tool.Ifc.get():
            return

        bim_props = tool.Blender.get_bim_props()
        if bim_props.has_blend_warning:
            box = self.layout.box()
            box.alert = True
            row = box.row(align=True)
            row.label(text="Your model may be outdated", icon="ERROR")
            op = row.operator("bim.open_uri", text="", icon="QUESTION")
            op.uri = "https://docs.bonsaibim.org/guides/troubleshooting.html#saving-and-loading-blend-files"
            row.operator("bim.close_blend_warning", text="", icon="CANCEL")

        if is_cache_locked_by_other_process():
            box = self.layout.box()
            box.alert = True
            row = box.row(align=True)
            row.label(text="IFC Already Open in Another Blender Instance", icon="ERROR")
            row.operator("bim.dismiss_multi_instance_warning", text="", icon="CANCEL")
            draw_multiline_text(
                box.column(align=True),
                "This file is open in another Blender instance. Editing the same "
                "IFC from two instances at once can lose your work or display "
                "outdated geometry. Close the other Blender instances to continue safely.",
                context=context,
            )

        pprops = tool.Project.get_project_props()
        if pending := pprops.pending_opening_recut:
            box = self.layout.box()
            box.alert = True
            box.label(text="Opening Cuts Skipped", icon="ERROR")
            draw_multiline_text(
                box.column(align=True),
                f"{len(pending)} element(s) had too many openings to cut during load. "
                f"Apply to recompute their meshes, or dismiss to leave them as they are.",
                context=context,
            )
            row = box.row(align=True)
            row.operator("bim.select_pending_opening_cuts", text="Select Elements", icon="RESTRICT_SELECT_OFF")
            row.operator("bim.apply_pending_opening_cuts", text="Apply Openings", icon="PLAY")
            row.operator("bim.dismiss_pending_opening_cuts", text="", icon="CANCEL")

        if pending := pprops.pending_array_repair:
            box = self.layout.box()
            box.alert = True
            box.label(text="Arrays With Missing Children", icon="ERROR")
            draw_multiline_text(
                box.column(align=True),
                f"{len(pending)} array parent(s) reference child GUIDs that don't exist in this file. "
                f"The arrays loaded incomplete. Select to inspect, or dismiss.",
                context=context,
            )
            row = box.row(align=True)
            row.operator("bim.select_pending_array_repair", text="Select Elements", icon="RESTRICT_SELECT_OFF")
            row.operator("bim.dismiss_pending_array_repair", text="", icon="CANCEL")

        gprops = tool.Geometry.get_geometry_props()
        # Check that Blender mode and IFC Mode do match.
        if context.mode == "OBJECT" and gprops.mode in ("OBJECT", "ITEM"):
            pass
        elif context.mode.startswith("EDIT") and gprops.mode == "EDIT":
            pass
        # Occurs when user wasn't using IFC mode or TAB/Esc hotkeys to change mode.
        # E.g. if user used TAB to set object's mode to EDIT and then used
        # Blender mode property to set it back to OBJECT.
        #
        # We show warning only for objects connected to IFC,
        # so users with vanilla Blender objects won't be affected.
        elif tool.Geometry.get_active_or_representation_obj():
            box = self.layout.box()
            box.alert = True
            row = box.row(align=True)
            row.label(text="Geometry changes will be lost", icon="ERROR")
            op = row.operator("bim.open_uri", text="", icon="QUESTION")
            op.uri = "https://docs.bonsaibim.org/guides/troubleshooting.html#incompatible-blender-features"

        if (o := context.active_object) and tool.Ifc.get_entity(o) and tool.Geometry.is_scaled(o):
            box = self.layout.box()
            box.alert = True
            row = box.row(align=True)
            row.label(text="Object scaling will be lost", icon="ERROR")
            op = row.operator("bim.open_uri", text="", icon="QUESTION")
            op.uri = "https://docs.bonsaibim.org/guides/troubleshooting.html#incompatible-blender-features"

    def draw_tab_entry(
        self, row: bpy.types.UILayout, icon: int | str, tab_name: str, enabled: bool = True, highlight: bool = True
    ) -> None:
        tab_entry = row.row(align=True)
        if isinstance(icon, int):
            tab_entry.operator("bim.set_tab", text="", emboss=highlight, icon_value=icon).tab = tab_name
        else:
            tab_entry.operator("bim.set_tab", text="", emboss=highlight, icon=icon).tab = tab_name
        tab_entry.enabled = enabled


class BIM_PT_tab_new_project_wizard(Panel):
    bl_idname = "BIM_PT_tab_new_project_wizard"
    bl_label = "New Project Wizard"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if not tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return False
        bim_props = tool.Blender.get_bim_props()
        pprops = tool.Project.get_project_props()
        if pprops.is_loading:
            return False
        elif tool.Ifc.get() or bim_props.ifc_file:
            return False
        return True

    def draw(self, context):
        pass


class BIM_PT_tab_project_info(Panel):
    bl_idname = "BIM_PT_tab_project_info"
    bl_label = "Project Info"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            bim_props = tool.Blender.get_bim_props()
            pprops = tool.Project.get_project_props()
            if pprops.is_loading:
                return True
            elif tool.Ifc.get() or bim_props.ifc_file:
                return True

    def draw(self, context):
        pass


class BIM_PT_tab_spatial(Panel):
    bl_idname = "BIM_PT_tab_spatial"
    bl_label = "Spatial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_project_setup(Panel):
    bl_idname = "BIM_PT_tab_project_setup"
    bl_label = "Project Setup"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_stakeholders(Panel):
    bl_idname = "BIM_PT_tab_stakeholders"
    bl_label = "Stakeholders"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_collaboration(Panel):
    bl_idname = "BIM_PT_tab_collaboration"
    bl_label = "Collaboration"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "QUALITY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_grouping_and_filtering(Panel):
    bl_idname = "BIM_PT_tab_grouping_and_filtering"
    bl_label = "Grouping and Filtering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"HEADER_LAYOUT_EXPAND"}
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass

    def draw_header(self, context):
        # Draws help button on the right
        row = self.layout.row(align=True)
        row.label(text="")  # empty text occupies the left of the row
        row.operator("bim.open_uri", text="", icon="HELP").uri = (
            "https://docs.ifcopenshell.org/ifcopenshell-python/selector_syntax.html"
        )


class BIM_PT_tab_geometry(Panel):
    bl_idname = "BIM_PT_tab_geometry"
    bl_label = "Geometry"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "PROJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_status(Panel):
    bl_idname = "BIM_PT_tab_status"
    bl_label = "Status"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SCHEDULING"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_qto(Panel):
    bl_idname = "BIM_PT_tab_qto"
    bl_label = "Quantity Take-off"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SCHEDULING"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_resources(Panel):
    bl_idname = "BIM_PT_tab_resources"
    bl_label = "Resources"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SCHEDULING"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_cost(Panel):
    bl_idname = "BIM_PT_tab_cost"
    bl_label = "Cost"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SCHEDULING"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_sequence(Panel):
    bl_idname = "BIM_PT_tab_sequence"
    bl_label = "Construction Scheduling"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SCHEDULING"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_structural(Panel):
    bl_idname = "BIM_PT_tab_structural"
    bl_label = "Structural"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "STRUCTURE"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_services(Panel):
    bl_idname = "BIM_PT_tab_services"
    bl_label = "Services"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SERVICES"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_lighting(Panel):
    bl_idname = "BIM_PT_tab_lighting"
    bl_label = "Lighting"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SERVICES"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_zones(Panel):
    bl_idname = "BIM_PT_tab_zones"
    bl_label = "Zones"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SERVICES"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_solar_analysis(Panel):
    bl_idname = "BIM_PT_tab_solar_analysis"
    bl_label = "Solar Analysis"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "SERVICES"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_quality_control(Panel):
    bl_idname = "BIM_PT_tab_quality_control"
    bl_label = "Quality Control"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "QUALITY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_clash_detection(Panel):
    bl_idname = "BIM_PT_tab_clash_detection"
    bl_label = "Clash Detection"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bim_tab_name = "QUALITY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_sandbox(Panel):
    bl_idname = "BIM_PT_tab_sandbox"
    bl_label = "Sandbox"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bim_tab_name = "QUALITY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        row = self.layout.row()
        row.label(text="More Experimental Than Usual", icon="ERROR")


# Object panel groups
class BIM_PT_tab_object_metadata(Panel):
    bl_idname = "BIM_PT_tab_object_metadata"
    bl_label = "Object"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "OBJECT"

    @classmethod
    def poll(cls, context):
        props = tool.Project.get_project_props()
        if (
            tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname)
            and tool.Ifc.get()
            and (obj := context.active_object)
            # Hide links empty handles.
            and (
                obj.type != "EMPTY"
                or not obj.instance_collection
                or not any(l.empty_handle == obj for l in props.links)
            )
        ):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_placement(Panel):
    bl_idname = "BIM_PT_tab_placement"
    bl_label = "Placement"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if (
            tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname)
            and tool.Ifc.get()
            and (obj := context.active_object)
            and tool.Ifc.get_entity(obj)
        ):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_representations(Panel):
    bl_idname = "BIM_PT_tab_representations"
    bl_label = "Representations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_geometric_relationships(Panel):
    bl_idname = "BIM_PT_tab_geometric_relationships"
    bl_label = "Geometric Relationships"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_options = {"DEFAULT_CLOSED"}
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_parametric_geometry(Panel):
    bl_idname = "BIM_PT_tab_parametric_geometry"
    bl_label = "Parametric Geometry"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_options = {"DEFAULT_CLOSED"}
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_object_materials(Panel):
    bl_idname = "BIM_PT_tab_object_materials"
    bl_label = "Object Materials"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_materials(Panel):
    bl_idname = "BIM_PT_tab_materials"
    bl_label = "Materials"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_styles(Panel):
    bl_idname = "BIM_PT_tab_styles"
    bl_label = "Styles"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_profiles(Panel):
    bl_idname = "BIM_PT_tab_profiles"
    bl_label = "Profiles"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "GEOMETRY"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_sheets(Panel):
    bl_idname = "BIM_PT_tab_sheets"
    bl_label = "Sheets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "DRAWINGS"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_drawings(Panel):
    bl_idname = "BIM_PT_tab_drawings"
    bl_label = "Drawings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "DRAWINGS"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_schedules(Panel):
    bl_idname = "BIM_PT_tab_schedules"
    bl_label = "Schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "DRAWINGS"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_references(Panel):
    bl_idname = "BIM_PT_tab_references"
    bl_label = "References"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "DRAWINGS"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_misc(Panel):
    bl_idname = "BIM_PT_tab_misc"
    bl_label = "Misc"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_options = {"DEFAULT_CLOSED"}
    bim_tab_name = "OBJECT"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname) and tool.Ifc.get():
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_handover(Panel):
    bl_idname = "BIM_PT_tab_handover"
    bl_label = "Handover"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bim_tab_name = "FM"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        pass


class BIM_PT_tab_operations(Panel):
    bl_idname = "BIM_PT_tab_operations"
    bl_label = "Operations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 2
    bim_tab_name = "FM"

    @classmethod
    def poll(cls, context):
        if tool.Blender.should_show_panel(context, cls.bim_tab_name, cls.bl_idname):
            return True

    def draw(self, context):
        pass


def refresh():
    UIData.is_loaded = False
    EnumData.data.clear()


class EnumData:
    data: dict[str, tool.Blender.BLENDER_ENUM_ITEMS] = {}

    @classmethod
    def get_data(cls, identifier: str) -> tool.Blender.BLENDER_ENUM_ITEMS:
        if identifier not in EnumData.data:
            cls.data[identifier] = getattr(cls, identifier)()
        return cls.data[identifier]

    @classmethod
    def organizations(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        organizations = tool.Ifc.get().by_type("IfcOrganization")
        return natsorted(((str(e.id()), e.Name, "") for e in organizations), key=lambda x: x[1])

    @classmethod
    def postal_addresses(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        addresses = tool.Ifc.get().by_type("IfcPostalAddress")
        items = ((str(e.id()), (e.Description or "Undescribed"), "") for e in addresses)
        items = natsorted(items, key=lambda x: x[1])
        return items


class UIData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "version": cls.version(),
            "menu_icon_color_mode": cls.icon_color_mode("user_interface.wcol_menu.text"),
            "tabs": cls.tabs(),
        }
        cls.is_loaded = True

    @classmethod
    def version(cls):
        return tool.Blender.get_bonsai_version()

    @classmethod
    def icon_color_mode(cls, color_path):
        return tool.Blender.detect_icon_color_mode(color_path)

    @classmethod
    def tabs(cls):
        hidden_tabs = [t.name for t in tool.Blender.get_bim_props().tab_visibilities if not t.is_visible]
        color_mode = cls.icon_color_mode("user_interface.wcol_regular.text")
        is_ifc_project = bool(tool.Ifc.get())
        return [
            tab
            for tab in [
                ("PROJECT", bonsai.bim.icons[f"{color_mode}_ifc"].icon_id, True),
                ("OBJECT", "FILE_3D", is_ifc_project),
                ("GEOMETRY", "MATERIAL", is_ifc_project),
                ("DRAWINGS", "DOCUMENTS", is_ifc_project),
                ("SERVICES", "NETWORK_DRIVE", is_ifc_project),
                ("STRUCTURE", "EDITMODE_HLT", is_ifc_project),
                ("SCHEDULING", "NLA", is_ifc_project),
                ("FM", "PACKAGE", True),
                ("QUALITY", "COMMUNITY", True),
                ("BOOKMARK", "SOLO_ON", is_ifc_project),
            ]
            if tab[0] not in hidden_tabs
        ]


def draw_statusbar(self, context):
    if not UIData.is_loaded:
        UIData.load()
    bonsai_version = f"Bonsai v{UIData.data['version']}"
    layout = self.layout
    row = layout.row()
    row.operator("bim.show_system_info", text=bonsai_version, emboss=False)


def draw_custom_context_menu(self: bpy.types.Menu, context: bpy.types.Context) -> None:
    # https://blender.stackexchange.com/a/275555/86891
    if (
        not hasattr(context, "button_pointer")
        or not hasattr(context, "button_prop")
        or not hasattr(context.button_prop, "identifier")
    ):
        return
    # E.g. `bim.props.Attribute`.
    prop_struct: bpy.types.bpy_struct = context.button_pointer
    # E.g. `IntProperty("int_value")`
    prop: bpy.types.Property = context.button_prop
    prop_name = prop.identifier
    # TODO: when `prop_struct` doesn't have `prop_name`?
    if not hasattr(prop_struct, prop_name):
        return
    prop_value = getattr(prop_struct, prop_name, ...)
    if prop_value is ...:
        return
    version = tool.Ifc.get_schema()
    assert self.layout
    layout = self.layout

    if isinstance(prop_struct, Attribute):
        attr = prop_struct

        # Hacky way to get Attribute containing description for enumerated values.
        pset_enum_identifier = ".enumerated_value.enumerated_values["
        attr_path = prop_struct.path_from_id()
        if pset_enum_identifier in attr_path:
            attr_path = attr_path.partition(pset_enum_identifier)[0]
            assert (data_block := prop_struct.id_data)
            attr = data_block.path_resolve(attr_path)
            assert isinstance(attr, IfcProperty)
            attr = attr.metadata

        description = attr.description
        ifc_class = attr.ifc_class
        url = ""
        if ifc_class:
            try:
                url = get_entity_doc(version, ifc_class).get("spec_url", "")
            except RuntimeError:  # It's not an Entity Attribute. Let's try a Property Set attribute.
                doc = get_property_set_doc(version, ifc_class)
                if doc:
                    url = doc.get("spec_url", "")
                else:  # It's a custom property set. No URL available
                    url = ""
        attr_name = attr.name
        if description:
            layout.separator()
            op_description = layout.operator("bim.show_description", text="IFC Description", icon="INFO")
            op_description.attr_name = attr_name
            op_description.description = description
            op_description.url = url
        if attr_name:
            op = layout.operator("bim.copy_text_to_clipboard", text="Copy Attribute Name", icon="COPYDOWN")
            op.text = attr_name
    elif isinstance(prop_struct, BIMBSDDProperties) and (
        active_bsdd_property := getattr(context, "active_bsdd_property", None)
    ):
        # Context Menu for bSDD Properties
        assert isinstance(active_bsdd_property, BSDDProperty)
        op_description = layout.operator("bim.show_bsdd_description", text="bSDD Description", icon="INFO")
        op_description.url = active_bsdd_property.uri
    else:
        # Basically context menu for any Blender property will end up here,
        # and will check 3 types of docs.
        # So at least we're skipping all non-string properties.
        if not isinstance(prop_value, str):
            return

        docs = None
        # Ugly but we can't know which type of data is under the cursor so we test everything until it clicks
        try:
            docs = get_entity_doc(version, prop_value)
            if docs is None:
                raise RuntimeError
        except (RuntimeError, AttributeError):
            try:
                docs = get_type_doc(version, prop_value)
                if docs is None:
                    raise RuntimeError
            except (RuntimeError, AttributeError):
                try:
                    docs = get_property_set_doc(version, prop_value)
                    if docs is None:
                        raise RuntimeError
                except (RuntimeError, AttributeError):
                    pass
        if docs:
            url = docs.get("spec_url", "")
            if url:
                layout.separator()
                url_op = layout.operator("bim.open_uri", icon="URL", text="Online IFC Documentation")
                url_op.uri = url


def draw_multiline_text(
    layout: bpy.types.UILayout,
    text: str,
    *,
    context: bpy.types.Context | None = None,
) -> None:
    """Render a read-only text box that wraps long text."""
    assert layout

    region_width = 200
    if context and context.region:
        region_width = context.region.width

    approximate_char_width = 7  # Empirical average width for Blender UI font (px)
    wrap_width = max(20, int(region_width / approximate_char_width))

    for paragraph in text.splitlines():
        if not paragraph:
            layout.label(text="")
            continue

        for line in textwrap.wrap(paragraph, width=wrap_width):
            layout.label(text=line)


class BIM_PT_decorators_overlay(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"
    bl_parent_id = "VIEW3D_PT_overlay"
    bl_label = "Bonsai Decorators"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        view = context.space_data
        overlay = view.overlay

        georeference_props = tool.Georeference.get_georeference_props()
        aggregate_props = tool.Aggregate.get_aggregate_props()
        nest_props = tool.Nest.get_nest_props()
        model_props = tool.Model.get_model_props()
        system_props = tool.System.get_system_props()
        display_all = overlay.show_overlays

        col = layout.column()
        col.active = display_all

        row = col.row(align=True)
        row.prop(georeference_props, "should_visualise", text="Georeference")
        row.prop(georeference_props, "visualization_scale", text="Size", slider=True)
        row = col.row(align=True)
        row.prop(aggregate_props, "aggregate_decorator", text="Aggregate")
        row = col.row(align=True)
        row.prop(nest_props, "nest_decorator", text="Nest")
        row = col.row(align=True)
        row.prop(model_props, "show_wall_axis", text="Wall Axis")
        row = col.row(align=True)
        row.prop(model_props, "show_slab_direction", text="Slab Direction")
        row = col.row(align=True)
        row.prop(model_props, "show_paths", text="Element Paths")
        row.prop(system_props, "should_draw_decorations", text="System Decorations")
        row = col.row(align=True)
        row.prop(model_props, "show_bounding_box", text="Bounding Box Dimensions")
        row = col.row(align=True)
        row.prop(model_props, "show_cut_decorator", text="Cut Decorator")
        row.prop(model_props, "show_cut_decorator_fill", text="Fill Cut Decorator")
        clip_box_props = tool.ClipBox.get_scene_props(context.scene)
        row = col.row(align=True)
        # Grey out the toggles when there is no clip box to act on, so the
        # user can see the controls but can't flip a switch that does nothing.
        row.enabled = bool(clip_box_props.clip_boxes)
        row.prop(clip_box_props, "enabled", text="Enable Clipping")
        row.prop(clip_box_props, "show_caps", text="Show Caps")


class BIM_PT_snappping(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"
    bl_parent_id = "VIEW3D_PT_snapping"
    bl_label = "Bonsai Snap Target"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        prop = tool.Snap.get_snap_props()
        layout = self.layout
        col = layout.column(align=True)
        col.prop(prop, "vertex", toggle=True, icon="SNAP_VERTEX")
        col.prop(prop, "edge", toggle=True, icon="SNAP_EDGE")
        col.prop(prop, "edge_center", toggle=True, icon="SNAP_MIDPOINT")
        col.prop(prop, "edge_intersection", toggle=True, icon="SNAP_GRID")
        col.prop(prop, "face", toggle=True, icon="SNAP_FACE")
        groups = tool.Snap.get_snap_groups()
        row = layout.row(align=True)
        row.label(text="Bonsai Target Selection")
        row = layout.row(align=True)
        row.prop(groups, "object", toggle=True)
        row.prop(groups, "polyline", toggle=True)
        row.prop(groups, "measure", toggle=True)
