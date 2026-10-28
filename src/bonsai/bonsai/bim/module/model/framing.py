# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

"""Framing systems: posts, rails, mullions, transoms and infill along a path.

The system (``BBIM_Framing.Data``) lives on the type when there is one, otherwise on
the element. Each occurrence keeps its own path and height (``BBIM_Framing.Guide``) and
its own Body, built by ``ifcopenshell.api.geometry.add_framing_representation``. Each
entry's material is the IfcMaterialConstituent named after the entry. See
``docs/dev-notes/framing-system.md``.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import bpy
import gpu
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.style
import ifcopenshell.util.element
import ifcopenshell.util.framing
import ifcopenshell.util.representation
import ifcopenshell.util.schema
import ifcopenshell.util.system
import ifcopenshell.util.type
import ifcopenshell.util.unit
import numpy as np
from gpu_extras.batch import batch_for_shader
from ifcopenshell.api.geometry.add_framing_representation import (
    compute_framing_geometry,
    compute_framing_mesh,
    get_framing_voids,
    get_profile_mesh,
)
from ifcopenshell.util.framing import FramingError
from mathutils import Matrix, Vector

import bonsai.core.geometry
import bonsai.core.root
import bonsai.core.style
import bonsai.core.type
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.data import FramingData, refresh
from bonsai.bim.module.model.decorator import PolylineDecorator, ProductDecorator, ProfileDecorator
from bonsai.bim.module.model.polyline import PolylineOperator
from bonsai.bim.module.model.railing import get_path_data

# Last regeneration error per element id, shown in the panel.
_errors: dict[int, str] = {}
# Last live-preview error per element id, shown while editing.
_preview_errors: dict[int, str] = {}
# Tessellated profiles for the live preview. Any IFC commit invalidates them.
_profile_meshes = tool.Parametric.GenerationKeyedCache()
# The element's openings on its guide, for the live preview, likewise.
_preview_voids = tool.Parametric.GenerationKeyedCache()
# Set while the panel's properties are filled from IFC, so that does not preview on every field.
_is_loading_props = False


# Parametric tools that already build an element's body, by their tool.Parametric predicate.
_OTHER_GENERATORS = (
    ("door", "Door"),
    ("window", "Window"),
    ("stair", "Stair"),
    ("railing", "Railing"),
    ("roof", "Roof"),
    ("array", "Array"),
)


def is_framing_class(ifc_class: str) -> bool:
    """Whether elements of this class can be framed at all: any element or element type,
    apart from feature and virtual elements, which have no body of their own to build."""
    try:
        declaration = tool.Ifc.schema().declaration_by_name(ifc_class)
    except Exception:
        return False
    is_a = ifcopenshell.util.schema.is_a
    if not (is_a(declaration, "IfcElement") or is_a(declaration, "IfcElementType")):
        return False
    return not any(is_a(declaration, c) for c in ("IfcFeatureElement", "IfcVirtualElement"))


def is_framing_host(element: Optional[ifcopenshell.entity_instance]) -> bool:
    return element is not None and is_framing_class(element.is_a())


def framing_refusal(element: Optional[ifcopenshell.entity_instance]) -> Optional[str]:
    """Why framing cannot be added to an element, or None if it can.

    Framing is open to any element, except where something else already owns the body."""
    if not is_framing_host(element):
        return "Only elements and element types can be framed, not openings or virtual elements."
    for name, label in _OTHER_GENERATORS:
        if getattr(tool.Parametric, f"is_{name}")(element):
            return f"This element is driven by the {label} tool. Remove its parameters first."
    if ifcopenshell.util.element.get_pset(element, "BBIM_Array"):
        return "This element is part of an array, which builds its copies itself."
    element_type = None if element.is_a("IfcTypeObject") else ifcopenshell.util.element.get_type(element)
    for product in filter(None, (element, element_type)):
        if tool.Model.get_usage_type(product):
            return "This element is built from its layered or profiled material."
    if element_type and element_type.RepresentationMaps:
        return "This element's type shares its geometry. Use a type without geometry."
    if not element.is_a("IfcTypeObject"):
        if ifcopenshell.util.system.get_ports(element):
            return "Elements with distribution ports cannot be framed."
        if element.is_a("IfcElementAssembly") and element.IsDecomposedBy:
            return "This assembly already has parts."
    return None


def get_system_owner(element: Optional[ifcopenshell.entity_instance]) -> Optional[ifcopenshell.entity_instance]:
    """The type or element whose ``BBIM_Framing.Data`` holds the system.

    An occurrence's own system overrides its type's, as property inheritance does."""
    if element is None:
        return None
    if ifcopenshell.util.element.get_pset(element, "BBIM_Framing", "Data", should_inherit=False):
        return element
    if not element.is_a("IfcTypeObject") and (element_type := ifcopenshell.util.element.get_type(element)):
        if ifcopenshell.util.element.get_pset(element_type, "BBIM_Framing", "Data"):
            return element_type
    return None


def get_framing_error(element: Optional[ifcopenshell.entity_instance]) -> Optional[str]:
    return _errors.get(element.id()) if element else None


def get_preview_error(element: Optional[ifcopenshell.entity_instance]) -> Optional[str]:
    return _preview_errors.get(element.id()) if element else None


def _entry_blender_material(entry) -> Optional[bpy.types.Material]:
    if not entry.material or entry.material == "0":
        return None
    ifc_file = tool.Ifc.get()
    material = ifc_file.by_id(int(entry.material))
    body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    for context in (body, getattr(body, "ParentContext", None)):
        if context and (style := ifcopenshell.util.representation.get_material_style(material, context)):
            if isinstance(blender_material := tool.Ifc.get_object(style), bpy.types.Material):
                return blender_material
    return None


def update_framing_preview(obj: bpy.types.Object) -> None:
    """Show the framing being edited on the object's mesh, without writing any IFC.

    Finish writes the real body; Cancel restores it. If the edit is not valid yet, the
    last good preview stays and the error is shown in the panel."""
    if _is_loading_props or not obj or not isinstance(obj.data, bpy.types.Mesh):
        return
    props = tool.Model.get_framing_props(obj)
    element = tool.Ifc.get_entity(obj)
    if not props.is_editing or not element or element.is_a("IfcTypeObject"):
        return
    ifc_file = tool.Ifc.get()
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    try:
        system = system_from_props(props, read_system(element))
        profile_meshes = {}
        for member in system["members"]:
            if member["kind"] not in ("V", "H"):
                continue
            profile = ifcopenshell.util.framing.resolve_profile(ifc_file, member.get("profile"))
            if profile is None:
                raise FramingError(f"Entry {member['name']!r} needs a profile.")
            profile_meshes[member["name"]] = _profile_meshes.get_or_compute(
                profile.id(), lambda profile=profile: get_profile_mesh(profile, unit_scale)
            )
        guide = read_guide(element) or default_guide(props.height / unit_scale, unit_scale)
        closed = guide.get("closed", False)
        items = compute_framing_geometry(
            system=system,
            guide=guide["verts"],
            height=props.height / unit_scale,
            profile_points={name: points for name, (points, _) in profile_meshes.items()},
            closed=closed,
            scope=props.scope,
            voids=_preview_voids.get_or_compute(
                (element.id(), str(guide)), lambda: get_framing_voids(element, guide["verts"], closed, unit_scale)
            ),
        )
        mesh = compute_framing_mesh(items, profile_meshes)
    except FramingError as e:
        _preview_errors[element.id()] = str(e)
        tool.Blender.update_viewport()
        return
    _preview_errors.pop(element.id(), None)

    materials: list[Optional[bpy.types.Material]] = []
    slot_by_entry: dict[str, int] = {}
    for entry in props.entries:
        material = _entry_blender_material(entry)
        if material not in materials:
            materials.append(material)
        slot_by_entry[entry.name.strip()] = materials.index(material)

    bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)
    verts = [bm.verts.new(Vector(v)) for v in (mesh.vertices * unit_scale).tolist()]
    for face, entry in zip(mesh.faces, mesh.face_entries):
        try:
            bm_face = bm.faces.new([verts[i] for i in face])
        except ValueError:  # A degenerate face, e.g. from a zero-thickness profile.
            continue
        bm_face.material_index = slot_by_entry.get(entry, 0)
    tool.Blender.apply_bmesh(obj.data, bm)
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)


def read_system(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    return json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Framing", "Data") or "{}")


def read_guide(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    return json.loads(
        ifcopenshell.util.element.get_pset(element, "BBIM_Framing", "Guide", should_inherit=False) or "{}"
    )


def get_own_framing_pset(product: ifcopenshell.entity_instance) -> Optional[ifcopenshell.entity_instance]:
    """The product's own BBIM_Framing pset, never its type's.

    ``tool.Pset.get_element_pset`` inherits, so for an occurrence without a pset of its
    own it returns the type's, and writing to that would change every occurrence."""
    pset = ifcopenshell.util.element.get_pset(product, "BBIM_Framing", should_inherit=False)
    return tool.Ifc.get().by_id(pset["id"]) if pset else None


