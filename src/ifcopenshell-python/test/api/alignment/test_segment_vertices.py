# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

import pytest
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit


def test_segment_vertices():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths
    )

    # test the horizontal alignment geometry segments
    expect = [[(500.0, 2500.0), (2142.2379952109395, 1436.01482000418), None, None],
              [(2142.2379952109395, 1436.01482000418), (3660.446122847804, 2050.7361731594674), (3340.0, 659.9999999999998), (2685.9792975637306, 2275.267699722618)],
              [(3660.4461228478035, 2050.7361731594674), (4084.115884236641, 3889.4629375870213), None, None],
              [(4084.115884236641, 3889.4629375870218), (5469.395067206271, 4847.5663099476205), (4340.0, 5000.000000000001), (5302.199415841732, 3608.7985293830834)],
              [(5469.395067206271, 4847.56630994762), (7019.971366858418, 4638.286073184753), None, None],
              [(7019.971366858417, 4638.286073184753), (7790.932128312586, 4006.7307645487535), (7600.0, 4560.0), (6892.902671821368, 3696.8225599557054)],
              [(7790.932128312587, 4006.7307645487535), (8480.0, 2010.0000000000002), None, None],
              [(8480.0, 2010.0000000000002), (8480.0, 2010.0000000000002), None, None]
          ]
    curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    for segment,expected in zip(curve.Segments,expect):
        s,e,pi,cc = ifcopenshell.api.alignment.segment_vertices(file,segment)
        assert s == pytest.approx(expected[0])
        assert e == pytest.approx(expected[1])
        assert pi == pytest.approx(expected[2])
        assert cc == pytest.approx(expected[3])


    # test vertical curve segments
    expect = [[(0.0, 100.0), (1200.0, 121.0), None, None],
              [(1200.0, 121.0), (2799.99999384661, 127.00000006153391), (1999.9999969233054, 134.99999994615786), (2218.1436363635016, -58058.63636362867)],
              [(2800.0, 127.0), (4400.0, 111.0), None, None],
              [(4400.0, 111.0), (5599.999994508736, 116.9999998901747), (4999.999997254367, 105.00000002745632), (4800.039999999177, 40114.99999991764)],
              [(5600.0, 117.0), (6400.0, 133.0), None, None],
              [(6400.0, 133.0), (8399.999995932576, 133.0000000813485), (7399.999997966288, 152.99999995932575), (7399.999999999187, -49866.99999995936)],
              [(8400.0, 133.0), (9400.0, 113.0), None, None],
              [(9400.0, 113.0), (10199.99999633883, 103.00000001830585), (9799.999998169415, 105.00000003661171), (10466.733333334432, 53449.66666672164)],
              [(10200.0, 103.0), (12800.0, 90.0), None, None],
              [(12800.0, 90.0), (12800.0, 90.0), None, None]
    ]
    curve = ifcopenshell.api.alignment.get_curve(alignment)
    for segment,expected in zip(curve.Segments,expect):
        s,e,pi,cc = ifcopenshell.api.alignment.segment_vertices(file,segment)
        assert s == pytest.approx(expected[0])
        assert e == pytest.approx(expected[1])
        assert pi == pytest.approx(expected[2])
        assert cc == pytest.approx(expected[3])

test_segment_vertices()
