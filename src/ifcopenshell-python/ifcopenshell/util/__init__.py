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

"""Utility functions for extracting IFC data

Data in IFC files is represented using relationships between IFC entities. To
extract data like "what properties does this wall have" involves looping
through these relationships which can be tedious.

This module makes it easy to get commonly requested data from IFC
relationships, such as properties of a wall, what elements are connected to
pipes, dates from work schedules, filtering maintainable elements, and more.

The most commonly used utilities to help you get started are:

- See :mod:`ifcopenshell.util.element` which contains a lot of useful functions
  for getting most common relationships on elements.
- See :func:`ifcopenshell.util.element.get_psets` to get all properties of an
  entity, like a wall.
- See :func:`ifcopenshell.util.element.get_type` to get the corresponding type
  object (e.g. the wall type definition) of a single occurrence (e.g. an
  individual wall).
- See :func:`ifcopenshell.util.placement.get_local_placement` to get the XYZ
  placement point of a single object.
- See :func:`ifcopenshell.util.unit.calculate_unit_scale` to convert between SI
  units and project units.
- See :mod:`ifcopenshell.util.shape` to calculate quantities from processed
  geometry.
"""
