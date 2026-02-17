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



import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty
from typing import TYPE_CHECKING
from . import callbacks_prop as callbacks



class IFCStatus(PropertyGroup):
    name: StringProperty(name="Name")
    is_visible: BoolProperty(
        name="Is Visible", default=True, update=lambda x, y: (None, bpy.ops.bim.activate_status_filters())[0]
    )
    if TYPE_CHECKING:
        name: str
        is_visible: bool


class BIMStatusProperties(PropertyGroup):
    is_enabled: BoolProperty(name="Is Enabled")
    statuses: CollectionProperty(name="Statuses", type=IFCStatus)
    if TYPE_CHECKING:
        is_enabled: bool
        statuses: bpy.types.bpy_prop_collection_idprop[IFCStatus]


class DatePickerProperties(PropertyGroup):
    display_date: StringProperty(
        name="Display Date",
        description="Needed to keep track of what month is currently opened in date picker without affecting the currently selected date.",
    )
    selected_date: StringProperty(name="Selected Date")
    selected_hour: IntProperty(min=0, max=23, update=callbacks.update_selected_date)
    selected_min: IntProperty(min=0, max=59, update=callbacks.update_selected_date)
    selected_sec: IntProperty(min=0, max=59, update=callbacks.update_selected_date)
    if TYPE_CHECKING:
        display_date: str
        selected_date: str
        selected_hour: int
        selected_min: int
        selected_sec: int


class BIMDateTextProperties(PropertyGroup):
    start_frame: IntProperty(name="Start Frame")
    total_frames: IntProperty(name="Total Frames")
    start: StringProperty(name="Start")
    finish: StringProperty(name="Finish")
    if TYPE_CHECKING:
        start_frame: int
        total_frames: int
        start: str
        finish: str





