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

import ifcopenshell
import ifcopenshell.util.date
from datetime import datetime


class Data:
    is_loaded = False
    items = {}
    layers = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.items = {}
        cls.layers = {}

    @classmethod
    def load(cls, file):
        cls._file = file
        if not cls._file:
            return
        cls.load_layers()
        cls.is_loaded = True

    @classmethod
    def load_layers(cls):
        cls.layers = {}
        cls.items = {}
        for layer in cls._file.by_type("IfcPresentationLayerAssignment"):
            data = layer.get_info()
            if layer.AssignedItems:
                for item in layer.AssignedItems:
                    cls.items.setdefault(item.id(), []).append(layer.id())
            del data["AssignedItems"]
            cls.layers[layer.id()] = data
