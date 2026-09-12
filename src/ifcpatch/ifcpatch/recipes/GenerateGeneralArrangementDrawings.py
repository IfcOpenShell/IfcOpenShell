# IfcPatch - IFC patching utility
# Copyright (C) 2024-2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing
import os
import re
from logging import Logger

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.document
import ifcopenshell.api.drawing
import ifcopenshell.api.group
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import numpy as np


def natural_sort_key(text):
    """Sort key that orders runs of digits by value, so "B2" comes before "B10"

    Args:
        text: String to sort by, or None

    Returns:
        List alternating text and integer parts
    """
    # re.split() puts the captured digit runs at the odd indices
    parts = re.split(r"(\d+)", text or "")
    return [int(part) if i % 2 else part for i, part in enumerate(parts)]


def sanitise_filename(name):
    """Keep only the characters Bonsai allows in drawing and sheet file names

    Args:
        name: File name

    Returns:
        The name without anything but letters, digits and "._- "
    """
    return "".join(c for c in name if c.isalnum() or c in "._- ")


# Bonsai's default drawing folders and style assets, used where the project's
# BBIM_Documentation pset doesn't set them
DOCUMENTATION_DEFAULTS = {
    "DrawingsDir": "drawings/",
    "LayoutsDir": "layouts/",
    "TitleblocksDir": "layouts/titleblocks/",
    "StylesheetPath": "drawings/assets/default.css",
    "MarkersPath": "drawings/assets/markers.svg",
    "SymbolsPath": "drawings/assets/symbols.svg",
    "PatternsPath": "drawings/assets/patterns.svg",
    "ShadingStylesPath": "drawings/assets/shading_styles.json",
}


# Bonsai's imperial drawing scales, as {denominator: HumanScale}
IMPERIAL_HUMAN_SCALES = {
    1: "1'=1'-0\"",
    2: '6"=1\'-0"',
    4: '3"=1\'-0"',
    8: '1-1/2"=1\'-0"',
    12: '1"=1\'-0"',
    16: '3/4"=1\'-0"',
    24: '1/2"=1\'-0"',
    32: '3/8"=1\'-0"',
    48: '1/4"=1\'-0"',
    64: '3/16"=1\'-0"',
    96: '1/8"=1\'-0"',
    120: "1\"=10'",
    128: '3/32"=1\'-0"',
    192: '1/16"=1\'-0"',
    240: "1\"=20'",
    360: "1\"=30'",
    384: '1/32"=1\'-0"',
    480: "1\"=40'",
    600: "1\"=50'",
    720: "1\"=60'",
    768: '1/64"=1\'-0"',
    840: "1\"=70'",
    960: "1\"=80'",
    1080: "1\"=90'",
    1200: "1\"=100'",
    1536: '1/128"=1\'-0"',
    1800: "1\"=150'",
    2400: "1\"=200'",
    3600: "1\"=300'",
    4800: "1\"=400'",
    6000: "1\"=500'",
}

# Elevation names, clockwise from true north in 45 degree steps
COMPASS_POINTS = [
    "NORTH",
    "NORTH-EAST",
    "EAST",
    "SOUTH-EAST",
    "SOUTH",
    "SOUTH-WEST",
    "WEST",
    "NORTH-WEST",
]


class ContextManager:
    """Manages IFC context creation and retrieval"""

    @staticmethod
    def ensure_contexts(ifc_file):
        """Create Annotation Context if it doesn't already exist

        Args:
            ifc_file: The IFC file

        Returns:
            Dictionary of contexts
        """
        model_context = ifcopenshell.util.representation.get_context(ifc_file, "Model")
        plan_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan")

        if not plan_context:
            plan_context = ifcopenshell.api.context.add_context(ifc_file, context_type="Plan")

        annotation_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", subcontext="Annotation")

        if not annotation_context:
            annotation_context = ifcopenshell.api.context.add_context(
                ifc_file,
                context_identifier="Annotation",
                context_type=plan_context.ContextType,
                parent=plan_context,
                target_view="PLAN_VIEW",
            )

        return {
            "model": model_context,
            "plan": plan_context,
            "annotation": annotation_context,
        }


