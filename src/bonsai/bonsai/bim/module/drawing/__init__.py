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

import bpy

import bonsai.tool as tool

from . import gizmos, handler, operator, prop, ui, workspace

classes = (
    operator.ActivateDrawing,
    operator.ActivateDrawingFromSheet,
    operator.ActivateDrawingByAnnotation,
    operator.ActivateDrawingStyle,
    operator.ActivateModel,
    operator.AddAnnotation,
    operator.AddAnnotationType,
    operator.AddDrawing,
    operator.AddDrawingStyle,
    operator.AddDrawingToSheet,
    operator.AddReference,
    operator.AddReferenceImage,
    operator.AddReferenceToSheet,
    operator.AddSchedule,
    operator.AddScheduleToSheet,
    operator.AddSheet,
    operator.AddTextLiteral,
    operator.AssignSelectedObjectAsProduct,
    operator.BuildSchedule,
    operator.CleanWireframes,
    operator.ContractSheet,
    operator.ConvertSVGToDXF,
    operator.CopyTextToSelection,
    operator.CreateDrawing,
    operator.CreateSheets,
    operator.DisableAddAnnotationType,
    operator.DisableEditingAssignedProduct,
    operator.DisableEditingDrawings,
    operator.DisableEditingReferences,
    operator.DisableEditingSchedules,
    operator.DisableEditingSheets,
    operator.DisableEditingText,
    operator.DuplicateDrawing,
    operator.DuplicateSheet,
    operator.EditAssignedProduct,
    operator.EditElementFilter,
    operator.EditSheet,
    operator.EditText,
    operator.EditTextPopup,
    operator.EnableAddAnnotationType,
    operator.EnableEditingAssignedProduct,
    operator.EnableEditingElementFilter,
    operator.EnableEditingText,
    operator.ExcludeAnnotation,
    operator.ExpandSheet,
    operator.ToggleElementValuesPanel,
    operator.ToggleElementValuesCategory,
    operator.SelectElementValues,
    operator.InsertFormattedLiteralPopup,
    operator.AddElementValueRow,
    operator.RemoveElementValueRow,
    operator.ElementValueSuggestionsPopup,
    operator.FormatElementValueRow,
    operator.ApplyElementValueRowsToLiteral,
    operator.ShowCategoryHelp,
    operator.ShowElementValuesInstructions,
    operator.LoadDrawings,
    operator.LoadReferences,
    operator.LoadSchedules,
    operator.LoadSheets,
    operator.OpenDrawing,
    operator.OpenLayout,
    operator.OpenReference,
    operator.OpenSchedule,
    operator.OpenSheet,
    operator.OrderTextLiteralDown,
    operator.OrderTextLiteralUp,
    operator.ReloadDrawingStyles,
    operator.RemoveDrawing,
    operator.RemoveDrawingFromSheet,
    operator.RemoveDrawingStyle,
    operator.RemoveReference,
    operator.RemoveSchedule,
    operator.RemoveSheet,
    operator.RemoveTextLiteral,
    operator.SaveDrawingStyle,
    operator.SaveDrawingStylesData,
    operator.SelectAllDrawings,
    operator.SelectAllSheets,
    operator.SelectAssignedProduct,
    operator.SelectSimilarTextLiteralValue,
    operator.ToggleTargetView,
    operator.OpenDocumentationWebUi,
    operator.FilterSelectedObjectsIfIntersectedByCamera,
    prop.Variable,
    prop.Drawing,
    prop.Document,
    prop.DrawingStyle,
    prop.Sheet,
    prop.DocProperties,
    prop.BIMCameraProperties,
    prop.ElementValueRow,
    prop.LiteralProps,
    prop.BIMTextProperties,
    prop.BIMAssignedProductProperties,
    prop.BIMAnnotationProperties,
    ui.BIM_PT_sheets,
    ui.BIM_PT_drawings,
    ui.BIM_PT_camera,
    ui.BIM_PT_element_filters,
    ui.BIM_PT_drawing_underlay,
    ui.BIM_PT_schedules,
    ui.BIM_PT_references,
    ui.BIM_PT_product_assignments,
    ui.BIM_PT_text,
    ui.BIM_UL_drawinglist,
    ui.BIM_UL_sheets,
    # Core gizmos (shared across modules)
    gizmos.BIM_OT_gizmo_value_input,
    gizmos.GizmoArrow,
    gizmos.GizmoArrow2D,
    gizmos.GizmoCone,
    gizmos.GizmoDimension,
    gizmos.GizmoLockOpen,
    gizmos.GizmoLockClosed,
    gizmos.GizmoArc,
    gizmos.GizmoLinkToggle,
    gizmos.GizmoFillet,
    gizmos.GizmoWallCornerIcon,
    gizmos.GizmoWallTeeIcon,
    gizmos.GizmoPen,
    gizmos.GizmoValidate,
    gizmos.GizmoCancel,
    gizmos.GizmoPlus,
    gizmos.GizmoMinus,
    gizmos.GizmoTrash,
    gizmos.GizmoArrayParent,
    gizmos.GizmoArrayAll,
    gizmos.GizmoArrayLayerIndicator,
    gizmos.GizmoCountLabel,
    gizmos.GizmoMerge,
    gizmos.GizmoSplit,
    gizmos.GizmoUnjoin,
    gizmos.GizmoExtend,
    gizmos.GizmoExtendVertical,
    gizmos.GizmoOffsetExterior,
    gizmos.GizmoOffsetCenter,
    gizmos.GizmoOffsetInterior,
    gizmos.GizmoAddOpening,
    gizmos.GizmoCycle,
    gizmos.GizmoMenu,
    # Drawing-specific gizmos
    gizmos.UglyDotGizmo,
    gizmos.ExtrusionGuidesGizmo,
    gizmos.ExtrusionWidget,
    workspace.LaunchAnnotationTypeManager,
    workspace.Hotkey,
)


def menu_func(self, context):
    active_obj = context.active_object
    if active_obj:
        element = tool.Ifc.get_entity(active_obj)
        if element and element.is_a("IfcAnnotation") and element.ObjectType in ["SECTION", "ELEVATION"]:
            self.layout.operator("bim.activate_drawing_by_annotation", text="Go to Drawing")


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.AnnotationTool, after={"bim.bim_tool"}, separator=True, group=False)
    bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
    bpy.types.Scene.BIMAnnotationProperties = bpy.props.PointerProperty(type=prop.BIMAnnotationProperties)
    bpy.types.Camera.BIMCameraProperties = bpy.props.PointerProperty(type=prop.BIMCameraProperties)
    bpy.types.Object.BIMAssignedProductProperties = bpy.props.PointerProperty(type=prop.BIMAssignedProductProperties)
    bpy.types.Object.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
    bpy.types.TextCurve.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
    bpy.app.handlers.load_post.append(handler.load_post)
    bpy.app.handlers.depsgraph_update_pre.append(handler.depsgraph_update_pre_handler)
    bpy.types.VIEW3D_MT_image_add.append(ui.add_object_button)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.AnnotationTool)
    del bpy.types.Scene.DocProperties
    del bpy.types.Scene.BIMAnnotationProperties
    del bpy.types.Camera.BIMCameraProperties
    del bpy.types.Object.BIMAssignedProductProperties
    del bpy.types.Object.BIMTextProperties
    del bpy.types.TextCurve.BIMTextProperties
    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.app.handlers.depsgraph_update_pre.remove(handler.depsgraph_update_pre_handler)
    bpy.types.VIEW3D_MT_image_add.remove(ui.add_object_button)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)