def write_framing_pset(product: ifcopenshell.entity_instance, **properties: Optional[dict[str, Any]]) -> None:
    """Write ``Data`` / ``Guide`` as JSON on the product itself. ``None`` removes the property."""
    ifc_file = tool.Ifc.get()
    if product.is_a("IfcTypeObject"):
        # Paths belong to occurrences. Drop any a type picked up, as earlier versions
        # could write an occurrence's path to its type.
        properties.setdefault("Guide", None)
    pset = get_own_framing_pset(product)
    if not pset:
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=product, name="BBIM_Framing")
    values = {k: None if v is None else ifc_file.createIfcText(json.dumps(v)) for k, v in properties.items()}
    ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties=values)


def get_constituent_set(product: ifcopenshell.entity_instance) -> Optional[ifcopenshell.entity_instance]:
    material = ifcopenshell.util.element.get_material(product, should_skip_usage=True)
    return material if material and material.is_a("IfcMaterialConstituentSet") else None


def default_guide(height: float, unit_scale: float) -> dict[str, Any]:
    return {"verts": [[0.0, 0.0, 0.0], [3.0 / unit_scale, 0.0, 0.0]], "closed": False, "height": height}


def update_profile_references(system: dict[str, Any]) -> bool:
    """Point each entry's profile reference at the profile it resolves to. Returns whether any changed."""
    changed = False
    for member in system.get("members", []):
        reference = member.get("profile")
        profile = ifcopenshell.util.framing.resolve_profile(tool.Ifc.get(), reference)
        if profile and reference != (resolved := {"id": profile.id(), "name": profile.ProfileName}):
            member["profile"] = resolved
            changed = True
    return changed


def get_occurrence_height(element: ifcopenshell.entity_instance) -> float:
    """An occurrence's own height in SI units: its path's, else its system's default."""
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    default = read_system(element).get("default_height", 1.1 / unit_scale)
    return read_guide(element).get("height", default) * unit_scale


def is_framed_occurrence(obj: Optional[bpy.types.Object]) -> bool:
    element = tool.Ifc.get_entity(obj) if obj else None
    return bool(element and not element.is_a("IfcTypeObject") and get_system_owner(element))


def set_framing_height(obj: bpy.types.Object, height: float) -> bool:
    """Give one framed occurrence a new height (SI units) and rebuild only it."""
    element = tool.Ifc.get_entity(obj)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    guide = read_guide(element) or default_guide(height / unit_scale, unit_scale)
    guide["height"] = height / unit_scale
    write_framing_pset(element, Guide=guide)
    return regenerate_framing(obj)


def extend_framing_to_z(objs: list[bpy.types.Object], z: float, report) -> list[bpy.types.Object]:
    """Ctrl+E: raise each framed occurrence's top to ``z``. Returns the framed objects handled.

    Each occurrence's height is measured from where its path starts, so occurrences on
    different levels each reach ``z``. Those starting at or above ``z`` are skipped."""
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    framed = [o for o in objs if is_framed_occurrence(o)]
    extended, skipped, errors = 0, 0, []
    for obj in framed:
        element = tool.Ifc.get_entity(obj)
        verts = read_guide(element).get("verts") or [[0.0, 0.0, 0.0]]
        base = (obj.matrix_world @ (Vector(verts[0]) * unit_scale)).z
        if z - base <= 1e-5:
            skipped += 1
        elif set_framing_height(obj, z - base):
            extended += 1
        else:
            errors.append(f"{element.Name or element.is_a()}: {get_framing_error(element)}")
    if extended:
        report({"INFO"}, f"Extended {extended} framing object(s) to z: {z:.2f}m")
    if skipped:
        report({"WARNING"}, f"Skipped {skipped} framing object(s) starting at or above the cursor ({z:.2f}m).")
    for error in errors:
        report({"WARNING"}, error)
    if framed:
        refresh()
    return framed


def regenerate_framing(obj: bpy.types.Object) -> bool:
    """Rebuild an occurrence's Body from its system and its own guide. Returns False on failure."""
    element = tool.Ifc.get_entity(obj)
    if not element or element.is_a("IfcTypeObject"):
        return False
    if not isinstance(obj.data, bpy.types.Mesh):
        _errors[element.id()] = "The object has no mesh to show the framing on."
        return False
    ifc_file = tool.Ifc.get()
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    owner = get_system_owner(element)
    if owner is None:
        _errors[element.id()] = "No framing system found."
        return False
    system = read_system(element)
    if update_profile_references(system):
        write_framing_pset(owner, Data=system)
    guide = read_guide(element)
    if not guide.get("verts"):
        guide = default_guide(system.get("default_height", 1.1 / unit_scale), unit_scale)
        write_framing_pset(element, Guide=guide)

    body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    if not element.Representation:
        element.Representation = ifc_file.createIfcProductDefinitionShape(None, None, ())
    try:
        voids = get_framing_voids(element, guide["verts"], guide.get("closed", False), unit_scale)
        representation = ifcopenshell.api.geometry.add_framing_representation(
            ifc_file,
            context=body,
            system=system,
            guide=guide["verts"],
            height=guide.get("height", system.get("default_height", 1.1 / unit_scale)),
            closed=guide.get("closed", False),
            scope=system.get("scope", "SEGMENT"),
            part_of_product=element.Representation,
            constituent_set=get_constituent_set(element),
            unit_scale=unit_scale,
            voids=voids,
        )
    except FramingError as e:
        _errors[element.id()] = str(e)
        return False
    _errors.pop(element.id(), None)
    tool.Model.replace_object_ifc_representation(body, obj, representation)
    return True


