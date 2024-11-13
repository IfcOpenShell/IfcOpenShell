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
from . import ui, prop, operator, handler, gizmos, workspace

classes = (
    operator.ActivateDrawing,
    operator.ActivateDrawingFromSheet,
    operator.ActivateDrawingStyle,
    operator.ActivateModel,
    operator.AddAnnotation,
    operator.AddAnnotationType,
    operator.AddDrawing,
    operator.AddDrawingStyle,
    operator.AddDrawingStyleAttribute,
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
    operator.ContractTargetView,
    operator.ConvertSVGToDXF,
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
    operator.ExpandSheet,
    operator.ExpandTargetView,
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
    operator.RemoveDrawingStyleAttribute,
    operator.RemoveReference,
    operator.RemoveSchedule,
    operator.RemoveSheet,
    operator.RemoveTextLiteral,
    operator.ResizeText,
    operator.SaveDrawingStyle,
    operator.SaveDrawingStylesData,
    operator.SelectAllDrawings,
    operator.SelectAllSheets,
    operator.SelectAssignedProduct,
    operator.SelectDocIfcFile,
    operator.OpenDocumentationWebUi,
    prop.Variable,
    prop.Drawing,
    prop.Document,
    prop.DrawingStyle,
    prop.Sheet,
    prop.DocProperties,
    prop.BIMCameraProperties,
    prop.Literal,
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
    gizmos.UglyDotGizmo,
    gizmos.DotGizmo,
    gizmos.DimensionLabelGizmo,
    gizmos.ExtrusionGuidesGizmo,
    gizmos.ExtrusionWidget,
    workspace.LaunchAnnotationTypeManager,
    workspace.Hotkey,
)


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