class GeometryUtils:
    """Utility functions for geometry operations"""

    @staticmethod
    def get_location_elements(ifc_file, spatial_elements):
        """Collect the IfcElements located in any of the spatial elements

        Walks the spatial decomposition directly, which returns the same
        elements as a selector location="{Name}" query but is much faster on
        large models and doesn't depend on names being unique or set.

        Args:
            ifc_file: The IFC file
            spatial_elements: List of spatial elements

        Returns:
            Set of IfcElements
        """
        elements = set()
        for spatial_element in spatial_elements:
            elements.update(
                e for e in ifcopenshell.util.element.get_decomposition(spatial_element) if e.is_a("IfcElement")
            )
        return elements

    @staticmethod
    def iterate_shapes(ifc_file, elements):
        """Tessellate elements in one multithreaded iterator pass

        Args:
            ifc_file: The IFC file
            elements: Iterable of elements

        Yields:
            Shapes in world coordinates and project units, for elements that
            have body geometry
        """
        elements = list(elements)
        if not elements:
            return

        settings = ifcopenshell.geom.settings()
        settings.set("use-world-coords", True)
        settings.set("convert-back-units", True)
        # Openings only ever remove material, so they can't enlarge a
        # bounding box, and boolean subtraction is the slowest part of
        # tessellation. Spaces have no openings.
        settings.set("disable-opening-subtractions", True)
        settings.set("no-normals", True)
        settings.set("weld-vertices", False)

        # The hybrid kernel uses CGAL for polyhedral geometry and OpenCASCADE
        # only where needed, giving the same bounds around twice as fast.
        iterator_args = (settings, ifc_file, multiprocessing.cpu_count())
        try:
            iterator = ifcopenshell.geom.iterator(
                *iterator_args,
                include=elements,
                geometry_library="hybrid-cgal-simple-opencascade",
            )
        except RuntimeError:
            # Builds without CGAL have no hybrid kernel
            iterator = ifcopenshell.geom.iterator(*iterator_args, include=elements)
        if not iterator.initialize():
            return

        while True:
            yield iterator.get()
            if not iterator.next():
                break

    @staticmethod
    def get_rotation(element):
        """Get the rotation about z of an element's absolute placement

        This includes rotations of the placements it's relative to, such as
        a rotated site above a building.

        Args:
            element: The element, typically an IfcBuilding

        Returns:
            3x3 matrix whose columns are the element's x, y and z axes in
            world coordinates, or None if it isn't rotated
        """
        matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        angle = np.arctan2(matrix[1][0], matrix[0][0])
        if abs(angle) < 1e-9:
            return None
        cos, sin = np.cos(angle), np.sin(angle)
        return np.array([[cos, -sin, 0.0], [sin, cos, 0.0], [0.0, 0.0, 1.0]])

    @staticmethod
    def get_oriented_element_bounds(ifc_file, elements, rotations):
        """Calculate bounding boxes of element geometry, some of them rotated

        Tessellates all elements in one multithreaded iterator pass and takes
        min/max over each vertex buffer with numpy, so no per-vertex Python
        loop is involved. Rotating the vertices before taking min/max gives a
        tighter box than rotating a world-aligned box.

        Args:
            ifc_file: The IFC file
            elements: Iterable of IfcElements
            rotations: Dict of {element id: rotation from get_rotation()}

        Returns:
            Tuple of two dicts of {element id: (min_xyz, max_xyz)} in project
            units: world-aligned boxes for all elements, and boxes aligned to
            the rotated axes, in coordinates along those axes, for elements in
            rotations. Elements without body geometry are absent.
        """
        bounds = {}
        oriented_bounds = {}
        for shape in GeometryUtils.iterate_shapes(ifc_file, elements):
            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            if not len(verts):
                continue
            bounds[shape.id] = (verts.min(axis=0), verts.max(axis=0))
            rotation = rotations.get(shape.id)
            if rotation is not None:
                verts = verts @ rotation
                oriented_bounds[shape.id] = (verts.min(axis=0), verts.max(axis=0))
        return bounds, oriented_bounds

    @staticmethod
    def get_element_bounds(ifc_file, elements):
        """Calculate world bounding boxes of element geometry

        Args:
            ifc_file: The IFC file
            elements: Iterable of IfcElements

        Returns:
            Dict of {element id: (min_xyz, max_xyz)} in project units. Elements
            without body geometry are absent.
        """
        return GeometryUtils.get_oriented_element_bounds(ifc_file, elements, {})[0]

    @staticmethod
    def get_bbox(ifc_file, spatial_elements, element_bounds=None, rotation=None):
        """Calculate bounding box for spatial elements

        Encloses the geometry of all elements located in the spatial elements.
        Elements without geometry contribute their placement origin instead.

        Args:
            ifc_file: The IFC file
            spatial_elements: List of spatial elements
            element_bounds: Optional precomputed element bounds aligned to
                rotation, from get_element_bounds() or
                get_oriented_element_bounds(), to avoid tessellating the same
                elements more than once
            rotation: Optional rotation from get_rotation() to align the box
                to, instead of the world axes

        Returns:
            Tuple of (min_point, mid_point, max_point), in coordinates along
            the rotated axes if rotation is given
        """
        elements = GeometryUtils.get_location_elements(ifc_file, spatial_elements)
        if element_bounds is None:
            element_bounds = GeometryUtils.get_oriented_element_bounds(
                ifc_file, elements, {e.id(): rotation for e in elements}
            )[0 if rotation is None else 1]

        mins = []
        maxs = []

        for element in elements:
            if element.id() in element_bounds:
                element_min, element_max = element_bounds[element.id()]
                mins.append(element_min)
                maxs.append(element_max)
                continue

            local_placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            origin = local_placement[:3, 3]

            # Skip only elements sitting at the true world origin, which
            # are typically unplaced. Elements legitimately placed on a
            # single world axis (e.g. on x=0 at the grid origin) are kept.
            if not origin.any():
                continue
            if rotation is not None:
                origin = origin @ rotation

            mins.append(origin)
            maxs.append(origin)

        # No geometry or validly placed elements found: return a degenerate
        # bbox at the origin rather than crashing in the midpoint calculation.
        if not mins:
            bbox_min = [0.0, 0.0, 0.0]
            bbox_max = [0.0, 0.0, 0.0]
        else:
            bbox_min = [float(v) for v in np.min(mins, axis=0)]
            bbox_max = [float(v) for v in np.max(maxs, axis=0)]

        # Calculate midpoint
        bbox_mid = [
            (bbox_min[0] + bbox_max[0]) / 2,
            (bbox_min[1] + bbox_max[1]) / 2,
            (bbox_min[2] + bbox_max[2]) / 2,
        ]

        return (bbox_min, bbox_mid, bbox_max)

    @staticmethod
    def get_centroids(ifc_file, elements):
        """Calculate world centroids of element geometry

        Uses the volume centroid of each mesh, which unlike the mean of its
        vertices isn't pulled towards densely tessellated edges. A mesh that
        encloses no volume falls back to the mean of its vertices.

        Args:
            ifc_file: The IFC file
            elements: Iterable of elements

        Returns:
            Dict of {element id: [x, y, z]} in project units. Elements without
            body geometry are absent.
        """
        centroids = {}
        for shape in GeometryUtils.iterate_shapes(ifc_file, elements):
            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            if not len(verts):
                continue
            # Work relative to the mean vertex so that large survey
            # coordinates don't lose precision
            origin = verts.mean(axis=0)
            triangles = (verts - origin)[ifcopenshell.util.shape.get_faces(shape.geometry)]
            # Signed volumes of the tetrahedra joining each triangle to origin
            volumes = (
                np.einsum(
                    "ij,ij->i",
                    triangles[:, 0],
                    np.cross(triangles[:, 1], triangles[:, 2]),
                )
                / 6.0
            )
            volume = volumes.sum()
            if abs(volume) <= 1e-9 * np.ptp(verts, axis=0).max() ** 3:
                centroids[shape.id] = [float(v) for v in origin]
                continue
            # Each tetrahedron's centroid is a quarter of its three triangle
            # corners, its fourth corner being the origin
            centroid = origin + (volumes[:, None] * triangles.sum(axis=1)).sum(axis=0) / (4.0 * volume)
            centroids[shape.id] = [float(v) for v in centroid]
        return centroids