def regenerate_framing_host(obj: bpy.types.Object) -> bool:
    """Lay a framing occurrence out again around its openings, after they changed.

    Returns False if ``obj`` is not a framing occurrence or its framing failed, so the
    caller recuts it as usual instead."""
    element = tool.Ifc.get_entity(obj)
    if element is None or element.is_a("IfcTypeObject") or get_system_owner(element) is None:
        return False
    if tool.Model.get_framing_props(obj).is_editing:
        # Finish writes the body; until then the preview shows the new openings.
        update_framing_preview(obj)
        return True
    return regenerate_framing(obj)


def apply_framing_type(obj: bpy.types.Object) -> bool:
    """After a framing type is assigned: use the type's system, keeping this occurrence's path.

    Like a wall taking its type's layer set, the occurrence drops a system and material
    set of its own, which would otherwise override the type's."""
    element = tool.Ifc.get_entity(obj)
    if not element or element.is_a("IfcTypeObject"):
        return False
    if ifcopenshell.util.element.get_pset(element, "BBIM_Framing", "Data", should_inherit=False):
        write_framing_pset(element, Data=None)
    if ifcopenshell.util.element.get_material(element, should_inherit=False):
        ifcopenshell.api.material.unassign_material(tool.Ifc.get(), products=[element])
    return regenerate_framing(obj)


def regenerate_system_users(owner: ifcopenshell.entity_instance) -> list[str]:
    """Regenerate every occurrence that uses the owner's system. Returns error messages.

    Occurrences of a type that have no framing path of their own yet are left alone, so
    framing a type does not replace geometry its other occurrences already have."""
    elements = ifcopenshell.util.element.get_types(owner) if owner.is_a("IfcTypeObject") else [owner]
    errors = []
    for element in elements:
        if get_system_owner(element) != owner or not read_guide(element):
            continue
        if (obj := tool.Ifc.get_object(element)) and not regenerate_framing(obj):
            errors.append(f"{element.Name or element.is_a()}: {_errors.get(element.id())}")
    return errors


def sync_constituents(
    owner: ifcopenshell.entity_instance, materials: dict[str, Optional[ifcopenshell.entity_instance]]
):
    """Make the owner's constituents match its entries: one per entry that has a material."""
    ifc_file = tool.Ifc.get()
    constituent_set = get_constituent_set(owner)
    if constituent_set is None:
        if not any(materials.values()):
            return
        constituent_set = ifcopenshell.api.material.add_material_set(
            ifc_file, name=f"{owner.Name or 'Framing'} Framing", set_type="IfcMaterialConstituentSet"
        )
        ifcopenshell.api.material.assign_material(ifc_file, products=[owner], material=constituent_set)
    existing = {c.Name: c for c in constituent_set.MaterialConstituents or []}
    for name, constituent in existing.items():
        if not materials.get(name):
            ifcopenshell.api.material.remove_constituent(ifc_file, constituent=constituent)
    for name, material in materials.items():
        if not material:
            continue
        if constituent := existing.get(name):
            constituent.Material = material
        else:
            constituent = ifcopenshell.api.material.add_constituent(
                ifc_file, constituent_set=constituent_set, material=material
            )
            constituent.Name = name


def ensure_profile(name: str, x: float, y: float) -> ifcopenshell.entity_instance:
    """A rectangle profile by name, created in project units if missing. Sizes are in metres."""
    ifc_file = tool.Ifc.get()
    if profile := next((p for p in ifc_file.by_type("IfcProfileDef") if p.ProfileName == name), None):
        return profile
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    return ifc_file.createIfcRectangleProfileDef("AREA", name, None, x / unit_scale, y / unit_scale)


def ensure_material(
    name: str, category: str, colour: tuple[float, float, float, float]
) -> ifcopenshell.entity_instance:
    """A material by name, created with a coloured Body style if missing."""
    ifc_file = tool.Ifc.get()
    if material := next((m for m in ifc_file.by_type("IfcMaterial") if m.Name == name), None):
        return material
    material = ifcopenshell.api.material.add_material(ifc_file, name=name, category=category)
    blender_material = bpy.data.materials.new(name)
    blender_material.diffuse_color = colour
    style = bonsai.core.style.add_style(tool.Ifc, tool.Style, obj=blender_material)
    body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    ifcopenshell.api.style.assign_material_style(ifc_file, material=material, style=style, context=body)
    return material


def default_preset(element: ifcopenshell.entity_instance) -> str:
    """The system an element starts with: a storefront for walls, else a railing.

    Only a starting point; the entries are then edited freely."""
    walls = ("IfcCurtainWall", "IfcCurtainWallType", "IfcWall", "IfcWallType")
    return "STOREFRONT" if any(element.is_a(c) for c in walls) else "RAILING"


def preset_system(preset: str) -> tuple[dict[str, Any], dict[str, ifcopenshell.entity_instance]]:
    """A starting system in project units, and the material for each entry."""
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    def m(metres: float) -> float:
        return metres / unit_scale

    def ref(profile: ifcopenshell.entity_instance) -> dict[str, Any]:
        return {"id": profile.id(), "name": profile.ProfileName}

    glass = ensure_material("Glass", "glass", (0.6, 0.8, 0.9, 0.3))
    if preset == "STOREFRONT":
        aluminium = ensure_material("Aluminium", "aluminium", (0.7, 0.7, 0.72, 1.0))
        # One profile for all frame members: X along the path, Y out of plane for the
        # mullions, and turned 90 degrees for the horizontals.
        frame = ensure_profile("Storefront Frame 45x115", 0.045, 0.115)
        horizontal = {"kind": "H", "breaks_at": ["Mullion"], "rotation": 90, "profile": ref(frame)}
        system = {
            "default_height": m(3.0),
            "members": [
                {
                    "name": "Mullion",
                    "kind": "V",
                    "spacing": {"mode": "MAX", "value": m(1.5)},
                    "at_ends": True,
                    "at_corners": True,
                    "profile": ref(frame),
                },
                {"name": "Sill", "v": "BASE", **horizontal},
                {"name": "Transom", "v": m(2.4), **horizontal},
                {"name": "Head", "v": "TOP", **horizontal},
                {
                    "name": "Vision",
                    "kind": "INFILL",
                    "between": "Mullion",
                    "bottom": {"member": "Sill"},
                    "top": {"member": "Transom"},
                    "thickness": m(0.025),
                    "gap": m(0.006),
                },
                {
                    "name": "Clerestory",
                    "kind": "INFILL",
                    "between": "Mullion",
                    "bottom": {"member": "Transom"},
                    "top": {"member": "Head"},
                    "thickness": m(0.025),
                    "gap": m(0.006),
                },
            ],
        }
        materials = {"Mullion": aluminium, "Sill": aluminium, "Transom": aluminium, "Head": aluminium}
        return system, materials | {"Vision": glass, "Clerestory": glass}

    steel = ensure_material("Steel", "steel", (0.25, 0.25, 0.27, 1.0))
    post = ensure_profile("Railing Post 50x50", 0.05, 0.05)
    cap = ensure_profile("Railing Cap 60x20", 0.06, 0.02)
    rail = ensure_profile("Railing Rail 40x40", 0.04, 0.04)
    system = {
        "default_height": m(1.1),
        "members": [
            {
                "name": "Post",
                "kind": "V",
                "spacing": {"mode": "MAX", "value": m(1.5)},
                "at_ends": True,
                "at_corners": True,
                "top": {"member": "TopRail"},
                "profile": ref(post),
            },
            {"name": "TopRail", "kind": "H", "v": m(1.07), "profile": ref(cap)},
            {"name": "BottomRail", "kind": "H", "v": m(0.1), "breaks_at": ["Post"], "profile": ref(rail)},
            {
                "name": "Glass",
                "kind": "INFILL",
                "between": "Post",
                "bottom": {"member": "BottomRail"},
                "top": {"member": "TopRail"},
                "thickness": m(0.012),
                "gap": m(0.02),
            },
        ],
    }
    return system, {"Post": steel, "TopRail": steel, "BottomRail": steel, "Glass": glass}


