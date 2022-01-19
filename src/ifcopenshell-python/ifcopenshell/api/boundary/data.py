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


class Data:
    is_loaded = False
    boundaries = {}
    spaces = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.boundaries = {}
        cls.spaces = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        for boundary in cls._file.by_type("IfcRelSpaceBoundary"):
            data = boundary.get_info()
            data["RelatingSpace"] = data["RelatingSpace"].id() if data["RelatingSpace"] else None
            data["RelatedBuildingElement"] = (
                data["RelatedBuildingElement"].id() if data["RelatedBuildingElement"] else None
            )
            del data["ConnectionGeometry"]
            if cls._file.schema == "IFC2X3":
                pass
            else:
                if boundary.is_a("IfcRelSpaceBoundary1stLevel"):
                    data["ParentBoundary"] = data["ParentBoundary"].id() if data["ParentBoundary"] else None
                if boundary.is_a("IfcRelSpaceBoundary2ndLevel"):
                    data["CorrespondingBoundary"] = (
                        data["CorrespondingBoundary"].id() if data["CorrespondingBoundary"] else None
                    )
            cls.boundaries[boundary.id()] = data
            cls.spaces.setdefault(data["RelatingSpace"], []).append(boundary.id())
        cls.is_loaded = True
