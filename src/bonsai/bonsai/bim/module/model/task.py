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

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date


def calculate_quantities(usecase_path, ifc_file, settings):
    if not set(["ScheduleStart", "ScheduleFinish", "ScheduleDuration"]).intersection(
        set(settings["attributes"].keys())
    ):
        return
    element = settings["task_time"]
    if not element.ScheduleDuration:
        return
    task = [e for e in ifc_file.get_inverse(element) if e.is_a("IfcTask")][0]
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=task, name="Qto_TaskBaseQuantities"
    )
    ifcopenshell.api.run(
        "pset.edit_qto",
        ifc_file,
        should_run_listeners=False,
        qto=qto,
        properties={
            "StandardWork": ifcopenshell.util.date.ifc2datetime(element.ScheduleDuration).days,
        },
    )
