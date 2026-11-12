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
import ifcopenshell.api.root


def remove_structural_load(file: ifcopenshell.file, structural_load: ifcopenshell.entity_instance) -> None:
    """Removes a structural load

    The structural activities (actions and reactions) that apply the load are
    removed with it, as their AppliedLoad is mandatory.

    :param structural_load: The IfcStructuralLoad to remove.
    :return: None
    """
    for inverse in file.get_inverse(structural_load):
        if inverse.is_a("IfcStructuralActivity") and inverse.AppliedLoad == structural_load:
            ifcopenshell.api.root.remove_product(file, product=inverse)
    file.remove(structural_load)
