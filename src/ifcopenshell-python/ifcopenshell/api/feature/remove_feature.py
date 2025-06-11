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

import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.util.element


def remove_feature(file: ifcopenshell.file, feature: ifcopenshell.entity_instance) -> None:
    """Remove a feature

    Fillings are retained as orphans. Featured elements remain. Features
    cannot exist by themselves, so not only is the relationship removed, the
    feature is also removed.

    :param feature: The IfcFeatureElement to remove.

    Example:

    .. code:: python

        # Create an orphaned opening. Note that an orphaned opening is
        # invalid, as an opening can only exist when voiding another
        # element.
        feature = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")

        # Remove it. This brings us back to a valid model.
        ifcopenshell.api.feature.remove_feature(model, feature=feature)
    """
    if feature.is_a("IfcFeatureElementSubtraction"):
        rels = feature.VoidsElements
    elif feature.is_a("IfcFeatureElementAddition"):
        rels = feature.ProjectsElements
    elif feature.is_a("IfcSurfaceFeature"):
        if file.schema == "IFC4":
            ifcopenshell.api.aggregate.unassign_object(file, products=[feature])
            rels = []
        else:
            rels = feature.ProjectsElements
    for rel in rels:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    if feature.is_a("IfcOpeningElement"):
        for rel in feature.HasFillings:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
    ifcopenshell.api.root.remove_product(file, product=feature)
