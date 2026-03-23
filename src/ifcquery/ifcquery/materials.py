# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcQuery.
#
# IfcQuery is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcQuery is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcQuery.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import ifcopenshell


def materials(model: ifcopenshell.file) -> list[dict]:
    """Return all materials and material sets from the model.

    :param model: The in-memory IFC model.
    :return: List of dicts covering IfcMaterial, IfcMaterialLayerSet,
        IfcMaterialConstituentSet, and IfcMaterialProfileSet entities.
    """
    results = []

    for m in model.by_type("IfcMaterial"):
        results.append(
            {
                "id": m.id(),
                "type": "IfcMaterial",
                "name": m.Name,
                "category": getattr(m, "Category", None),
            }
        )

    for ls in model.by_type("IfcMaterialLayerSet"):
        layers = []
        for layer in ls.MaterialLayers or []:
            layers.append(
                {
                    "name": layer.Name,
                    "thickness": layer.LayerThickness,
                    "material": layer.Material.Name if layer.Material else None,
                    "is_ventilated": layer.IsVentilated,
                }
            )
        results.append(
            {
                "id": ls.id(),
                "type": "IfcMaterialLayerSet",
                "name": ls.LayerSetName,
                "layers": layers,
            }
        )

    for cs in model.by_type("IfcMaterialConstituentSet"):
        constituents = []
        for c in cs.MaterialConstituents or []:
            constituents.append(
                {
                    "name": c.Name,
                    "material": c.Material.Name if c.Material else None,
                    "fraction": c.Fraction,
                }
            )
        results.append(
            {
                "id": cs.id(),
                "type": "IfcMaterialConstituentSet",
                "name": cs.Name,
                "constituents": constituents,
            }
        )

    for ps in model.by_type("IfcMaterialProfileSet"):
        profiles = []
        for p in ps.MaterialProfiles or []:
            profiles.append(
                {
                    "name": p.Name,
                    "material": p.Material.Name if p.Material else None,
                }
            )
        results.append(
            {
                "id": ps.id(),
                "type": "IfcMaterialProfileSet",
                "name": ps.Name,
                "profiles": profiles,
            }
        )

    return results
