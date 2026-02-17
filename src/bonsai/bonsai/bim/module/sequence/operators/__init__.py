# File: .../sequence/operators/__init__.py
# Description: Central registration point for all sequence operators.

import bpy
from . import camera_operators
from . import io_operators
from . import animation_operators
from . import navigation_operators
from . import config_operators
from . import schedule_task_operators
from . import work_schedule_operators
from . import filter_operators
from . import schedule_assignment_operators
from . import schedule_calendar_operators
from . import hud_operators
from . import copy_sync_3d_operators
from . import schedule_sequence_operators
from . import schedule_operators
from . import work_plan_operators
from . import color_scheme_operators
from .animation_operators import CreateAnimation, ClearAnimation, AddAnimationTaskType, RemoveAnimationTaskType, ClearPreviousAnimation, ClearPreviousSnapshot, SyncAnimationByDate

# A single tuple containing all operator classes to be registered.

classes = (
    # from camera_operators.py
    camera_operators.RefreshCameraSelectors,
    camera_operators.ForceCameraPropertyUpdate,
    camera_operators.SetActiveAnimationCamera,
    camera_operators.SetActiveSnapshotCamera,
    camera_operators.TestCameraDetection,
    camera_operators.DebugListAllCameras,
    camera_operators.ResetCameraSettings,
    camera_operators.Align4DCameraToView,
    camera_operators.UpdateCameraOnly,
    camera_operators.AddCameraByMode,
    camera_operators.AddSnapshotCamera,
    camera_operators.AlignSnapshotCameraToView,
    camera_operators.AddAnimationCamera,
    camera_operators.DeleteAnimationCamera,
    camera_operators.DeleteSnapshotCamera,

    # from io_operators.py
    io_operators.ImportWorkScheduleCSV,
    io_operators.ImportP6,
    io_operators.ImportP6XER,
    io_operators.ImportPP,
    io_operators.ImportMSP,
    io_operators.ExportMSP,
    io_operators.ExportP6,

    # from schedule_task_operators.py
    schedule_task_operators.LoadTaskProperties,
    schedule_task_operators.AddTask,
    schedule_task_operators.AddSummaryTask,
    schedule_task_operators.ExpandTask,
    schedule_task_operators.ContractTask,
    schedule_task_operators.RemoveTask,
    schedule_task_operators.EnableEditingTask,
    schedule_task_operators.DisableEditingTask,
    schedule_task_operators.EditTask,
    schedule_task_operators.CopyTaskAttribute,
    schedule_task_operators.CalculateTaskDuration,
    schedule_task_operators.ExpandAllTasks,
    schedule_task_operators.ContractAllTasks,
    schedule_task_operators.CopyTask,
    schedule_task_operators.GoToTask,
    schedule_task_operators.ReorderTask,
    schedule_task_operators.RefreshTaskOutputCounts,
    
    # from work_schedule_operators.py
    work_schedule_operators.AssignWorkSchedule,
    work_schedule_operators.UnassignWorkSchedule,
    work_schedule_operators.AddWorkSchedule,
    work_schedule_operators.EditWorkSchedule,
    work_schedule_operators.RemoveWorkSchedule,
    work_schedule_operators.CopyWorkSchedule,
    work_schedule_operators.EnableEditingWorkSchedule,
    work_schedule_operators.EnableEditingWorkScheduleTasks,
    work_schedule_operators.DisableEditingWorkSchedule,
    work_schedule_operators.SortWorkScheduleByIdAsc,
    work_schedule_operators.VisualiseWorkScheduleDateRange,
    work_schedule_operators.SelectWorkScheduleProducts,
    work_schedule_operators.SelectUnassignedWorkScheduleProducts,

    # from schedule_assignment_operators.py 
    schedule_assignment_operators.AssignPredecessor,
    schedule_assignment_operators.AssignSuccessor,
    schedule_assignment_operators.UnassignPredecessor,
    schedule_assignment_operators.UnassignSuccessor,
    schedule_assignment_operators.AssignProduct,
    schedule_assignment_operators.UnassignProduct,
    schedule_assignment_operators.AssignProcess,
    schedule_assignment_operators.UnassignProcess,
    schedule_assignment_operators.AssignRecurrencePattern,
    schedule_assignment_operators.UnassignRecurrencePattern,
    schedule_assignment_operators.AssignLagTime,
    schedule_assignment_operators.UnassignLagTime,
    schedule_assignment_operators.SelectTaskRelatedProducts,
    schedule_assignment_operators.SelectTaskRelatedInputs,
    schedule_assignment_operators.LoadProductTasks,

    # from schedule_calendar_operators.py 
    schedule_calendar_operators.AddWorkCalendar,
    schedule_calendar_operators.EditWorkCalendar,
    schedule_calendar_operators.RemoveWorkCalendar,
    schedule_calendar_operators.EnableEditingWorkCalendar,
    schedule_calendar_operators.DisableEditingWorkCalendar,
    schedule_calendar_operators.EnableEditingWorkCalendarTimes,
    schedule_calendar_operators.AddWorkTime,
    schedule_calendar_operators.EnableEditingWorkTime,
    schedule_calendar_operators.DisableEditingWorkTime,
    schedule_calendar_operators.EditWorkTime,
    schedule_calendar_operators.RemoveWorkTime,
    schedule_calendar_operators.AddTimePeriod,
    schedule_calendar_operators.RemoveTimePeriod,
    schedule_calendar_operators.EnableEditingTaskTime,
    schedule_calendar_operators.EditTaskTime,
    schedule_calendar_operators.DisableEditingTaskTime,
    schedule_calendar_operators.EnableEditingTaskCalendar,
    schedule_calendar_operators.EditTaskCalendar,
    schedule_calendar_operators.RemoveTaskCalendar,
    
    # from filter_operators.py
    filter_operators.EnableStatusFilters,
    filter_operators.DisableStatusFilters,
    filter_operators.ActivateStatusFilters,
    filter_operators.SelectStatusFilter,
    filter_operators.AssignStatus,
    filter_operators.AddTaskFilter,
    filter_operators.RemoveTaskFilter,
    filter_operators.ClearAllTaskFilters,
    filter_operators.ApplyTaskFilters,
    filter_operators.ApplyLookaheadFilter,
    filter_operators.UpdateSavedFilterSet,
    filter_operators.SaveFilterSet,
    filter_operators.LoadFilterSet,
    filter_operators.RemoveFilterSet,
    filter_operators.ExportFilterSet,
    filter_operators.ImportFilterSet,
    filter_operators.Bonsai_DatePicker,
    filter_operators.FilterDatePicker,
    


    # from hud_operators.py 
    hud_operators.ArrangeScheduleTexts,
    hud_operators.Fix3DTextAlignment,
    hud_operators.SetupTextHUD,
    hud_operators.ClearTextHUD,
    hud_operators.UpdateTextHUDPositions,
    hud_operators.UpdateTextHUDScale,
    hud_operators.ToggleTextHUD,
    hud_operators.Setup3DLegendHUD,
    hud_operators.Clear3DLegendHUD,
    hud_operators.Update3DLegendHUD,
    hud_operators.Toggle3DLegendHUD,
    hud_operators.EnableScheduleHUD,
    hud_operators.DisableScheduleHUD,
    hud_operators.ToggleScheduleHUD,
    hud_operators.RefreshScheduleHUD,
    hud_operators.LegendHudcolortypeScrollUp,
    hud_operators.LegendHudcolortypeScrollDown,
    hud_operators.LegendHudTogglecolortypeVisibility,

    # from copy_sync_3d_operators.py
    copy_sync_3d_operators.Copy3D,
    copy_sync_3d_operators.Sync3D,
    copy_sync_3d_operators.SnapshotWithcolortypesFixed,
    copy_sync_3d_operators.SnapshotWithcolortypes,

    # from schedule_sequence_operators.py 
    schedule_sequence_operators.EnableEditingTaskSequence,
    schedule_sequence_operators.EnableEditingSequenceAttributes,
    schedule_sequence_operators.EditSequenceAttributes,
    schedule_sequence_operators.DisableEditingSequence,
    schedule_sequence_operators.EnableEditingSequenceTimeLag,
    schedule_sequence_operators.EditSequenceTimeLag,

    # from schedule_operators.py 
    schedule_operators.RecalculateSchedule,
    schedule_operators.GenerateGanttChart,
    schedule_operators.AddTaskColumn,
    schedule_operators.SetupDefaultTaskColumns,
    schedule_operators.RemoveTaskColumn,
    schedule_operators.SetTaskSortColumn,
    schedule_operators.CreateBaseline,
    schedule_operators.CalculateScheduleVariance,
    schedule_operators.ClearScheduleVariance,
    schedule_operators.DeactivateVarianceColorMode,
    schedule_operators.RefreshTask3DCounts,
    schedule_operators.AddTaskBars,
    schedule_operators.ClearTaskBars,
    schedule_operators.GuessDateRange,

    # from work_plan_operators.py 
    work_plan_operators.AddWorkPlan,
    work_plan_operators.EditWorkPlan,
    work_plan_operators.RemoveWorkPlan,
    work_plan_operators.EnableEditingWorkPlan,
    work_plan_operators.DisableEditingWorkPlan,
    work_plan_operators.EnableEditingWorkPlanSchedules,

    # from color_scheme_operators.py
    color_scheme_operators.AddAnimationColorSchemes,
    color_scheme_operators.RemoveAnimationColorSchemes,
    color_scheme_operators.SaveAnimationColorSchemesSetInternal,
    color_scheme_operators.LoadAnimationColorSchemesSetInternal,
    color_scheme_operators.RemoveAnimationColorSchemesSetInternal,
    color_scheme_operators.ExportAnimationColorSchemesSetToFile,
    color_scheme_operators.ImportAnimationColorSchemesSetFromFile,
    color_scheme_operators.CleanupTaskcolortypeMappings,
    color_scheme_operators.UpdateActivecolortypeGroup,
    color_scheme_operators.InitializeColorTypeSystem,
    color_scheme_operators.BIM_OT_init_default_all_tasks,
    color_scheme_operators.CopyTaskCustomcolortypeGroup,
    color_scheme_operators.LoadDefaultAnimationColors,
    color_scheme_operators.SaveAnimationColorScheme,
    color_scheme_operators.LoadAnimationColorScheme,
    color_scheme_operators.ANIM_OT_group_stack_add,
    color_scheme_operators.ANIM_OT_group_stack_remove,
    color_scheme_operators.ANIM_OT_group_stack_move,
    color_scheme_operators.VerifyCustomGroupsExclusion,
    color_scheme_operators.ShowcolortypeUIState,
    color_scheme_operators.BIM_OT_cleanup_colortype_groups,

    # from animation_operators.py
    animation_operators.CreateAnimation,
    animation_operators.ClearAnimation,
    animation_operators.AddAnimationTaskType,
    animation_operators.RemoveAnimationTaskType,
    animation_operators.ClearPreviousAnimation,
    animation_operators.ClearPreviousSnapshot,
    animation_operators.SyncAnimationByDate,
    
    # from navigation_operators.py
    navigation_operators.NavigateColumnsLeft,
    navigation_operators.NavigateColumnsRight,
    navigation_operators.NavigateColumnsHome,
    navigation_operators.NavigateColumnsEnd,
    
    # from config_operators.py
    config_operators.VisualiseWorkScheduleDate,
    config_operators.LoadAndActivatecolortypeGroup,
    config_operators.SetupDefaultcolortypes,
    config_operators.UpdateDefaultcolortypeColors,
    config_operators.BIM_OT_verify_colortype_json,
    config_operators.BIM_OT_fix_colortype_hide_at_end_immediate,
    config_operators.RefreshSnapshotTexts,
    config_operators.CreateStaticSnapshotTexts,
    config_operators.BIM_OT_show_performance_stats,
    config_operators.BIM_OT_clear_performance_cache,
)

def register():
    """Registers all operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregisters all operator classes in reverse order."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# Explicit imports for main module access.
ExportP6 = io_operators.ExportP6
ExportMSP = io_operators.ExportMSP
ImportWorkScheduleCSV = io_operators.ImportWorkScheduleCSV
ImportP6 = io_operators.ImportP6
ImportP6XER = io_operators.ImportP6XER
ImportPP = io_operators.ImportPP
ImportMSP = io_operators.ImportMSP
ResetCameraSettings = camera_operators.ResetCameraSettings