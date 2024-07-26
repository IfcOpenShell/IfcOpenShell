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