class ShapeCreator:
    """Creates IFC shape representations"""

    @staticmethod
    def create_camera_shape(ifc_file, x, y, z):
        """Create a camera shape representation

        Args:
            ifc_file: The IFC file
            x, y, z: Dimensions

        Returns:
            IfcProductDefinitionShape
        """
        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", subcontext="Body")

        placement = ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint([float(x / -2), float(y / -2), float(-z)]),
            None,
            None,
        )

        solid = ifc_file.createIfcCSGSolid(ifc_file.createIfcBlock(placement, x, y, z))

        return ifc_file.createIfcProductDefinitionShape(
            None,
            None,
            [ifc_file.createIfcShapeRepresentation(body_context, "Body", "CSG", [solid])],
        )

    @staticmethod
    def create_label_shape(ifc_file):
        """Create a text label shape representation

        Args:
            ifc_file: The IFC file

        Returns:
            IfcProductDefinitionShape
        """
        annotation_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", subcontext="Annotation")

        placement = ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint([0.0, 0.0, 0.0]),
            ifc_file.createIfcDirection([0.0, 0.0, 1.0]),
            ifc_file.createIfcDirection([1.0, 0.0, 0.0]),
        )

        literal = ifc_file.createIfcTextLiteralWithExtent(
            "{{Name}}",
            placement,
            "RIGHT",
            ifc_file.createIfcPlanarExtent(1000.0, 1000.0),
            "center",
        )

        representation = ifc_file.createIfcShapeRepresentation(
            annotation_context, "Annotation", "Annotation2D", [literal]
        )

        return ifc_file.createIfcProductDefinitionShape(None, None, [representation])


