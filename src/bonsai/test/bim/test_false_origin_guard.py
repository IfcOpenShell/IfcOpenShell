# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""Which placement is allowed to become the false origin.

Exporters exist that put map coordinates on the IfcSite while leaving the
building tree hanging off the world origin. Subtracting that placement moves
geometry that already sits at the origin hundreds of kilometres away, where
single precision viewport maths quantises vertices and doors flicker, render
chunky or disappear. Measured on ifc-georeferencer-AC20-FZK-Haus 1 wall.ifc:
site at 433832, 477738; wall geometry at 11.7, 9.7; the offset took the wall
from 15.2 m off the Blender origin to 645309.5 m.

A false origin the model's geometry does sit under stays accepted, measured on
the same corpus: BWFI_X_3_ELT 38211.9 m to 0.6 m, QTO-Test_extracted
7087311.5 m to 1225.8 m, Rampe_V6_251028_v3 5665787.1 m to 2832889.8 m."""

import ifcopenshell
import numpy as np
import pytest

pytestmark = pytest.mark.georeference


def _placement(ifc, translation):
    return ifc.create_entity(
        "IfcLocalPlacement",
        RelativePlacement=ifc.create_entity(
            "IfcAxis2Placement3D",
            Location=ifc.create_entity("IfcCartesianPoint", Coordinates=tuple(float(c) for c in translation)),
        ),
    )


def _project_with_site(site_translation):
    ifc = ifcopenshell.file(schema="IFC4")
    project = ifc.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new())
    site = ifc.create_entity(
        "IfcSite",
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=_placement(ifc, site_translation),
    )
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        RelatingObject=project,
        RelatedObjects=[site],
    )
    return ifc, site


class _Route:
    """Records which false origin branch ``guess_false_origin`` took."""

    def __init__(self, monkeypatch, geometry_point):
        from bonsai.tool.loader import Loader

        self.taken = None
        monkeypatch.setattr(Loader, "unit_scale", 1.0, raising=False)
        monkeypatch.setattr(Loader, "get_geometry_point", classmethod(lambda cls, f: geometry_point))
        monkeypatch.setattr(
            Loader,
            "guess_false_origin_and_project_north",
            classmethod(lambda cls, f, element: self._record("placement")),
        )
        monkeypatch.setattr(
            Loader,
            "guess_false_origin_from_elements",
            classmethod(lambda cls, f: self._record("elements")),
        )

    def _record(self, name):
        self.taken = name


def _limit_settings(monkeypatch, limit=1000.0):
    from bonsai.tool.loader import Loader

    class Settings:
        distance_limit = limit

    monkeypatch.setattr(Loader, "settings", Settings(), raising=False)


def test_site_placement_the_geometry_sits_under_is_a_false_origin(monkeypatch):
    from bonsai.tool.loader import Loader

    _limit_settings(monkeypatch)
    ifc, _site = _project_with_site((433832.0, 477738.0, 0.0))
    route = _Route(monkeypatch, np.array([433840.0, 477745.0, 0.0]))
    Loader.guess_false_origin(ifc)
    assert route.taken == "placement"


def test_site_placement_the_geometry_does_not_sit_under_is_not_a_false_origin(monkeypatch):
    from bonsai.tool.loader import Loader

    _limit_settings(monkeypatch)
    ifc, _site = _project_with_site((433832.0, 477738.0, 0.0))
    route = _Route(monkeypatch, np.array([11.7, 9.7, 0.0]))
    Loader.guess_false_origin(ifc)
    assert route.taken == "elements"


def test_a_file_without_geometry_keeps_the_placement_false_origin(monkeypatch):
    from bonsai.tool.loader import Loader

    _limit_settings(monkeypatch)
    ifc, _site = _project_with_site((433832.0, 477738.0, 0.0))
    route = _Route(monkeypatch, None)
    Loader.guess_false_origin(ifc)
    assert route.taken == "placement"


def test_moves_geometry_towards_origin_measures_both_distances(monkeypatch):
    from bonsai.tool.loader import Loader

    _limit_settings(monkeypatch)
    monkeypatch.setattr(Loader, "unit_scale", 1.0, raising=False)
    ifc, site = _project_with_site((433832.0, 477738.0, 0.0))

    monkeypatch.setattr(Loader, "get_geometry_point", classmethod(lambda cls, f: np.array([11.7, 9.7, 0.0])))
    assert Loader.moves_geometry_towards_origin(ifc, site) is False

    monkeypatch.setattr(Loader, "get_geometry_point", classmethod(lambda cls, f: np.array([433840.0, 477745.0, 0.0])))
    assert Loader.moves_geometry_towards_origin(ifc, site) is True


def test_offset_point_only_reports_geometry_that_is_far_away(monkeypatch):
    from bonsai.tool.loader import Loader

    _limit_settings(monkeypatch)
    monkeypatch.setattr(Loader, "unit_scale", 1.0, raising=False)
    ifc = ifcopenshell.file(schema="IFC4")

    monkeypatch.setattr(Loader, "get_geometry_point", classmethod(lambda cls, f: np.array([11.7, 9.7, 0.0])))
    assert Loader.get_offset_point(ifc) is None

    monkeypatch.setattr(
        Loader, "get_geometry_point", classmethod(lambda cls, f: np.array([4581141.2384, 5407691.0, 339.2027]))
    )
    np.testing.assert_allclose(Loader.get_offset_point(ifc), [4581141.238, 5407691.0, 339.203])
