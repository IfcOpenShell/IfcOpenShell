# Ifc4D - IFC scheduling utility
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Ifc4D.
#
# Ifc4D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc4D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc4D.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

from ifc4d.wpattern import AstaCalendarWorkPattern


class TestAstaCalendarWorkPatternMissingDays:
    def test_non_english_partial_week_fills_missing_days_in_english(self) -> None:
        # A French calendar naming only 5 weekdays. day_names is already
        # translated to English, so the missing days must be computed
        # against the English day set, not the source language's set.
        pattern = '<"Lundi">0,0<"Mardi">0,0<"Mercredi">0,0<"Jeudi">0,0<"Vendredi">0,0'
        wp = AstaCalendarWorkPattern(pattern, work_type_ids=[1])

        day_names = [slot["DayOfWeek"] for slot in wp.dict_wp]

        assert len(wp.dict_wp) == 7
        assert set(day_names) == {
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        }
