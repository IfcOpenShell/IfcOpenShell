# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


import datetime

import ifcopenshell.util.date as subject


class TestReadableIFCDuration:
    def test_run(self):
        assert subject.readable_ifc_duration("P0Y0M1DT16H0M0S") == "1D 16h"
        assert subject.readable_ifc_duration("P2Y3M1W4DT5H45M30S") == "2Y 3M 1W 4D 5h 45m 30s"
        assert subject.readable_ifc_duration("PT40H") == "40h"

        # Float values.
        assert subject.readable_ifc_duration("P2.5D") == "2.5D"
        assert subject.readable_ifc_duration("PT1.5H") == "1.5h"


class TestDurationRoundTrip:
    """Regression tests for #6964.

    DimitriosThe's EVA_POC_20250628_.ifc contains both IFCDURATION('PT2H30M')
    and, on a sibling resource that should hold the same value,
    IFCDURATION('PT2H29M59.999867S'), 133 microseconds short of 2.5 hours.
    The exact statement he raised: "there should be absolutely no rounding
    whatsoever, happening ever anywhere. The calculation is something that
    should be happening without any rounding in bonsai and ifcopenshell."

    These tests assert that an IfcDuration round-tripped through
    ifc2datetime/datetime2ifc comes back exactly as written, whether the
    value is whole seconds or carries a fractional second.
    """

    def test_whole_value_survives_the_round_trip(self):
        # This is the exact clean value from his file.
        value = "PT2H30M"
        parsed = subject.ifc2datetime(value)
        assert subject.datetime2ifc(parsed, "IfcDuration") == value

    def test_fractional_seconds_survive_the_round_trip(self):
        value = "PT1H2M3.456789S"
        parsed = subject.ifc2datetime(value)
        assert parsed.total_seconds() == 3723.456789
        assert subject.datetime2ifc(parsed, "IfcDuration") == value

    def test_timedelta2duration_preserves_microseconds(self):
        td = datetime.timedelta(seconds=8999, microseconds=999867)
        duration = subject.timedelta2duration(td)
        assert duration.total_seconds() == 8999.999867

    def test_sub_second_duration_is_not_floored_to_the_whole_second(self):
        # Before the fix, any fractional second was silently dropped by
        # timedelta2duration, so a duration ending in ".999867S" would come
        # back as a whole second short.
        value = "PT29M59.999867S"
        parsed = subject.ifc2datetime(value)
        assert parsed.total_seconds() == 1799.999867