def _bound_to_props(entry, prefix: str, bound: Any, unit_scale: float) -> None:
    if bound in ("BASE", "TOP"):
        setattr(entry, f"{prefix}_type", bound)
    elif isinstance(bound, dict):
        setattr(entry, f"{prefix}_type", "MEMBER")
        setattr(entry, f"{prefix}_member", bound.get("member", ""))
    elif isinstance(bound, (int, float)):
        setattr(entry, f"{prefix}_type", "HEIGHT")
        setattr(entry, prefix, bound * unit_scale)


def _bound_from_props(entry, prefix: str, unit_scale: float) -> Any:
    bound_type = getattr(entry, f"{prefix}_type")
    if bound_type in ("BASE", "TOP"):
        return bound_type
    if bound_type == "MEMBER":
        return {"member": getattr(entry, f"{prefix}_member")}
    return getattr(entry, prefix) / unit_scale


def load_props(obj: bpy.types.Object) -> None:
    """Fill the panel's properties from the element's system and guide (SI units in Blender)."""
    global _is_loading_props
    _is_loading_props = True
    try:
        _load_props(obj)
    finally:
        _is_loading_props = False


def _load_props(obj: bpy.types.Object) -> None:
    element = tool.Ifc.get_entity(obj)
    props = tool.Model.get_framing_props(obj)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    system = read_system(element)
    owner = get_system_owner(element)
    constituents = {}
    if owner and (constituent_set := get_constituent_set(owner)):
        constituents = {c.Name: c.Material for c in constituent_set.MaterialConstituents or []}
    profile_ids = {item[0] for item in FramingData.data.get("profiles", [])} if FramingData.is_loaded else set()

    props.entries.clear()
    for member in system.get("members", []):
        entry = props.entries.add()
        entry.name = member.get("name", "")
        entry.kind = member.get("kind", "V")
        if spacing := member.get("spacing"):
            entry.spacing_mode = spacing["mode"]
            if spacing["mode"] == "COUNT":
                entry.count = int(spacing["value"])
            else:
                entry.spacing = spacing["value"] * unit_scale
            if spacing["mode"] == "MAX":
                entry.max_align = spacing.get("align", "EVEN")
            else:
                entry.spacing_align = spacing.get("align", "CENTER")
            entry.spacing_offset = spacing.get("offset", 0.0) * unit_scale
            entry.equal_openings = spacing.get("openings", False)
        entry.at_ends = member.get("at_ends", False)
        entry.at_corners = member.get("at_corners", False)
        entry.butt_corners = member.get("butt_corners", False)
        entry.corner_joint = member.get("corner_joint", "MITRE")
        entry.square_cut = member.get("square_cut", False)
        entry.flush = member.get("flush", False)
        entry.extend_start = member.get("extend_start", 0.0) * unit_scale
        entry.extend_end = member.get("extend_end", 0.0) * unit_scale
        within = member.get("within") or []
        within = [within] if isinstance(within, str) else within
        entry.within = within[0] if within else ""
        entry.within_also.clear()
        for name in within[1:]:
            entry.within_also.add().name = name
        if "v" in member:
            _bound_to_props(entry, "level", member["v"], unit_scale)
        entry.level_offset = member.get("level_offset", 0.0) * unit_scale
        _bound_to_props(entry, "bottom", member.get("bottom", "BASE"), unit_scale)
        _bound_to_props(entry, "top", member.get("top", "TOP"), unit_scale)
        entry.breaks_at.clear()
        for name in member.get("breaks_at", []):
            entry.breaks_at.add().name = name
        entry.between = member.get("between") or ""
        entry.bays = ", ".join(str(i) for i in member.get("bays", []))
        entry.rows = ", ".join(str(i) for i in member.get("rows", []))
        entry.thickness = member.get("thickness", 0.012 / unit_scale) * unit_scale
        gap = member.get("gap", 0.0)
        entry.gap = (gap if isinstance(gap, (int, float)) else gap.get("left", 0.0)) * unit_scale
        entry.max_width = (member.get("max_width") or 0.0) * unit_scale
        entry.joint = member.get("joint", 0.0) * unit_scale
        entry.rotation = member.get("rotation", 0.0)
        entry.offset = member.get("offset", 0.0) * unit_scale
        # The older single key sets both.
        both = member.get("cut_by_voids", True)
        entry.cut_by_edge_voids = member.get("cut_by_edge_voids", both)
        entry.cut_by_hole_voids = member.get("cut_by_hole_voids", both)
        entry.void_role = member.get("void_role") or "NONE"
        entry.void_layer = member.get("void_layer", 1)
        entry.jamb_height = member.get("jamb_height", "FULL")
        void_for = member.get("void_for") or []
        void_for = [void_for] if isinstance(void_for, str) else void_for
        entry.void_for = {c for c in void_for if c in ("IfcDoor", "IfcWindow", "IfcOpeningElement")}
        if (profile := member.get("profile")) and str(profile.get("id")) in profile_ids:
            entry.profile = str(profile["id"])
        if material := constituents.get(entry.name):
            entry.material = str(material.id())

    guide = read_guide(element) if not element.is_a("IfcTypeObject") else {}
    props.height = guide.get("height", system.get("default_height", 1.1 / unit_scale)) * unit_scale
    props.scope = system.get("scope", "SEGMENT")
    props.active_entry_index = min(props.active_entry_index, max(len(props.entries) - 1, 0))


