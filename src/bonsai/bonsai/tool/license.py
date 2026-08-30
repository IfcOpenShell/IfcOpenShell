# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# AI-assisted development tool was used in writing this file.

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element

import bonsai.core.tool

if TYPE_CHECKING:
    pass

PSET_NAME = "BBIM_LicenseInformation"

# Curated SPDX identifiers appropriate for construction documentation.
# Format: (identifier, label, description)
SPDX_LICENSES: list[tuple[str, str, str]] = [
    # Open content
    ("CC0-1.0", "CC0 1.0", "Public domain dedication — no rights reserved"),
    ("CC-BY-4.0", "CC BY 4.0", "Attribution required"),
    ("CC-BY-SA-4.0", "CC BY-SA 4.0", "Attribution + share-alike (copyleft)"),
    ("CC-BY-ND-4.0", "CC BY-ND 4.0", "Attribution, no derivatives"),
    ("CC-BY-NC-4.0", "CC BY-NC 4.0", "Attribution, non-commercial only"),
    ("CC-BY-NC-SA-4.0", "CC BY-NC-SA 4.0", "Attribution, non-commercial, share-alike"),
    # Data
    ("ODbL-1.0", "ODbL 1.0", "Open Database License — for data-heavy BIM content"),
    # Software / parametric content
    ("MIT", "MIT", "Permissive — suitable for parametric/procedural content"),
    ("Apache-2.0", "Apache 2.0", "Permissive with patent grant"),
    ("LGPL-2.1-or-later", "LGPL 2.1+", "Weak copyleft (IfcOpenShell's own license)"),
    # Proprietary
    ("LicenseRef-Proprietary", "Proprietary", "All rights reserved — no reuse without permission"),
    ("LicenseRef-AllRightsReserved", "All Rights Reserved", "Explicit all-rights-reserved declaration"),
]

SPDX_ENUM_ITEMS: list[tuple[str, str, str]] = [(id_, label, desc) for id_, label, desc in SPDX_LICENSES]


def _get_pset_from_element(element: ifcopenshell.entity_instance) -> Optional[dict]:
    """Return raw pset dict from this element only, no inheritance."""
    return ifcopenshell.util.element.get_pset(element, PSET_NAME, should_inherit=False)


def _walk_up(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Return ancestor chain from element up to IfcProject (inclusive)."""
    ancestors: list[ifcopenshell.entity_instance] = []
    current = element
    seen: set[int] = set()
    while current is not None and current.id() not in seen:
        seen.add(current.id())
        ancestors.append(current)
        if current.is_a("IfcProject"):
            break
        # Spatial containment
        container = ifcopenshell.util.element.get_container(current, should_get_direct=True)
        if container is not None:
            current = container
            continue
        # Aggregation (e.g. element inside assembly, storey inside building)
        aggregate = ifcopenshell.util.element.get_aggregate(current)
        if aggregate is not None:
            current = aggregate
            continue
        # Type objects may declare themselves to a project/library context
        if hasattr(current, "HasContext"):
            for rel in current.HasContext:
                current = rel.RelatingContext
                break
            else:
                break
            continue
        break
    return ancestors


class License(bonsai.core.tool.License):
    @classmethod
    def get_pset(cls, element: ifcopenshell.entity_instance) -> Optional[dict]:
        """Return BBIM_LicenseInformation pset dict if directly on this element, else None."""
        return _get_pset_from_element(element)

    @classmethod
    def get_effective_pset(
        cls, element: ifcopenshell.entity_instance
    ) -> tuple[Optional[dict], Optional[ifcopenshell.entity_instance]]:
        """Walk up the spatial/aggregation hierarchy returning (pset_dict, source_entity).

        The source entity is the element where the pset was actually found, so the
        UI can indicate whether the license was inherited.  Returns (None, None) if
        no license is found anywhere in the chain.
        """
        for ancestor in _walk_up(element):
            pset = _get_pset_from_element(ancestor)
            if pset:
                return pset, ancestor
        return None, None

    @classmethod
    def set_license(
        cls,
        file: ifcopenshell.file,
        element: ifcopenshell.entity_instance,
        spdx_id: str,
        copyright_notice: str,
        attribution_text: str = "",
        source_url: str = "",
    ) -> None:
        """Create or update BBIM_LicenseInformation on element."""
        props: dict = {"SpdxLicenseIdentifier": spdx_id, "CopyrightNotice": copyright_notice}
        if attribution_text:
            props["AttributionText"] = attribution_text
        if source_url:
            props["SourceUrl"] = source_url

        existing = cls._get_pset_entity(file, element)
        if existing:
            ifcopenshell.api.pset.edit_pset(file, pset=existing, properties=props)
        else:
            pset = ifcopenshell.api.pset.add_pset(file, product=element, name=PSET_NAME)
            ifcopenshell.api.pset.edit_pset(file, pset=pset, properties=props)

    @classmethod
    def remove_license(cls, file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> None:
        """Remove BBIM_LicenseInformation pset from element."""
        existing = cls._get_pset_entity(file, element)
        if existing:
            ifcopenshell.api.pset.remove_pset(file, product=element, pset=existing)

    @classmethod
    def _get_pset_entity(
        cls, file: ifcopenshell.file, element: ifcopenshell.entity_instance
    ) -> Optional[ifcopenshell.entity_instance]:
        """Return the actual IfcPropertySet entity, or None."""
        pset_data = _get_pset_from_element(element)
        if not pset_data:
            return None
        return file.by_id(pset_data["id"])

    @classmethod
    def inherit_library_license(
        cls,
        file: ifcopenshell.file,
        element: ifcopenshell.entity_instance,
        library: ifcopenshell.file,
        library_element: ifcopenshell.entity_instance,
    ) -> None:
        """After append_asset, stamp an inherited library license onto the element if it has none.

        Checks, in order: the library element itself, its declaring IfcProjectLibrary,
        then the library's IfcProject.  The first match found is copied to the
        imported element in the destination file.
        """
        # If the element already has an explicit tag it traveled with the asset.
        if _get_pset_from_element(element):
            return

        pset_data = cls._resolve_library_license(library, library_element)
        if not pset_data:
            return

        spdx_id = pset_data.get("SpdxLicenseIdentifier", "")
        copyright_notice = pset_data.get("CopyrightNotice", "")
        if not spdx_id and not copyright_notice:
            return

        cls.set_license(
            file,
            element,
            spdx_id=spdx_id,
            copyright_notice=copyright_notice,
            attribution_text=pset_data.get("AttributionText", "") or "",
            source_url=pset_data.get("SourceUrl", "") or "",
        )

    @classmethod
    def _resolve_library_license(
        cls, library: ifcopenshell.file, library_element: ifcopenshell.entity_instance
    ) -> Optional[dict]:
        """Walk up inside the library file to find an effective license."""
        # 1. Directly on the element (should already have traveled, but check anyway)
        pset = _get_pset_from_element(library_element)
        if pset:
            return pset

        # 2. Declaring IfcProjectLibrary context
        if hasattr(library_element, "HasContext"):
            for rel in library_element.HasContext:
                pset = _get_pset_from_element(rel.RelatingContext)
                if pset:
                    return pset

        # 3. IfcProject
        for project in library.by_type("IfcProject"):
            pset = _get_pset_from_element(project)
            if pset:
                return pset

        return None
