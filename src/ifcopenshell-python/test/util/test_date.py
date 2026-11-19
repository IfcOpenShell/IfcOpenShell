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

import isodate

import ifcopenshell.util.date as subject


class TestReadableIFCDuration:
    def test_run(self):
        assert subject.readable_ifc_duration("P0Y0M1DT16H0M0S") == "1D 16h"
        assert subject.readable_ifc_duration("P2Y3M1W4DT5H45M30S") == "2Y 3M 1W 4D 5h 45m 30s"
        assert subject.readable_ifc_duration("PT40H") == "40h"

        # Float values.
        assert subject.readable_ifc_duration("P2.5D") == "2.5D"
        assert subject.readable_ifc_duration("PT1.5H") == "1.5h"


class TestParseDuration:
    def test_iso_duration(self):
        assert subject.parse_duration("PT1.5H") == datetime.timedelta(hours=1.5)
        assert subject.parse_duration("P2DT4H") == datetime.timedelta(days=2, hours=4)

    def test_fuzzy_duration(self):
        assert subject.parse_duration("3D") == datetime.timedelta(days=3)
        assert subject.parse_duration("2H") == datetime.timedelta(hours=2)
        assert subject.parse_duration("90S") == datetime.timedelta(seconds=90)
        assert subject.parse_duration("2D 4H") == datetime.timedelta(days=2, hours=4)
        assert subject.parse_duration("1h30m") == datetime.timedelta(hours=1, minutes=30)

    def test_fuzzy_minutes(self):
        assert subject.parse_duration("30MIN") == datetime.timedelta(minutes=30)
        assert subject.parse_duration("30 min") == datetime.timedelta(minutes=30)
        assert subject.parse_duration("2H 30MIN") == datetime.timedelta(hours=2, minutes=30)
        assert subject.parse_duration("1D 30MIN") == datetime.timedelta(days=1, minutes=30)
        # A lone "M" is still months, as in an ISO duration.
        assert subject.parse_duration("2M") == isodate.Duration(months=2)