def system_from_props(props, previous: dict[str, Any]) -> dict[str, Any]:
    """Build the system JSON (project units) from the panel's properties, and validate it."""
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    ifc_file = tool.Ifc.get()
    members = []
    for entry in props.entries:
        member: dict[str, Any] = {"name": entry.name.strip(), "kind": entry.kind}
        if entry.kind in ("V", "H") and entry.spacing_mode != "NONE":
            value = entry.count if entry.spacing_mode == "COUNT" else entry.spacing / unit_scale
            member["spacing"] = {"mode": entry.spacing_mode, "value": value}
            if entry.spacing_mode == "FIXED" and entry.spacing_align != "CENTER":
                member["spacing"]["align"] = entry.spacing_align
            elif entry.spacing_mode == "MAX" and entry.max_align != "EVEN":
                member["spacing"]["align"] = entry.max_align
            has_anchor = entry.spacing_mode == "FIXED" or (entry.spacing_mode == "MAX" and entry.max_align != "EVEN")
            if has_anchor and entry.spacing_offset:
                member["spacing"]["offset"] = entry.spacing_offset / unit_scale
            if entry.equal_openings and (
                entry.spacing_mode == "COUNT" or (entry.spacing_mode == "MAX" and entry.max_align == "EVEN")
            ):
                member["spacing"]["openings"] = True
        if entry.kind == "V":
            member["at_ends"] = entry.at_ends
            member["at_corners"] = entry.at_corners
            if entry.at_corners and entry.butt_corners:
                member["butt_corners"] = True
            if entry.square_cut:
                member["square_cut"] = True
        if entry.flush and entry.kind in ("V", "H"):
            member["flush"] = True
        repeats = entry.kind == "INFILL" or entry.spacing_mode != "NONE"
        within = [entry.within.strip()]
        if entry.kind == "V":
            within += [w.name.strip() for w in entry.within_also]
        within = list(dict.fromkeys(w for w in within if w))
        if within and repeats:
            member["within"] = within[0] if len(within) == 1 else within
        if entry.between and entry.kind in ("H", "INFILL"):
            member["between"] = entry.between
        if bays := _selection_from_props(entry, "bays"):
            member["bays"] = bays
        if (rows := _selection_from_props(entry, "rows")) and entry.kind in ("H", "INFILL") and repeats:
            member["rows"] = rows
        if entry.kind == "H" and entry.spacing_mode == "NONE":
            member["v"] = _bound_from_props(entry, "level", unit_scale)
            if entry.level_offset and entry.level_type != "HEIGHT":
                member["level_offset"] = entry.level_offset / unit_scale
        else:
            member["bottom"] = _bound_from_props(entry, "bottom", unit_scale)
            member["top"] = _bound_from_props(entry, "top", unit_scale)
        if entry.kind == "H":
            if entry.corner_joint != "MITRE":
                member["corner_joint"] = entry.corner_joint
            if entry.extend_start:
                member["extend_start"] = entry.extend_start / unit_scale
            if entry.extend_end:
                member["extend_end"] = entry.extend_end / unit_scale
        if breaks := [b.name.strip() for b in entry.breaks_at if b.name.strip()]:
            member["breaks_at"] = breaks
        if entry.kind == "INFILL":
            member["thickness"] = entry.thickness / unit_scale
            member["gap"] = entry.gap / unit_scale
            if entry.max_width > 0:
                member["max_width"] = entry.max_width / unit_scale
                member["joint"] = entry.joint / unit_scale
        else:
            if entry.profile and entry.profile != "0":
                profile = ifc_file.by_id(int(entry.profile))
                member["profile"] = {"id": profile.id(), "name": profile.ProfileName}
            if entry.rotation:
                member["rotation"] = entry.rotation
        if entry.offset:
            member["offset"] = entry.offset / unit_scale
        if not entry.cut_by_edge_voids:
            member["cut_by_edge_voids"] = False
        if not entry.cut_by_hole_voids:
            member["cut_by_hole_voids"] = False
        if (entry.kind, entry.void_role) in (("V", "JAMB"), ("H", "HEAD"), ("H", "SILL")):
            _void_role_from_props(member, entry)
        members.append(member)
    system = {k: v for k, v in previous.items() if k not in ("members", "scope")}
    system["scope"] = props.scope
    system["members"] = members
    ifcopenshell.util.framing.parse_system(system)
    return system


def _void_role_from_props(member: dict[str, Any], entry) -> None:
    """An entry that frames openings has no layout of its own, so drop the keys for one."""
    layout_keys = [
        "spacing",
        "at_ends",
        "at_corners",
        "butt_corners",
        "within",
        "bays",
        "rows",
        "between",
        "v",
        "flush",
    ]
    layout_keys += [
        "corner_joint",
        "square_cut",
        "extend_start",
        "extend_end",
        "cut_by_edge_voids",
        "cut_by_hole_voids",
        "level_offset",
    ]
    if entry.kind == "H":
        # A head or sill is placed by its opening, so it has no bounds or breaks either.
        layout_keys += ["bottom", "top", "breaks_at"]
    for key in layout_keys:
        member.pop(key, None)
    member["void_role"] = entry.void_role
    member["void_layer"] = entry.void_layer
    if entry.kind == "V":
        member["jamb_height"] = entry.jamb_height
    if entry.void_for:
        member["void_for"] = sorted(entry.void_for)


def _selection_from_props(entry, prop_name: str) -> list[int]:
    text = getattr(entry, prop_name).strip()
    if not text:
        return []
    try:
        selection = [int(part) for part in text.replace(";", ",").split(",") if part.strip()]
    except ValueError:
        raise FramingError(f"Entry {entry.name!r}: {prop_name} must be whole numbers, like '1, -1'.")
    if 0 in selection:
        raise FramingError(f"Entry {entry.name!r}: {prop_name} count from 1, or from -1 at the end.")
    return selection


def materials_from_props(props) -> dict[str, Optional[ifcopenshell.entity_instance]]:
    ifc_file = tool.Ifc.get()
    return {
        e.name.strip(): ifc_file.by_id(int(e.material)) if e.material and e.material != "0" else None
        for e in props.entries
    }


