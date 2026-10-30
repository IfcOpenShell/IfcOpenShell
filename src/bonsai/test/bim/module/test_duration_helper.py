# This file was generated with the assistance of an AI coding tool.

import pytest

from bonsai.bim.module.sequence.helper import parse_duration_as_blender_props

ZERO = {"years": 0, "months": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}


class TestParseDurationAsBlenderProps:
    @pytest.mark.parametrize("value", ["1D", "", "WORKTIME"])
    def test_malformed_duration_is_treated_as_empty(self, value):
        assert parse_duration_as_blender_props(value) == ZERO

    def test_valid_duration(self):
        assert parse_duration_as_blender_props("P2D")["days"] == 2
