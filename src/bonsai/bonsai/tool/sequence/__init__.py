# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
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



from __future__ import annotations
from collections.abc import Iterable
import ifcopenshell

# --- STEP 1: Import all the refactored module classes ---
from .props_sequence import PropsSequence
from .camera_sequence import CameraSequence
from .text_sequence import TextSequence
from .task_bars_sequence import TaskBarsSequence
from .date_utils_sequence import DateUtilsSequence
from .color_management_sequence import ColorManagementSequence
from .task_tree_sequence import TaskTreeSequence
from .task_icom_sequence import TaskIcomSequence
from .snapshot_sequence import SnapshotSequence
from .animation_setup_sequence import AnimationSetupSequence
from .animation_frames_sequence import AnimationFramesSequence
from .animation_baker_sequence import AnimationBakerSequence
from .task_attributes_sequence import TaskAttributesSequence
from .schedule_management_sequence import ScheduleManagementSequence
from .calendar_sequence import CalendarSequence
from .variance_sequence import VarianceSequence
from .sync_config_sequence import SyncConfigSequence
from .sequence_relations_sequence import SequenceRelationsSequence
from .ui_helpers_sequence import UiHelpersSequence
from .gantt_chart_sequence import GanttChartSequence
from .schedule_utils_sequence import ScheduleUtilsSequence

# --- STEP 2: Assemble the final "Sequence" class with the CORRECT INHERITANCE ORDER ---
class Sequence(
    # --- LEVEL 4: High-Level Tools (depend on almost everything else) ---
    SyncConfigSequence,

    # --- LEVEL 3: Core Engines and Main Logic ---
    SnapshotSequence,
    VarianceSequence,
    # --- REFACTORED ANIMATION LOGIC ---
    AnimationBakerSequence,       # 3. Executes the animation in Blender
    AnimationFramesSequence,      # 2. Calculates the frame data
    AnimationSetupSequence,       # 1. Configures the base settings
    # --- END OF ANIMATION LOGIC ---

    # --- LEVEL 2: Managers and Complex Utilities ---
    ScheduleManagementSequence,
    TaskTreeSequence,
    ScheduleUtilsSequence,
    TextSequence,
    TaskBarsSequence,
    
    # --- LEVEL 1: Base Modules and Data Providers ---
    CalendarSequence,
    SequenceRelationsSequence,
    TaskAttributesSequence,
    ColorManagementSequence,
    TaskIcomSequence,
    CameraSequence,
    DateUtilsSequence,
    UiHelpersSequence,
    GanttChartSequence,

    # --- LEVEL 0: The Fundamental Base for Properties ---
    PropsSequence,

):
    """
    The main Sequence tool class, assembled from refactored mixins
    with a consistent Method Resolution Order (MRO).
    """
    ELEMENT_STATUSES = ("NEW", "EXISTING", "DEMOLISH", "TEMPORARY", "OTHER", "NOTKNOWN", "UNSET")

    @classmethod
    def are_entities_same_class(cls, entities: list[ifcopenshell.entity_instance]) -> bool:
        if not entities: return False
        if len(entities) == 1: return True
        first_class = entities[0].is_a()
        for entity in entities:
            if entity.is_a() != first_class: return False
        return True

    @classmethod
    def select_products(cls, products: Iterable[ifcopenshell.entity_instance]) -> None:
        import bpy
        import bonsai.tool as tool
        [obj.select_set(False) for obj in bpy.context.selected_objects]
        for product in products:
            obj = tool.Ifc.get_object(product)
            obj.select_set(True) if obj else None