class AddFraming(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_framing"
    bl_label = "Add Framing"
    bl_description = "Build this element from a framing system of posts, rails, mullions and infill"
    bl_options = {"REGISTER", "UNDO"}
    preset: bpy.props.EnumProperty(
        name="Starting System",
        items=[
            ("AUTO", "Automatic", "Storefront for curtain walls and walls, otherwise railing"),
            ("RAILING", "Railing", "Posts, a top rail, a bottom rail and glass"),
            ("STOREFRONT", "Storefront", "Mullions, sill, transom, head and glazing"),
        ],
        default="AUTO",
        options={"SKIP_SAVE"},
    )

    @classmethod
    def poll(cls, context):
        element = tool.Ifc.get_entity(context.active_object) if context.active_object else None
        if tool.Parametric.is_framing(element):
            cls.poll_message_set("This element already has framing.")
            return False
        if reason := framing_refusal(element):
            cls.poll_message_set(reason)
            return False
        return True

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        element_type = None if element.is_a("IfcTypeObject") else ifcopenshell.util.element.get_type(element)
        if element_type and tool.Parametric.is_framing(element_type):
            # The type already has a system: this occurrence only needs its own path.
            height = read_system(element_type).get("default_height", 1.1 / unit_scale)
            write_framing_pset(element, Guide=default_guide(height, unit_scale))
            if not regenerate_framing(obj):
                self.report({"WARNING"}, get_framing_error(element) or "Framing failed.")
            refresh()
            return {"FINISHED"}
        system, materials = preset_system(self.preset if self.preset != "AUTO" else default_preset(element))
        owner = element_type or element
        update_profile_references(system)
        write_framing_pset(owner, Data=system)
        sync_constituents(owner, materials)
        if not element.is_a("IfcTypeObject"):
            write_framing_pset(element, Guide=default_guide(system["default_height"], unit_scale))
        errors = regenerate_system_users(owner)
        refresh()
        for error in errors:
            self.report({"WARNING"}, error)
        return {"FINISHED"}


class EnableEditingFraming(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_framing"
    bl_label = "Edit Framing"
    bl_description = "Edit the framing system"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        FramingData.load()
        load_props(obj)
        tool.Model.get_framing_props(obj).is_editing = True
        return {"FINISHED"}


class FinishEditingFraming(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_framing"
    bl_label = "Finish Editing Framing"
    bl_description = "Save the framing system and rebuild every element that uses it"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_framing_props(obj)
        owner = get_system_owner(element) or element
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        try:
            system = system_from_props(props, read_system(element))
        except FramingError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        if element.is_a("IfcTypeObject"):
            # On a type, the height is what new occurrences start with.
            system["default_height"] = props.height / unit_scale
        write_framing_pset(owner, Data=system)
        sync_constituents(owner, materials_from_props(props))
        if not element.is_a("IfcTypeObject"):
            guide = read_guide(element) or default_guide(props.height / unit_scale, unit_scale)
            guide["height"] = props.height / unit_scale
            write_framing_pset(element, Guide=guide)
        props.is_editing = False
        errors = regenerate_system_users(owner)
        refresh()
        for error in errors:
            self.report({"WARNING"}, error)
        return {"FINISHED"}


class CancelEditingFraming(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_framing"
    bl_label = "Cancel Editing Framing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        tool.Model.get_framing_props(obj).is_editing = False
        element = tool.Ifc.get_entity(obj)
        _preview_errors.pop(element.id(), None)
        if isinstance(obj.data, bpy.types.Mesh) and (
            body := ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        ):
            bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=body)
        return {"FINISHED"}


class AddFramingEntry(bpy.types.Operator):
    bl_idname = "bim.add_framing_entry"
    bl_label = "Add Framing Entry"
    bl_options = {"REGISTER", "UNDO"}
    kind: bpy.props.EnumProperty(items=[("V", "Vertical", ""), ("H", "Horizontal", ""), ("INFILL", "Infill", "")])

    def execute(self, context):
        global _is_loading_props
        obj = context.active_object
        props = tool.Model.get_framing_props(obj)
        names = {e.name for e in props.entries}
        base = {"V": "Vertical", "H": "Horizontal", "INFILL": "Infill"}[self.kind]
        name, i = base, 1
        while name in names:
            i += 1
            name = f"{base}{i}"
        _is_loading_props = True
        try:
            entry = props.entries.add()
            entry.name = name
            entry.kind = self.kind
            if self.kind == "V":
                entry.at_ends = True
        finally:
            _is_loading_props = False
        props.active_entry_index = len(props.entries) - 1
        update_framing_preview(obj)
        return {"FINISHED"}


class DuplicateFramingEntry(bpy.types.Operator):
    bl_idname = "bim.duplicate_framing_entry"
    bl_label = "Duplicate Framing Entry"
    bl_description = "Copy the active entry, with all its settings, below it"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global _is_loading_props
        obj = context.active_object
        props = tool.Model.get_framing_props(obj)
        index = props.active_entry_index
        if not 0 <= index < len(props.entries):
            return {"CANCELLED"}
        names = {e.name for e in props.entries}
        base = props.entries[index].name.rstrip("0123456789") or props.entries[index].name
        name, i = f"{base}2", 2
        while name in names:
            i += 1
            name = f"{base}{i}"
        _is_loading_props = True
        try:
            entry = props.entries.add()
            # Adding can reallocate the collection, so fetch the source only afterwards.
            source = props.entries[index]
            for prop in source.bl_rna.properties:
                key = prop.identifier
                if key in ("rna_type", "name") or (prop.is_readonly and prop.type != "COLLECTION"):
                    continue
                if prop.type == "COLLECTION":
                    for item in getattr(source, key):
                        getattr(entry, key).add().name = item.name
                else:
                    setattr(entry, key, getattr(source, key))
            entry.name = name
        finally:
            _is_loading_props = False
        props.entries.move(len(props.entries) - 1, index + 1)
        props.active_entry_index = index + 1
        update_framing_preview(obj)
        return {"FINISHED"}


class RemoveFramingEntry(bpy.types.Operator):
    bl_idname = "bim.remove_framing_entry"
    bl_label = "Remove Framing Entry"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Model.get_framing_props(context.active_object)
        if 0 <= props.active_entry_index < len(props.entries):
            props.entries.remove(props.active_entry_index)
            props.active_entry_index = max(0, props.active_entry_index - 1)
        update_framing_preview(context.active_object)
        return {"FINISHED"}


class AddFramingBreak(bpy.types.Operator):
    bl_idname = "bim.add_framing_break"
    bl_label = "Add Break"
    bl_description = "Break this member or panel at another vertical entry"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = tool.Model.get_framing_props(obj)
        if 0 <= props.active_entry_index < len(props.entries):
            entry = props.entries[props.active_entry_index]
            taken = {b.name for b in entry.breaks_at}
            # Verticals break at horizontals, the others at verticals. Start with the first
            # such entry not already listed, as that is the usual choice.
            kind = "H" if entry.kind == "V" else "V"
            choice = next((e.name for e in props.entries if e.kind == kind and e.name not in taken), "")
            global _is_loading_props
            _is_loading_props = True
            try:
                entry.breaks_at.add().name = choice
            finally:
                _is_loading_props = False
            update_framing_preview(obj)
        return {"FINISHED"}


class RemoveFramingBreak(bpy.types.Operator):
    bl_idname = "bim.remove_framing_break"
    bl_label = "Remove Break"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        props = tool.Model.get_framing_props(obj)
        if 0 <= props.active_entry_index < len(props.entries):
            entry = props.entries[props.active_entry_index]
            if 0 <= self.index < len(entry.breaks_at):
                entry.breaks_at.remove(self.index)
                update_framing_preview(obj)
        return {"FINISHED"}


class AddFramingWithin(bpy.types.Operator):
    bl_idname = "bim.add_framing_within"
    bl_label = "Add Within"
    bl_description = "Also space inside the bays of another vertical entry, so bays run between the members of both"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global _is_loading_props
        obj = context.active_object
        props = tool.Model.get_framing_props(obj)
        if 0 <= props.active_entry_index < len(props.entries):
            entry = props.entries[props.active_entry_index]
            taken = {entry.name, entry.within} | {w.name for w in entry.within_also}
            # Start with the first vertical entry not already listed.
            choice = next((e.name for e in props.entries if e.kind == "V" and e.name not in taken), "")
            _is_loading_props = True
            try:
                entry.within_also.add().name = choice
            finally:
                _is_loading_props = False
            update_framing_preview(obj)
        return {"FINISHED"}


class RemoveFramingWithin(bpy.types.Operator):
    bl_idname = "bim.remove_framing_within"
    bl_label = "Remove Within"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        props = tool.Model.get_framing_props(obj)
        if 0 <= props.active_entry_index < len(props.entries):
            entry = props.entries[props.active_entry_index]
            if 0 <= self.index < len(entry.within_also):
                entry.within_also.remove(self.index)
                update_framing_preview(obj)
        return {"FINISHED"}


class MoveFramingEntry(bpy.types.Operator):
    bl_idname = "bim.move_framing_entry"
    bl_label = "Move Framing Entry"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    def execute(self, context):
        props = tool.Model.get_framing_props(context.active_object)
        i = props.active_entry_index
        j = i - 1 if self.direction == "UP" else i + 1
        if 0 <= j < len(props.entries):
            props.entries.move(i, j)
            props.active_entry_index = j
        update_framing_preview(context.active_object)
        return {"FINISHED"}


class EnableEditingFramingPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_framing_path"
    bl_label = "Edit Framing Path"
    bl_description = "Edit the path this element's framing follows"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        element = tool.Ifc.get_entity(context.active_object) if context.active_object else None
        if not element or element.is_a("IfcTypeObject"):
            cls.poll_message_set("Paths belong to occurrences, not types.")
            return False
        return True

    def _execute(self, context):
        obj = context.active_object
        [o.select_set(False) for o in context.selected_objects if o != obj]
        props = tool.Model.get_framing_props(obj)
        if props.is_editing:
            tool.Parametric.commit_object_draft(obj, "bim.finish_editing_framing")
        element = tool.Ifc.get_entity(obj)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        guide = read_guide(element) or default_guide(1.1 / unit_scale, unit_scale)

        bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)
        verts = [bm.verts.new(Vector(v) * unit_scale) for v in guide["verts"]]
        for a, b in zip(verts, verts[1:]):
            bm.edges.new((a, b))
        if guide.get("closed") and len(verts) > 2:
            bm.edges.new((verts[-1], verts[0]))
        tool.Blender.apply_bmesh(obj.data, bm)

        props.is_editing_path = True
        if obj.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
        tool.Blender.set_viewport_tool("bim.cad_tool")
        ProfileDecorator.install(context, exit_edit_mode_callback=lambda: cancel_editing_framing_path(context))
        return {"FINISHED"}


def cancel_editing_framing_path(context: bpy.types.Context) -> set[str]:
    obj = context.active_object
    props = tool.Model.get_framing_props(obj)
    ProfileDecorator.uninstall()
    props.is_editing_path = False
    if obj.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")
    element = tool.Ifc.get_entity(obj)
    if body := ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW"):
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=body)
    return {"FINISHED"}


class CancelEditingFramingPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_framing_path"
    bl_label = "Cancel Editing Framing Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        return cancel_editing_framing_path(context)


class FinishEditingFramingPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_framing_path"
    bl_label = "Finish Editing Framing Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_framing_props(obj)
        path_data = get_path_data(obj)
        ProfileDecorator.uninstall()
        props.is_editing_path = False
        if obj.mode == "EDIT":
            bpy.ops.object.mode_set(mode="OBJECT")
        if not path_data or len(path_data["verts"]) < 2:
            self.report({"ERROR"}, "The path needs at least two connected vertices.")
            return cancel_editing_framing_path(context)
        guide = read_guide(element)
        guide["verts"] = [list(v) for v in path_data["verts"]]
        guide["closed"] = path_data["edges"][-1][-1] == path_data["edges"][0][0]
        write_framing_pset(element, Guide=guide)
        if not regenerate_framing(obj):
            self.report({"ERROR"}, get_framing_error(element) or "Framing failed.")
            cancel_editing_framing_path(context)
        refresh()
        return {"FINISHED"}


class CreateFramingType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.create_framing_type"
    bl_label = "Create Framing Type"
    bl_description = "Move this element's framing system onto a new type, so other elements can share it"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        element = tool.Ifc.get_entity(context.active_object) if context.active_object else None
        if not element or element.is_a("IfcTypeObject") or get_system_owner(element) != element:
            cls.poll_message_set("Only an element with its own framing system can become a type.")
            return False
        return True

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        ifc_file = tool.Ifc.get()
        type_obj = bpy.data.objects.new(f"{element.Name or element.is_a()[3:]} Type", None)
        element_type = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=type_obj,
            ifc_class=f"{element.is_a()}Type",
            should_add_representation=False,
        )
        write_framing_pset(element_type, Data=read_system(element))
        write_framing_pset(element, Data=None)
        if constituent_set := get_constituent_set(element):
            ifcopenshell.api.material.unassign_material(ifc_file, products=[element])
            ifcopenshell.api.material.assign_material(ifc_file, products=[element_type], material=constituent_set)
        bonsai.core.type.assign_type(tool.Ifc, tool.Model, tool.Type, element=element, type=element_type)
        refresh()
        return {"FINISHED"}