class DrawingGenerator:
    """Main drawing generation class"""

    def __init__(self, ifc_file, scale=None, titleblock="A2"):
        """Initialize the drawing generator

        Args:
            ifc_file: The IFC file
            scale: Drawing scale denominator (default 100, or 96 for
                1/8"=1'-0" in imperial projects)
            titleblock: Titleblock size (default "A2")
        """
        self.ifc_file = ifc_file

        # Validate basic requirements
        buildings = ifc_file.by_type("IfcBuilding")
        if not buildings:
            raise ValueError("No IfcBuilding entities found in IFC file")

        model_context = ifcopenshell.util.representation.get_context(ifc_file, "Model")
        if not model_context:
            raise ValueError("No Model context found in IFC file")

        self.imperial = self.is_imperial(ifc_file)
        # Like Bonsai, default to 1:100, or 1/8"=1'-0" in imperial projects
        self.scale = scale or (96 if self.imperial else 100)
        self.titleblock = titleblock
        self.paths = self.get_documentation_paths(ifc_file)
        self.contexts = ContextManager.ensure_contexts(ifc_file)
        # To convert meters to project units: project_units = meters / unit_scale
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

        # Calculate overall bounding box for site plan
        self.buildings = sorted(ifc_file.by_type("IfcBuilding"), key=lambda x: natural_sort_key(x.Name))
        # A building's orientation comes from its placement alone
        self.rotations = {building.id(): GeometryUtils.get_rotation(building) for building in self.buildings}
        self.true_north = ifcopenshell.util.geolocation.get_true_north(ifc_file)

        # Tessellate every element once, reused for all bounding boxes.
        # Elements of rotated buildings also get boxes aligned to their
        # building.
        elements = set()
        element_rotations = {}
        for building in self.buildings:
            building_elements = GeometryUtils.get_location_elements(ifc_file, [building])
            elements.update(building_elements)
            rotation = self.rotations[building.id()]
            if rotation is not None:
                element_rotations.update((e.id(), rotation) for e in building_elements)
        self.element_bounds, self.oriented_bounds = GeometryUtils.get_oriented_element_bounds(
            ifc_file, elements, element_rotations
        )
        # The site bbox stays aligned to the world axes, so location plans
        # are north up
        self.bbox_all = GeometryUtils.get_bbox(ifc_file, self.buildings, self.element_bounds)
        self.bbox_all_min, self.bbox_all_mid, self.bbox_all_max = self.bbox_all

        # Calculate dimensions (add 2 meters padding in project units)
        self.dim_all_x = self.bbox_all_max[0] - self.bbox_all_min[0] + 2.0 / self.unit_scale
        self.dim_all_y = self.bbox_all_max[1] - self.bbox_all_min[1] + 2.0 / self.unit_scale
        self.dim_all_z = self.bbox_all_max[2] - self.bbox_all_min[2] + 2.0 / self.unit_scale

    @staticmethod
    def is_imperial(ifc_file):
        """Check whether the project's length unit is imperial

        Like Bonsai, any length unit that isn't an SI unit counts as imperial.

        Args:
            ifc_file: The IFC file

        Returns:
            True for imperial projects
        """
        unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        return bool(unit) and not unit.is_a("IfcSIUnit")

    @staticmethod
    def get_documentation_paths(ifc_file):
        """Get the folders and style assets that drawings and sheets refer to

        As in Bonsai, these come from the project's BBIM_Documentation pset.
        Bonsai never writes that pset, so it's usually absent or only partly
        filled in, and each path falls back separately to Bonsai's default.
        Blender preferences, which Bonsai reads next, are deliberately left
        out, so the recipe gives the same result wherever it runs.

        Args:
            ifc_file: The IFC file

        Returns:
            Dict of {BBIM_Documentation property name: path}, with "/"
            separators
        """
        project = next(iter(ifc_file.by_type("IfcProject")), None)
        pset = (ifcopenshell.util.element.get_pset(project, "BBIM_Documentation") if project else None) or {}
        return {
            name: (pset.get(name) or default).replace("\\", "/") for name, default in DOCUMENTATION_DEFAULTS.items()
        }

    def get_path(self, directory, filename):
        """Get the path of a file in one of the documentation folders

        Follows Bonsai's get_default_drawing_path and its siblings, including
        their file name sanitising.

        Args:
            directory: BBIM_Documentation folder property, such as "DrawingsDir"
            filename: File name, to be sanitised

        Returns:
            Path with "/" separators
        """
        return os.path.join(self.paths[directory], sanitise_filename(filename)).replace("\\", "/")

    def get_human_scale(self, scale):
        """Format a scale denominator for a drawing's HumanScale

        Imperial projects use Bonsai's architectural or engineering notation,
        such as 1/8"=1'-0" for 1/96, where there is one.

        Args:
            scale: Drawing scale denominator

        Returns:
            HumanScale string
        """
        scale = int(scale)
        if self.imperial and scale in IMPERIAL_HUMAN_SCALES:
            return IMPERIAL_HUMAN_SCALES[scale]
        return f"1:{scale}"

    def create_drawing_pset(self, annotation, scale=50):
        """Create EPset_Drawing property set

        Args:
            annotation: The annotation element
            scale: Drawing scale denominator

        Returns:
            The created property set
        """
        scale_str = str(int(scale))
        pset = ifcopenshell.api.pset.add_pset(self.ifc_file, product=annotation, name="EPset_Drawing")

        ifcopenshell.api.pset.edit_pset(
            self.ifc_file,
            pset=pset,
            properties={
                "GeneratedBy": "endrawing",
                "TargetView": "PLAN_VIEW",
                "Scale": f"1/{scale_str}",
                "HumanScale": self.get_human_scale(scale),
                "HasUnderlay": False,
                "HasLinework": True,
                "HasAnnotation": True,
                "GlobalReferencing": True,
                "Stylesheet": self.paths["StylesheetPath"],
                "Markers": self.paths["MarkersPath"],
                "Symbols": self.paths["SymbolsPath"],
                "Patterns": self.paths["PatternsPath"],
                "ShadingStyles": self.paths["ShadingStylesPath"],
                "CurrentShadingStyle": "Blender Default",
            },
        )

        return pset

    def set_elevation_properties(self, pset, building):
        """Set elevation view properties

        Args:
            pset: The property set
            building: The building element
        """
        ifcopenshell.api.pset.edit_pset(
            self.ifc_file,
            pset=pset,
            properties={
                "TargetView": "ELEVATION_VIEW",
                # GlobalId rather than Name, which buildings can share
                "Include": f'IfcTypeProduct, IfcProduct, location="{building.GlobalId}"',
            },
        )

    def create_drawing_group(self, annotation):
        """Create a drawing group

        Args:
            annotation: The annotation element

        Returns:
            The created group
        """
        group = ifcopenshell.api.group.add_group(self.ifc_file)

        ifcopenshell.api.group.edit_group(
            self.ifc_file,
            group=group,
            attributes={
                "Name": annotation.Name,
                "ObjectType": "DRAWING",
            },
        )

        ifcopenshell.api.group.assign_group(self.ifc_file, group=group, products=[annotation])

        # Bonsai collects every drawing group in one parent group
        ifcopenshell.api.group.assign_group(self.ifc_file, group=self.drawings_group, products=[group])

        return group

    def ensure_drawings_parent_document(self):
        """Get or create the document Bonsai nests drawing documents under

        Shared with drawings made in Bonsai, so cleanup never removes it.

        Returns:
            IfcDocumentInformation named DRAWINGS
        """
        for information in self.ifc_file.by_type("IfcDocumentInformation"):
            if information.Name == "DRAWINGS" and information.Scope == "DRAWINGS":
                return information
        information = ifcopenshell.api.document.add_information(self.ifc_file)
        self.edit_information(information, Identification="DRAWINGS", Name="DRAWINGS", Scope="DRAWINGS")
        return information

    def ensure_drawings_parent_group(self):
        """Get or create the group Bonsai collects drawing groups in

        Shared with drawings made in Bonsai, so cleanup never removes it.

        Returns:
            IfcGroup named DRAWINGS
        """
        for group in self.ifc_file.by_type("IfcGroup"):
            if group.Name == "DRAWINGS" and group.ObjectType == "DRAWINGS":
                return group
        group = ifcopenshell.api.group.add_group(self.ifc_file)
        ifcopenshell.api.group.edit_group(
            self.ifc_file,
            group=group,
            attributes={"Name": "DRAWINGS", "ObjectType": "DRAWINGS"},
        )
        return group

    def edit_information(self, information, **attributes):
        """Set IfcDocumentInformation attributes, named as in IFC4

        IFC2X3 calls Identification DocumentId.

        Args:
            information: The IfcDocumentInformation
            **attributes: Attribute values
        """
        if self.ifc_file.schema == "IFC2X3" and "Identification" in attributes:
            attributes["DocumentId"] = attributes.pop("Identification")
        ifcopenshell.api.document.edit_information(self.ifc_file, information=information, attributes=attributes)

    def add_reference(self, information, **attributes):
        """Add an IfcDocumentReference with attributes named as in IFC4

        IFC2X3 calls Identification ItemReference, and has no Description, so
        Bonsai uses Name instead.

        Args:
            information: The IfcDocumentInformation to add the reference to
            **attributes: Attribute values

        Returns:
            IfcDocumentReference
        """
        reference = ifcopenshell.api.document.add_reference(self.ifc_file, information=information)
        if self.ifc_file.schema == "IFC2X3":
            if "Identification" in attributes:
                attributes["ItemReference"] = attributes.pop("Identification")
            if "Description" in attributes:
                attributes["Name"] = attributes.pop("Description")
        ifcopenshell.api.document.edit_reference(self.ifc_file, reference=reference, attributes=attributes)
        return reference

    def attach_sheet(self, annotation, sheet_info, drawing_id):
        """Create a drawing's document and place the drawing on a sheet

        Follows Bonsai's add_drawing and AddDrawingToSheet.

        Args:
            annotation: The annotation element
            sheet_info: Sheet document information
            drawing_id: Drawing ID
        """
        information = ifcopenshell.api.document.add_information(self.ifc_file, parent=self.drawings_document)
        self.edit_information(information, Identification="X", Name=annotation.Name, Scope="DRAWING")

        # Associate the drawing SVG with the drawing annotation
        location = self.get_path("DrawingsDir", f"{annotation.Name}.svg")
        reference = self.add_reference(information, Location=location)
        ifcopenshell.api.document.assign_document(self.ifc_file, products=[annotation], document=reference)

        # Place the drawing SVG on the sheet
        self.add_reference(
            sheet_info,
            Location=location,
            Identification=str(drawing_id),
            Description="DRAWING",
        )

    def create_sheet_info(self, identification, building_name):
        """Create sheet document information

        Follows Bonsai's add_sheet.

        Args:
            identification: Sheet identifier
            building_name: Building name

        Returns:
            IfcDocumentInformation
        """
        # Without a parent, the sheet is associated with the IfcProject
        sheet_info = ifcopenshell.api.document.add_information(self.ifc_file)
        self.edit_information(
            sheet_info,
            Identification=identification,
            Name=building_name,
            Description="General Arrangement",
            Purpose="General Arrangement",
            Scope="SHEET",
        )

        self.add_reference(
            sheet_info,
            Location=self.get_path("LayoutsDir", f"{identification} - {building_name}.svg"),
            Description="LAYOUT",
        )
        self.add_reference(
            sheet_info,
            Location=self.get_path("TitleblocksDir", f"{self.titleblock}.svg"),
            Description="TITLEBLOCK",
        )

        return sheet_info

    def create_plan_drawing(
        self,
        building,
        storey,
        building_bbox,
        scale,
        sheet_info,
        drawing_id,
        rotation=None,
    ):
        """Create a plan drawing for a storey

        The plan is square to its building: the camera's x axis, which runs
        along the sheet, is the building's x axis.

        Args:
            building: The building element
            storey: The building storey
            building_bbox: Building bounding box tuple
            scale: Drawing scale
            sheet_info: Sheet document information
            drawing_id: Drawing ID
            rotation: Optional building rotation from
                GeometryUtils.get_rotation(), along whose axes building_bbox
                is given

        Returns:
            Tuple of (new_drawing_id, annotation, group)
        """
        bbox_min, bbox_mid, bbox_max = building_bbox
        dim_x = bbox_max[0] - bbox_min[0] + 2.0 / self.unit_scale
        dim_y = bbox_max[1] - bbox_min[1] + 2.0 / self.unit_scale

        # Get elevation from storey placement
        local_placement = ifcopenshell.util.placement.get_local_placement(storey.ObjectPlacement)
        elevation = local_placement[2][3]

        # Camera 1.8 meters above floor in project units, looking down
        local_placement = self.create_camera_placement(
            [bbox_mid[0], bbox_mid[1], elevation + 1.8 / self.unit_scale],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            rotation,
        )

        # Create annotation (camera volume depth 10 meters in project units)
        annotation = ifcopenshell.api.root.create_entity(self.ifc_file, ifc_class="IfcAnnotation")
        # Storey names like "Ground Floor" repeat across buildings, and the
        # name gives the drawing its SVG path, so include the building
        annotation.Name = f"{building.Name} {storey.Name}"
        annotation.ObjectType = "DRAWING"
        annotation.ObjectPlacement = local_placement
        annotation.Representation = ShapeCreator.create_camera_shape(
            self.ifc_file, dim_x, dim_y, 10.0 / self.unit_scale
        )

        # Create property set
        pset = self.create_drawing_pset(annotation, scale)
        ifcopenshell.api.pset.edit_pset(
            self.ifc_file,
            pset=pset,
            properties={
                "TargetView": "PLAN_VIEW",
            },
        )

        # Attach to sheet
        self.attach_sheet(annotation, sheet_info, drawing_id)

        # Create group
        group = self.create_drawing_group(annotation)

        # Update drawing ID for next drawing
        drawing_id += 1
        return drawing_id, annotation, group

    @staticmethod
    def get_storey_spaces(storey):
        """Get the spaces that make up a storey

        Args:
            storey: The building storey

        Returns:
            List of IfcSpace
        """
        return [part for part in ifcopenshell.util.element.get_parts(storey) if part.is_a("IfcSpace")]

    def create_space_labels(self, storey, elevation, group, centroids, rotation=None):
        """Create labels for spaces in a storey

        Args:
            storey: The building storey
            elevation: Elevation value
            group: Drawing group
            centroids: Result of GeometryUtils.get_centroids() for the spaces
            rotation: Optional building rotation from
                GeometryUtils.get_rotation(), which the text follows so that
                it runs along the plan
        """
        ref_direction = [1.0, 0.0, 0.0] if rotation is None else rotation[:, 0]
        for space in self.get_storey_spaces(storey):
            # Spaces without body geometry have no centroid to label
            centroid = centroids.get(space.id())
            if centroid is None:
                continue

            # Create placement (0.1 meters above floor in project units)
            placement = self.ifc_file.createIfcLocalPlacement(
                None,
                self.ifc_file.createIfcAxis2Placement3D(
                    self.ifc_file.createIfcCartesianPoint(
                        [centroid[0], centroid[1], float(elevation) + 0.1 / self.unit_scale]
                    ),
                    self.ifc_file.createIfcDirection([0.0, 0.0, 1.0]),
                    self.ifc_file.createIfcDirection([float(v) for v in ref_direction]),
                ),
            )

            # Create room label annotation
            annotation = ifcopenshell.api.root.create_entity(self.ifc_file, ifc_class="IfcAnnotation")
            annotation.Name = "TEXT"
            annotation.ObjectType = "TEXT"
            annotation.ObjectPlacement = placement
            annotation.Representation = ShapeCreator.create_label_shape(self.ifc_file)

            # Add to group and assign to space
            ifcopenshell.api.group.assign_group(
                self.ifc_file,
                group=group,
                products=[annotation],
            )

            ifcopenshell.api.drawing.assign_product(
                self.ifc_file,
                relating_product=space,
                related_object=annotation,
            )

            # Add properties
            pset = ifcopenshell.api.pset.add_pset(
                self.ifc_file,
                product=annotation,
                name="EPset_Annotation",
            )

            ifcopenshell.api.pset.edit_pset(
                self.ifc_file,
                pset=pset,
                properties={
                    "GeneratedBy": "endrawing",
                    "Classes": "header",
                },
            )

    def create_camera_placement(self, point, axis, ref_direction, rotation=None):
        """Create an absolute placement for a drawing camera

        Args:
            point: Camera position
            axis: Camera z axis, pointing back towards the viewer
            ref_direction: Camera x axis, which runs along the drawing
            rotation: Optional rotation from GeometryUtils.get_rotation(),
                along whose axes point, axis and ref_direction are given

        Returns:
            IfcLocalPlacement
        """
        vectors = [np.array(v, dtype=float) for v in (point, axis, ref_direction)]
        if rotation is not None:
            vectors = [rotation @ v for v in vectors]
        point, axis, ref_direction = ([float(c) for c in v] for v in vectors)
        return self.ifc_file.createIfcLocalPlacement(
            None,
            self.ifc_file.createIfcAxis2Placement3D(
                self.ifc_file.createIfcCartesianPoint(point),
                self.ifc_file.createIfcDirection(axis),
                self.ifc_file.createIfcDirection(ref_direction),
            ),
        )

    def get_compass_name(self, direction):
        """Name a horizontal direction by the nearest of eight compass points

        Bearings are measured clockwise from true north. A bearing exactly
        between two compass points goes to the cardinal one.

        Args:
            direction: Direction in world coordinates

        Returns:
            Compass point name from COMPASS_POINTS, such as "NORTH-EAST"
        """
        # World +y is project north, and true north is self.true_north
        # degrees anticlockwise from it
        angle = np.degrees(np.arctan2(direction[1], direction[0]))
        sector = ((90.0 + self.true_north - angle) % 360.0) / 45.0
        lower = np.floor(sector)
        if abs(sector - lower - 0.5) < 1e-6:
            # Cardinal points have even indices
            index = lower if lower % 2 == 0 else lower + 1
        else:
            index = np.floor(sector + 0.5)
        return COMPASS_POINTS[int(index) % 8]

    def create_elevation_drawing(
        self,
        building,
        building_bbox,
        normal,
        sheet_info,
        drawing_id,
        rotation=None,
    ):
        """Create an elevation drawing of one face of a building's bbox

        The camera looks square on to the face, and the drawing is named by
        the compass point the face looks towards.

        Args:
            building: The building element
            building_bbox: Building bounding box tuple
            normal: Outward normal of the face along the bbox axes, one of
                [0, 1, 0], [0, -1, 0], [-1, 0, 0] or [1, 0, 0]
            sheet_info: Sheet document information
            drawing_id: Drawing ID
            rotation: Optional building rotation from
                GeometryUtils.get_rotation(), along whose axes building_bbox
                and normal are given

        Returns:
            new_drawing_id
        """
        bbox_min, bbox_mid, bbox_max = (np.array(v, dtype=float) for v in building_bbox)
        normal = np.array(normal, dtype=float)
        # Bbox dimensions padded by 2m in project units
        dims = bbox_max - bbox_min + 2.0 / self.unit_scale

        # Camera 0.5m out from the face in project units, looking back at it,
        # with the drawing running left to right as seen from outside
        offset = 0.5 / self.unit_scale
        point = bbox_mid + normal * ((bbox_max - bbox_min) / 2 + offset)
        ref_direction = np.cross([0.0, 0.0, 1.0], normal)
        local_placement = self.create_camera_placement(point, normal, ref_direction, rotation)

        # The camera reaches 1m (in project units) short of the far side of
        # the padded bbox
        depth = 1.0 / self.unit_scale
        camera_dims = (
            float(np.abs(ref_direction) @ dims),
            float(dims[2]),
            float(np.abs(normal) @ dims - depth),
        )

        direction = self.get_compass_name(normal if rotation is None else rotation @ normal)

        # Create annotation
        annotation = ifcopenshell.api.root.create_entity(self.ifc_file, ifc_class="IfcAnnotation")
        annotation.Name = f"{building.Name} {direction}"
        annotation.ObjectType = "DRAWING"
        annotation.ObjectPlacement = local_placement
        annotation.Representation = ShapeCreator.create_camera_shape(
            self.ifc_file, camera_dims[0], camera_dims[1], camera_dims[2]
        )

        # Create property set
        pset = self.create_drawing_pset(annotation, self.scale)
        self.set_elevation_properties(pset, building)

        # Attach to sheet
        self.attach_sheet(annotation, sheet_info, drawing_id)

        # Create group
        self.create_drawing_group(annotation)

        # Update drawing ID for next drawing
        drawing_id += 1

        return drawing_id

    def create_location_plan(self, building, sheet_info, drawing_id):
        """Create a location plan drawing

        Args:
            building: The building element
            sheet_info: Sheet document information
            drawing_id: Drawing ID

        Returns:
            new_drawing_id
        """
        # Create point at center of all buildings, above max height (1 meter in project units)
        point = self.ifc_file.createIfcCartesianPoint(
            [
                float(self.bbox_all_mid[0]),
                float(self.bbox_all_mid[1]),
                float(self.bbox_all_max[2] + 1.0 / self.unit_scale),
            ]
        )

        # Create placement
        local_placement = self.ifc_file.createIfcLocalPlacement(
            None, self.ifc_file.createIfcAxis2Placement3D(point, None, None)
        )

        # Create annotation
        annotation = ifcopenshell.api.root.create_entity(self.ifc_file, ifc_class="IfcAnnotation")
        annotation.Name = f"{building.Name} LOCATION"
        annotation.ObjectType = "DRAWING"
        annotation.ObjectPlacement = local_placement
        annotation.Representation = ShapeCreator.create_camera_shape(
            self.ifc_file, self.dim_all_x, self.dim_all_y, self.dim_all_z
        )

        # Use larger scale for location plan
        location_scale = self.scale * 10.0

        # Create property set
        pset = self.create_drawing_pset(annotation, location_scale)
        ifcopenshell.api.pset.edit_pset(
            self.ifc_file,
            pset=pset,
            properties={
                "TargetView": "PLAN_VIEW",
                "Include": f'IfcSite + IfcRoof, IfcWall, IfcSlab, location="{building.GlobalId}"',
            },
        )

        # Attach to sheet
        self.attach_sheet(annotation, sheet_info, drawing_id)

        # Create group
        self.create_drawing_group(annotation)

        # Update drawing ID for next drawing
        drawing_id += 1

        return drawing_id

    def get_references(self, information):
        """Get the document references of an IfcDocumentInformation

        Args:
            information: The IfcDocumentInformation

        Returns:
            List of IfcDocumentReference
        """
        if self.ifc_file.schema == "IFC2X3":
            return list(information.DocumentReferences or [])
        return list(information.HasDocumentReferences)

    def get_information(self, reference):
        """Get the IfcDocumentInformation that a reference belongs to

        Args:
            reference: The IfcDocumentReference

        Returns:
            IfcDocumentInformation, or None
        """
        if self.ifc_file.schema == "IFC2X3":
            return next(iter(reference.ReferenceToDocument), None)
        return reference.ReferencedDocument

    def get_reference_description(self, reference):
        """Get the role of a sheet reference, such as "DRAWING" or "LAYOUT"

        IFC2X3 references have no Description, so Bonsai uses Name instead.

        Args:
            reference: The IfcDocumentReference

        Returns:
            Description string, or None
        """
        if self.ifc_file.schema == "IFC2X3":
            return reference.Name
        return reference.Description

    def is_generated_sheet(self, sheet, drawing_locations):
        """Check whether a sheet was created by endrawing

        A generated sheet is a General Arrangement sheet whose drawings are
        all endrawing drawings. A sheet with any other drawing on it, or with
        none, belongs to the user, whatever its Purpose.

        Args:
            sheet: IfcDocumentInformation
            drawing_locations: Set of SVG locations of endrawing drawings

        Returns:
            True if endrawing created the sheet
        """
        if sheet.Scope != "SHEET" or sheet.Purpose != "General Arrangement":
            return False
        locations = [
            reference.Location
            for reference in self.get_references(sheet)
            if self.get_reference_description(reference) == "DRAWING"
        ]
        return bool(locations) and all(l in drawing_locations for l in locations)

    def cleanup_existing_drawings(self):
        """Remove all endrawing-generated drawings and sheets

        Everything removed is traced from annotations marked GeneratedBy =
        "endrawing": the annotations themselves, the documents and groups of
        the drawings among them, and the sheets holding only those drawings.
        """
        drawings = []
        labels = []
        for annotation in self.ifc_file.by_type("IfcAnnotation"):
            psets = ifcopenshell.util.element.get_psets(annotation)
            if psets.get("EPset_Drawing", {}).get("GeneratedBy") == "endrawing":
                drawings.append(annotation)
            elif psets.get("EPset_Annotation", {}).get("GeneratedBy") == "endrawing":
                labels.append(annotation)

        documents = set()
        groups = set()
        drawing_locations = set()
        for drawing in drawings:
            for rel in drawing.HasAssociations:
                if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument.is_a("IfcDocumentReference"):
                    drawing_locations.add(rel.RelatingDocument.Location)
                    information = self.get_information(rel.RelatingDocument)
                    if information:
                        documents.add(information)
            for rel in drawing.HasAssignments:
                if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                    groups.add(rel.RelatingGroup)

        # Identify sheets while their drawings still exist
        sheets = [
            sheet
            for sheet in self.ifc_file.by_type("IfcDocumentInformation")
            if self.is_generated_sheet(sheet, drawing_locations)
        ]

        # Removing a drawing's document also removes its reference and the
        # association with the drawing
        for information in documents:
            ifcopenshell.api.document.remove_information(self.ifc_file, information=information)

        for annotation in drawings + labels:
            ifcopenshell.api.root.remove_product(self.ifc_file, product=annotation)

        # A drawing group can also hold annotations the user added to the
        # drawing, so it's only removed once it's empty
        for group in groups:
            if not any(rel.RelatedObjects for rel in group.IsGroupedBy):
                ifcopenshell.api.group.remove_group(self.ifc_file, group=group)

        for sheet in sheets:
            ifcopenshell.api.document.remove_information(self.ifc_file, information=sheet)

    def get_storeys(self, building):
        """Get the storeys of a building, lowest first

        Args:
            building: The building element

        Returns:
            List of (elevation, storey) pairs
        """
        # Pairs rather than a dict keyed by elevation, so two storeys sharing
        # an elevation (mezzanines, split levels) don't overwrite each other.
        # Walking the decomposition rather than querying by location Name
        # keeps buildings that share a Name apart.
        storeys = []
        for ifc_storey in ifcopenshell.util.element.get_decomposition(building):
            if not ifc_storey.is_a("IfcBuildingStorey"):
                continue
            local_placement = ifcopenshell.util.placement.get_local_placement(ifc_storey.ObjectPlacement)
            storeys.append((local_placement[2][3], ifc_storey))
        return sorted(storeys, key=lambda s: s[0])

    def generate_drawings(self):
        """Generate all drawings for buildings"""
        self.cleanup_existing_drawings()
        self.drawings_document = self.ensure_drawings_parent_document()
        self.drawings_group = self.ensure_drawings_parent_group()

        storeys = {building: self.get_storeys(building) for building in self.buildings}

        # Tessellate every labelled space in one pass
        centroids = GeometryUtils.get_centroids(
            self.ifc_file,
            [
                space
                for building_storeys in storeys.values()
                for _, storey in building_storeys
                for space in self.get_storey_spaces(storey)
            ],
        )

        sheet_id = 0

        for building in self.buildings:
            # Create sheet for the building
            sheet_id += 1
            identification = f"A{str(sheet_id).zfill(3)}"
            sheet_info = self.create_sheet_info(identification, building.Name)

            # Calculate the building bounding box, aligned to the building's
            # own axes
            rotation = self.rotations[building.id()]
            building_bbox = GeometryUtils.get_bbox(
                self.ifc_file,
                [building],
                self.element_bounds if rotation is None else self.oriented_bounds,
                rotation,
            )

            # Drawings on a sheet are numbered from 1, as is conventional
            drawing_id = 1

            # Create plan drawings for each storey
            for elevation, storey in storeys[building]:
                drawing_id, annotation, group = self.create_plan_drawing(
                    building,
                    storey,
                    building_bbox,
                    self.scale,
                    sheet_info,
                    drawing_id,
                    rotation,
                )

                # Add space labels
                self.create_space_labels(storey, elevation, group, centroids, rotation)

            # Create elevation drawings of the bbox faces along the building's
            # +y, -y, -x and +x axes
            for normal in (
                [0.0, 1.0, 0.0],
                [0.0, -1.0, 0.0],
                [-1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
            ):
                drawing_id = self.create_elevation_drawing(
                    building,
                    building_bbox,
                    normal,
                    sheet_info,
                    drawing_id,
                    rotation,
                )

            # Create location plan if there's more than one building
            if len(self.buildings) > 1:
                drawing_id = self.create_location_plan(building, sheet_info, drawing_id)


class Patcher:
    def __init__(self, file: ifcopenshell.file, logger: Logger, scale: int = 0, titleblock: str = "A2"):
        """Generate General Arrangement drawings and sheets for every building

        Each building gets a sheet holding a plan of each of its storeys,
        elevations of its four faces, and a location plan when the site has
        more than one building. Plans and elevations follow the building's
        own axes, taken from its placement, and elevations are named by the
        nearest compass point to true north. Drawings and sheets are set up
        the way Bonsai creates them, so they can be generated in Bonsai.

        Running the recipe again replaces the drawings and sheets it created
        before, which are marked with GeneratedBy "endrawing" in their
        EPset_Drawing, and leaves all other drawings and sheets alone.

        Drawings, layouts and titleblocks go in the folders set by the
        project's BBIM_Documentation property set, as in Bonsai, and drawings
        use the style assets it sets. Anything it doesn't set, which is
        usually all of it, uses Bonsai's defaults: drawings/, layouts/,
        layouts/titleblocks/ and drawings/assets/.

        :param scale: Drawing scale denominator, such as 100 for 1:100. 0
            picks 100, or 96 (1/8"=1'-0") in imperial projects
        :param titleblock: Name of the sheet titleblock, such as "A2"

        Example:

        .. code:: python

            ifcpatch.execute({"file": model, "recipe": "GenerateGeneralArrangementDrawings", "arguments": [100, "A2"]})
        """
        self.file = file
        self.logger = logger
        # The command line passes arguments as strings
        self.scale = int(scale)
        self.titleblock = titleblock

    def patch(self) -> None:
        generator = DrawingGenerator(self.file, scale=self.scale or None, titleblock=self.titleblock)
        generator.generate_drawings()
        self.logger.info("Generated General Arrangement drawings for %d buildings", len(generator.buildings))
