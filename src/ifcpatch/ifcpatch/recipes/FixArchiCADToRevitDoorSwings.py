# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


import os
import math
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.util.schema
import ifcopenshell.util.element


class Patcher:
    def __init__(self, file, logger):
        """Fix missing door swings in Revit when viewing ArchiCAD IFCs

        ArchiCAD has the ability to store 2D data with objects like doors for
        door swings. ArchiCAD's implementation is not 100% correct (using
        footprint instead of annotation contexts), but otherwise not too
        shabby.

        Revit, however, is incapable of understanding this 2D representation.
        Revit users linking in IFCs produced by ArchiCAD may experience the
        following symptoms:

        A. Invisible doors, and difficulty selecting doors
        B. Invisible door swings, or only visible at particular view ranges
        C. Weird arc shapes around doors
        D. Extra lines around doors and walls
        E. Cannot easily change visibility graphics of 2D vs 3D elements
        F. Cannot view 2D data in a 3D view

        This is caused by the perfect storm of Revit IFC bugs, which we will
        work through methodically. For programmers interested in the details of
        how we fix this, read the comments of the patch function.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})
        """
        self.file = file
        self.logger = logger

    def patch(self):
        # Revit has the ability to switch between 3D representations and 2D
        # representations (e.g. in plan view). It does this by detecting IFC
        # representations that belong to either the Model Body representation
        # for 3D and the "Annotation" representation for 2D. Note: this is not a real
        # "Annotation" representation. It is an invalid representation that is
        # hardcoded in Revit. Nevertheless, if you follow their incorrect
        # context naming convention by renaming ArchiCAD's also incorrect
        # FootPrint context (but less incorrect) to Annotation, Revit will show
        # 2D door representations as desired and switch between 2D and 3D
        # intelligently.
        #
        # See bug https://github.com/Autodesk/revit-ifc/issues/187

        # for context in self.file.by_type("IfcGeometricRepresentationSubContext"):
        #    if context.ContextIdentifier == "FootPrint":
        #        context.ContextIdentifier = None
        #        context.ContextType = "Annotation"
        #        context.ParentContext = [
        #            c
        #            for c in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
        #            if c.ContextType == "Plan"
        #        ][0]

        # However, we will not use this approach (hence it is commented out).
        # This is because Revit will generate a single object with both a
        # magically switching 2D and 3D representation - you cannot control both
        # representations independently. Furthermore, the 2D representation is
        # always generated at a Z value of 0. This means that the door swings
        # are always invisible on any view range apart from those typically near
        # an elevation of 0 which won't work for most projects. Because they are
        # merged into a single object, you cannot fix the 2D elevation without
        # breaking your 3D elevation. Even if we split it into 2D and 3D
        # objects, the 2D object can only be moved up in 3D or section, but
        # Revit makes the object invisible in 3D or section, so go fish.
        #
        # See symptom B.

        # Purge axis representations from walls. Revit will draw the axis (a
        # line through the wall) but doesn't give you control over its
        # visibility, resulting in very ugly walls and lines typically cutting
        # across door openings.
        #
        # See bug https://github.com/Autodesk/revit-ifc/issues/360
        #
        # This fixes symptom D.

        for wall in self.file.by_type("IfcWall"):
            reps = list(wall.Representation.Representations)
            reps_excluding_axis = [r for r in reps if r.RepresentationIdentifier != "Axis"]
            wall.Representation.Representations = reps_excluding_axis

        # We're going to split the 3D door body and the 2D door swing into two
        # objects. Before we do that, we're going to cull the 2D representation
        # from door types. If we didn't, this scenario may occur:
        #
        # 1. 3D IfcDoors with IfcDoorType import as Revit doors
        # 2. 2D IfcBuildingElementProxy with no type import as Revit generic model
        # 3. The Revit user turns off the visibility of the door category.
        # 4. The user is shocked to see that generic models are now invisible,
        #    even though it is clearly a separate category to doors.
        #
        # This should be a warning to all Revit users that unintuitively
        # visibility graphics actually do _not_ affect the categories (e.g.
        # Door, Window) for instances. Instead, they target categories for
        # representation maps types, even if an instance is untyped. Yikes!
        #
        # See bug: https://github.com/Autodesk/revit-ifc/issues/362
        #
        # This fixes symptom E.

        for door in self.file.by_type("IfcDoorType"):
            rep_maps = list(door.RepresentationMaps or [])
            door.RepresentationMaps = [
                r
                for r in rep_maps
                if r.MappedRepresentation
                if r.MappedRepresentation.RepresentationIdentifier != "FootPrint"
            ]

        # Let's now duplicate each door. The original door shall only retain its
        # non 2D representations. The copied door will be changed into a
        # "IfcDiscreteAccessory" so it can be filtered separately in Revit.
        # Then, the copied door will only retain 2D representations. However,
        # we're going to change the 2D representation context into a Model Body
        # 3D context. This tricks Revit into converting the 2D data into 3D
        # model line geometry (or something similar to that).
        #
        # See bug https://github.com/Autodesk/revit-ifc/issues/358
        #
        # This fixes symptom A, B, and F.

        for door in self.file.by_type("IfcDoor"):
            reps = list(door.Representation.Representations)
            reps_excluding_footprint = [r for r in reps if r.RepresentationIdentifier != "FootPrint"]
            footprint_reps = [r for r in reps if r.RepresentationIdentifier == "FootPrint"]
            if not footprint_reps:
                continue
            door_copy = ifcopenshell.util.element.copy(self.file, door)
            door_copy = ifcopenshell.util.schema.reassign_class(self.file, door_copy, "IfcDiscreteAccessory")
            door_copy.Representation = ifcopenshell.util.element.copy(self.file, door.Representation)
            door_copy.Representation.Representations = footprint_reps
            door.Representation.Representations = reps_excluding_footprint
            related_elements = list(door.ContainedInStructure[0].RelatedElements)
            related_elements.append(door_copy)
            door.ContainedInStructure[0].RelatedElements = related_elements

            body_context = next(
                c for c in self.file.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Body"
            )
            for subelement in self.file.traverse(footprint_reps[0]):
                if not subelement.is_a("IfcShapeRepresentation"):
                    continue
                subelement.ContextOfItems = body_context
                subelement.RepresentationIdentifier = "Body"
                subelement.RepresentationType = "Curve3D"

        # Revit has bugs with handling arc index, which is relevant in IFC4. Our
        # solution is to facet the arcs and swap out the polycurves with new
        # faceted polycurves.
        #
        # See bug https://github.com/Autodesk/revit-ifc/issues/359
        #
        # This fixes symptom C.

        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        for curve in self.file.by_type("IfcIndexedPolyCurve"):
            if True in [s.is_a("IfcArcIndex") for s in curve.Segments]:
                shape = ifcopenshell.geom.create_shape(settings, curve)
                e = shape.edges
                v = shape.verts
                is_2d = curve.Points.is_a("IfcCartesianPointList2D")
                if is_2d:
                    vertices = [[v[i] / unit_scale, v[i + 1] / unit_scale] for i in range(0, len(v), 3)]
                else:
                    vertices = [
                        [v[i] / unit_scale, v[i + 1] / unit_scale, v[i + 2] / unit_scale] for i in range(0, len(v), 3)
                    ]
                edges = [[e[i] + 1, e[i + 1] + 1] for i in range(0, len(e), 2)]
                points = []
                curve.Points = f.create_entity(curve.Points.is_a(), vertices)
                curve.Segments = [f.createIfcLineIndex(e) for e in edges]