def create_framing_occurrence(
    relating_type: ifcopenshell.entity_instance, points: list[Vector], closed: bool, height: Optional[float] = None
) -> Optional[bpy.types.Object]:
    """Place an occurrence of a framing type along drawn points (world, SI units).

    :param height: In SI units. Defaults to the type's default height."""
    ifc_file = tool.Ifc.get()
    ifc_class = ifcopenshell.util.type.get_applicable_entities(relating_type.is_a(), ifc_file.schema)[0].ifc_class
    obj = bpy.data.objects.new(
        tool.Model.generate_occurrence_name(relating_type, ifc_class), bpy.data.meshes.new("Framing")
    )
    location = points[0].copy()
    obj.matrix_world = Matrix.Translation(location)
    bpy.context.view_layer.update()
    element = bonsai.core.root.assign_class(
        tool.Ifc, tool.Collector, tool.Root, obj=obj, ifc_class=ifc_class, should_add_representation=False
    )
    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    if height is None:
        height = read_system(relating_type).get("default_height", 1.1 / unit_scale)
    else:
        height = height / unit_scale
    verts = [list((p - location) / unit_scale) for p in points]
    write_framing_pset(element, Guide={"verts": verts, "closed": closed, "height": height})
    # Assigning the type builds the body from the type's system, along this path.
    bonsai.core.type.assign_type(tool.Ifc, tool.Model, tool.Type, element=element, type=relating_type)
    return obj


