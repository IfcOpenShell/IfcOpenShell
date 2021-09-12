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
    operator.AddDrawing,
    operator.CreateDrawing,
    operator.AddAnnotation,
    operator.AddSheet,
    operator.OpenSheet,
    operator.AddDrawingToSheet,
    operator.CreateSheets,
    operator.OpenView,
    operator.OpenViewCamera,
    operator.ActivateView,
    operator.SelectDocIfcFile,
    operator.GenerateReferences,
    operator.ResizeText,
    operator.AddVariable,
    operator.RemoveVariable,
    operator.PropagateTextData,
    operator.RemoveDrawing,
    operator.AddDrawingStyle,
    operator.RemoveDrawingStyle,
    operator.SaveDrawingStyle,
    operator.ActivateDrawingStyle,
    operator.EditVectorStyle,
    operator.RemoveSheet,
    operator.AddSchedule,
    operator.RemoveSchedule,
    operator.SelectScheduleFile,
    operator.BuildSchedule,
    operator.AddScheduleToSheet,
    operator.AddDrawingStyleAttribute,
    operator.RemoveDrawingStyleAttribute,
    operator.RefreshDrawingList,
    operator.CleanWireframes,
    operator.CopyGrid,
    operator.AddSectionsAnnotations,
    prop.Variable,
    prop.Drawing,
    prop.Schedule,
    prop.DrawingStyle,
    prop.Sheet,
    prop.DocProperties,
    prop.BIMCameraProperties,
    prop.BIMTextProperties,
    ui.BIM_PT_camera,
    ui.BIM_PT_drawing_underlay,
    ui.BIM_PT_drawings,
    ui.BIM_PT_schedules,
    ui.BIM_PT_sheets,
    ui.BIM_PT_text,
    ui.BIM_PT_annotation_utilities,
    ui.BIM_UL_drawinglist,
    gizmos.UglyDotGizmo,
    gizmos.DotGizmo,
    gizmos.DimensionLabelGizmo,
    gizmos.ExtrusionGuidesGizmo,
    gizmos.ExtrusionWidget,
)


def register():
    bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
    bpy.types.Camera.BIMCameraProperties = bpy.props.PointerProperty(type=prop.BIMCameraProperties)
    bpy.types.TextCurve.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
    bpy.app.handlers.load_post.append(handler.toggleDecorationsOnLoad)
    bpy.app.handlers.depsgraph_update_pre.append(handler.depsgraph_update_pre_handler)


def unregister():
    del bpy.types.Scene.DocProperties
    del bpy.types.Camera.BIMCameraProperties
    del bpy.types.TextCurve.BIMTextProperties
    bpy.app.handlers.load_post.remove(handler.toggleDecorationsOnLoad)
    bpy.app.handlers.depsgraph_update_pre.remove(handler.depsgraph_update_pre_handler)
