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
from . import ui, prop, operator, handler, gizmos

classes = (
    operator.ActivateDrawingStyle,
    operator.ActivateView,
    operator.AddAnnotation,
    operator.AddDrawing,
    operator.AddDrawingStyle,
    operator.AddDrawingStyleAttribute,
    operator.AddDrawingToSheet,
    operator.AddSchedule,
    operator.AddScheduleToSheet,
    operator.AddSectionsAnnotations,
    operator.AddSheet,
    operator.BuildSchedule,
    operator.CleanWireframes,
    operator.ContractSheet,
    operator.CopyGrid,
    operator.CreateDrawing,
    operator.CreateSheets,
    operator.DisableEditingAssignedProduct,
    operator.DisableEditingDrawings,
    operator.DisableEditingSchedules,
    operator.DisableEditingSheets,
    operator.DisableEditingText,
    operator.EditAssignedProduct,
    operator.EditText,
    operator.EditVectorStyle,
    operator.EnableEditingAssignedProduct,
    operator.EnableEditingText,
    operator.ExpandSheet,
    operator.LoadDrawings,
    operator.LoadSchedules,
    operator.LoadSheets,
    operator.OpenSchedule,
    operator.OpenSheet,
    operator.OpenView,
    operator.RemoveDrawing,
    operator.RemoveDrawingFromSheet,
    operator.RemoveDrawingStyle,
    operator.RemoveDrawingStyleAttribute,
    operator.RemoveSchedule,
    operator.RemoveSheet,
    operator.ResizeText,
    operator.SaveDrawingStyle,
    operator.SelectDocIfcFile,
    prop.Variable,
    prop.Drawing,
    prop.Schedule,
    prop.DrawingStyle,
    prop.Sheet,
    prop.DocProperties,
    prop.BIMCameraProperties,
    prop.BIMTextProperties,
    prop.BIMAssignedProductProperties,
    ui.BIM_PT_camera,
    ui.BIM_PT_drawing_underlay,
    ui.BIM_PT_annotation_utilities,
    ui.BIM_PT_sheets,
    ui.BIM_PT_drawings,
    ui.BIM_PT_schedules,
    ui.BIM_PT_product_assignments,
    ui.BIM_PT_text,
    ui.BIM_UL_drawinglist,
    ui.BIM_UL_sheets,
    gizmos.UglyDotGizmo,
    gizmos.DotGizmo,
    gizmos.DimensionLabelGizmo,
    gizmos.ExtrusionGuidesGizmo,
    gizmos.ExtrusionWidget,
)


def register():
    bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
    bpy.types.Camera.BIMCameraProperties = bpy.props.PointerProperty(type=prop.BIMCameraProperties)
    bpy.types.Object.BIMAssignedProductProperties = bpy.props.PointerProperty(type=prop.BIMAssignedProductProperties)
    bpy.types.Object.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
    bpy.types.TextCurve.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
    bpy.app.handlers.load_post.append(handler.toggleDecorationsOnLoad)
    bpy.app.handlers.depsgraph_update_pre.append(handler.depsgraph_update_pre_handler)


def unregister():
    del bpy.types.Scene.DocProperties
    del bpy.types.Camera.BIMCameraProperties
    del bpy.types.Object.BIMAssignedProductProperties
    del bpy.types.Object.BIMTextProperties
    del bpy.types.TextCurve.BIMTextProperties
    bpy.app.handlers.load_post.remove(handler.toggleDecorationsOnLoad)
    bpy.app.handlers.depsgraph_update_pre.remove(handler.depsgraph_update_pre_handler)
