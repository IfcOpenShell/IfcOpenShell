# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

"""
When true return inverses without an aggregate specifier as a single
element or None. Example:

>>> import ifcopenshell
>>> f = ifcopenshell.file(schema='ifc2x3')
>>> f.createIfcGroup()
#1=IfcGroup($,$,$,$,$)
>>> f.createIfcRelAssignsToGroup(RelatingGroup=f[1])
#2=IfcRelAssignsToGroup($,$,$,$,$,$,#1)
>>> f[1].IsGroupedBy
(#2=IfcRelAssignsToGroup($,$,$,$,$,$,#1),)
>>> ifcopenshell.settings.unpack_non_aggregate_inverses = True
>>> f[1].IsGroupedBy
#2=IfcRelAssignsToGroup($,$,$,$,$,$,#1)
"""

unpack_non_aggregate_inverses = False

"""
When true compare entity instances by value rather than by identity, even
when they belong to the same file. EXPRESS uses `=` for value comparison and
`:=:` for instance comparison, whereas the Python API only has `==`, which
normally means "the same instance". Example:

>>> import ifcopenshell
>>> f = ifcopenshell.file(schema='ifc2x3')
>>> f.createIfcCartesianPoint((0., 0.))
#1=IfcCartesianPoint((0.,0.))
>>> f.createIfcCartesianPoint((0., 0.))
#2=IfcCartesianPoint((0.,0.))
>>> f[1] == f[2]
False
>>> ifcopenshell.settings.compare_instances_by_value = True
>>> f[1] == f[2]
True
"""

compare_instances_by_value = False