class FramingGhostDecorator(tool.Blender.ViewportDecorator):
    """A translucent preview of the framing being drawn, without any IFC or Blender data."""

    draw_method = "draw_ghost"
    # (world vertices, triangle indices), set by the drawing tool as the mouse moves.
    geometry: Optional[tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]] = None

    @classmethod
    def set_geometry(cls, geometry) -> None:
        cls.geometry = geometry
        tool.Blender.update_viewport()

    def draw_ghost(self, context: bpy.types.Context) -> None:
        if not (geometry := FramingGhostDecorator.geometry):
            return
        vertices, triangles = geometry
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        batch = batch_for_shader(shader, "TRIS", {"pos": vertices}, indices=triangles)
        colour = tool.Blender.get_addon_preferences().decorator_color_special
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.depth_mask_set(False)
        shader.bind()
        shader.uniform_float("color", (colour[0], colour[1], colour[2], 0.35))
        batch.draw(shader)
        gpu.state.depth_mask_set(True)
        gpu.state.depth_test_set("NONE")
        gpu.state.blend_set("NONE")


def framing_ghost(
    relating_type: ifcopenshell.entity_instance, points: list[Vector], height: Optional[float] = None
) -> Optional[tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]]:
    """World-space triangles for a framing type laid along drawn points, or None if not valid yet.

    :param height: In SI units. Defaults to the type's default height."""
    ifc_file = tool.Ifc.get()
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    system = read_system(relating_type)
    try:
        profile_meshes = {}
        for member in system.get("members", []):
            if member.get("kind") not in ("V", "H"):
                continue
            profile = ifcopenshell.util.framing.resolve_profile(ifc_file, member.get("profile"))
            if profile is None:
                return None
            profile_meshes[member["name"]] = _profile_meshes.get_or_compute(
                profile.id(), lambda profile=profile: get_profile_mesh(profile, unit_scale)
            )
        origin = points[0]
        items = compute_framing_geometry(
            system=system,
            guide=[tuple((p - origin) / unit_scale) for p in points],
            height=height / unit_scale if height else system.get("default_height", 1.1 / unit_scale),
            profile_points={name: points_ for name, (points_, _) in profile_meshes.items()},
            scope=system.get("scope", "SEGMENT"),
        )
        mesh = compute_framing_mesh(items, profile_meshes)
    except FramingError:
        return None
    vertices = [tuple(v) for v in (mesh.vertices * unit_scale + np.array(origin)).tolist()]
    triangles = [(face[0], face[i], face[i + 1]) for face in mesh.faces for i in range(1, len(face) - 1)]
    return vertices, triangles


class DrawPolylineFraming(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    bl_idname = "bim.draw_polyline_framing"
    bl_label = "Draw Polyline Framing"
    bl_description = "Draw the path of a new occurrence of the selected framing type"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self.input_options = ["D", "A", "X", "Y", "Z"]
        self.input_ui = tool.Polyline.create_input_ui(input_options=self.input_options)
        self.relating_type = None
        if relating_type_id := tool.Model.get_model_props().relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        self.ghost_key = None

    def update_ghost(self) -> None:
        """Preview the framing along the points so far plus the mouse, as it moves."""
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        points = [Vector((p.x, p.y, p.z)) for p in polyline_data[0].polyline_points] if polyline_data else []
        if polyline_props.snap_mouse_point:
            mouse = polyline_props.snap_mouse_point[0]
            points.append(Vector((mouse.x, mouse.y, mouse.z)))
        points = [p for i, p in enumerate(points) if i == 0 or (p - points[i - 1]).length > 1e-6]
        key = (tool.Model.get_model_props().framing_height, *(round(c, 6) for p in points for c in p))
        if key == self.ghost_key:
            return
        self.ghost_key = key
        height = tool.Model.get_model_props().framing_height
        geometry = framing_ghost(self.relating_type, points, height) if len(points) > 1 else None
        FramingGhostDecorator.set_geometry(geometry)

    def cleanup(self, context: bpy.types.Context) -> None:
        FramingGhostDecorator.uninstall()
        FramingGhostDecorator.geometry = None
        super().cleanup(context)

    def create_framing_from_polyline(self, context: bpy.types.Context) -> None:
        polyline_data = tool.Model.get_polyline_props().insertion_polyline
        points = [Vector((p.x, p.y, p.z)) for p in polyline_data[0].polyline_points] if polyline_data else []
        closed = len(points) > 3 and (points[0] - points[-1]).length < 1e-6
        if closed:
            points = points[:-1]
        if len(points) < 2:
            return
        height = tool.Model.get_model_props().framing_height
        if obj := create_framing_occurrence(self.relating_type, points, closed, height):
            tool.Blender.select_and_activate_single_object(context, obj)
            if error := get_framing_error(tool.Ifc.get_entity(obj)):
                self.report({"WARNING"}, error)

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        if not self.relating_type or not tool.Parametric.is_framing(self.relating_type):
            self.report({"WARNING"}, "You need to select a framing type.")
            self.cleanup(context)
            return {"FINISHED"}

        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)  # Must come before "PASS_THROUGH"

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_instructions(context)
        self.handle_mouse_move(context, event, should_round=True)
        self.choose_axis(event, z=True)
        self.choose_plane(event)
        self.handle_snap_selection(context, event)

        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            self.create_framing_from_polyline(context)
            self.tool_state.plane_method = None
            self.cleanup(context)
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)
        self.handle_inserting_polyline(context, event)

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            return cancel

        self.update_ghost()
        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        super().invoke(context, event)
        ProductDecorator.install(context)
        FramingGhostDecorator.install(context)
        self.tool_state.use_default_container = False
        self.tool_state.plane_method = None
        return {"RUNNING_MODAL"}


class EditFramingHeight(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_framing_height"
    bl_label = "Edit Framing Height"
    bl_description = (
        "Change the height of the selected framed occurrences. Only they are rebuilt; their type is unchanged"
    )
    bl_options = {"REGISTER", "UNDO"}
    height: bpy.props.FloatProperty(name="Height", min=0.001, subtype="DISTANCE")

    @classmethod
    def poll(cls, context):
        element = tool.Ifc.get_entity(context.active_object) if context.active_object else None
        if not element or element.is_a("IfcTypeObject") or not get_system_owner(element):
            cls.poll_message_set("Select a framed occurrence. A type's height is the default for new ones.")
            return False
        return True

    def invoke(self, context, event):
        self.height = get_occurrence_height(tool.Ifc.get_entity(context.active_object))
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        errors = []
        for obj in {context.active_object, *context.selected_objects}:
            if is_framed_occurrence(obj) and not set_framing_height(obj, self.height):
                element = tool.Ifc.get_entity(obj)
                errors.append(f"{element.Name or element.is_a()}: {get_framing_error(element)}")
        refresh()
        for error in errors:
            self.report({"WARNING"}, error)
        return {"FINISHED"}


class RemoveFraming(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_framing"
    bl_label = "Remove Framing"
    bl_description = "Remove the framing parameters from this element. Its current geometry stays as it is"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_framing_props(obj)
        props.is_editing = False
        if pset := get_own_framing_pset(element):
            ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)
        _errors.pop(element.id(), None)
        refresh()
        return {"FINISHED"}
