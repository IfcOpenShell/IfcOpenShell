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
import ifcopenshell.util.representation
from typing import Optional, Any


def add_context(
    file: ifcopenshell.file,
    context_type: Optional[ifcopenshell.util.representation.CONTEXT_TYPE] = None,
    context_identifier: Optional[ifcopenshell.util.representation.REPRESENTATION_IDENTIFIER] = None,
    target_view: Optional[ifcopenshell.util.representation.TARGET_VIEW] = None,
    parent: Optional[ifcopenshell.entity_instance] = None,
) -> ifcopenshell.entity_instance:
    """Adds a new geometric representation context

    In IFC, physical objects may have zero, one, or multiple geometric
    representations associated with it. For example, a building storey might
    not have any geometry, but simply be a coordinate in space.
    Alternatively, a wall might have a 3D body representation in the form of
    a cuboid. As a final example, a door might also have a 3D body
    representation of a 3D door panel and door frame, but may additionally
    have a 2D door plan view representation of the door swing, and even a 2D
    elevation view of the door, a 3D box representing the disabled clearance
    zone of the door, a 2D profile representing the profile of the door to
    cut out in a wall, and so on. In this situation, a door will have
    multiple geometric representations.

    To distinguish between the different purposes of multiple geometric
    representations, each geometric representation must belong to a
    geometric representation "context". There are typically always 2
    contexts, one for 3D representations and one for 2D representations.
    These 2 contexts then have subcontexts for things like the 3D body
    representation, clearance representations, annotation representations,
    and so on. Each representation of a physical IFC product (e.g. a door)
    must be assigned to one of these subcontexts. Therefore setting up
    appropriate contexts is critical prior to authoring any IFC model which
    contains geometry.

    There are two steps to setting up appropriate subcontexts. First, a 2D
    and/or 3D context must be added. These must be always called the "Model"
    context for 3D and the "Plan" context for 2D (even if the 2D geometry is
    not a plan view). Then, one or more subcontexts are added using either
    the "Model" or "Plan" as their parent. These subcontexts are further
    distinguished using an "identifier" and "target view". The "identifier"
    describes the purpose of the representation, and the "target view"
    describes the typical diagrammatic presentation that context's geometry
    should be viewed in. The most common identifiers you might use are:

    - Body: for the actual shape of the object
    - Box: the bounding box of the object (useful for shape analytics)
    - Axis: the parametric line determining the shape of the object
    - Profile: the elevation silhouette of the object, useful for cutting
          out holes for the object to fit into host elements
    - Footprint: the plan view silhouette of the object, useful for certain
          quantity take-off rules
    - Clearance: the clearance zone of the object
    - Annotation: symbolic annotations typically used in diagrams or
          drawings

    The most common "target views" you might use are:

    - MODEL_VIEW: for 3D geometry you might see in a BIM viewer
    - PLAN_VIEW: for 2D geometry you might see in a plan representation
    - ELEVATION_VIEW: for 2D geometry you might see in an elevation representation
    - SECTION_VIEW: for 2D geometry you might see in a section representation
    - GRAPH_VIEW: for 2D or 3D line or frame or path connectivity diagrams
          you might use for structural frame analysis, axis-based parametric
          modeling
    - SKETCH_VIEW: for viewing abstract high-level representations such as
          in bubble diagrams of spatial topology

    This may sound like a lot, but after a few typical contexts are set up
    at the beginning, it becomes easy to navigate and isolate geometry for
    different purposes. There is also the concept of a target scale, which
    represents the zoom level detail of geometry, but this is not currently
    supported by this API. Setting up all these contexts are also optional,
    and you may only use a single Model context and Body subcontext for
    simple models, but this simplification sacrifices the ability of more
    parametric or analytical usecases.

    :param context_type: The type of the context, must be one of "Model" or
        "Plan" only.
    :type context_type: str, optional
    :param context_identifier: The identifier of the context, chosen from
        one of the common identifiers above or consult the IFC documentation
        (under the IfcShapeRepresentation page) for more details. Optional
        for contexts, but mandatory for subcontexts.
    :type context_identifier: str, optional
    :param target_view: the target view of the context, chosen from one of
        the common target views above or consult the IFC documentation
        (under the IfcShapeRepresentation page) for more details. Optional
        for contexts, but mandatory for subcontexts.
    :param parent: the parent context. Must be left as None (the default)
        for contexts, and only set for subcontexts. Note that there are only
        contexts and subcontexts, a subcontext cannot have any children.
    :type parent: ifcopenshell.entity_instance, optional
    :return: the newly created IfcGeometricRepresentationContext or
        IfcGeometricRepresentationSubContext entity
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # If we plan to store 3D geometry in our IFC model, we have to setup
        # a "Model" context.
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")

        # And/Or, if we plan to store 2D geometry, we need a "Plan" context
        plan = ifcopenshell.api.context.add_context(model, context_type="Plan")

        # Now we setup the subcontexts with each of the geometric "purposes"
        # we plan to store in our model. "Body" is by far the most important
        # and common context, as most IFC models are assumed to be viewable
        # in 3D.
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # The 3D Axis subcontext is important if any "axis-based" parametric
        # geometry is going to be created. For example, a beam, or column
        # may be drawn using a single 3D axis line, and for this we need an
        # Axis subcontext.
        ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Axis", target_view="GRAPH_VIEW", parent=model3d)

        # The 3D Box subcontext is useful for clash detection or shape
        # analysis, or even lazy-loading of large models.
        ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Box", target_view="MODEL_VIEW", parent=model3d)

        # It's also important to have a 2D Axis subcontext for things like
        # walls and claddings which can be drawn using a 2D axis line.
        ifcopenshell.api.context.add_context(model,
            context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan)

        # A 2D annotation subcontext for plan views are important for door
        # swings, window cuts, and symbols for equipment like GPOs, fire
        # extinguishers, and so on.
        ifcopenshell.api.context.add_context(model,
            context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan)

        # You may also create 2D annotation subcontexts for sections and
        # elevation views.
        ifcopenshell.api.context.add_context(model,
            context_type="Plan", context_identifier="Annotation", target_view="SECTION_VIEW", parent=plan)
        ifcopenshell.api.context.add_context(model,
            context_type="Plan", context_identifier="Annotation", target_view="ELEVATION_VIEW", parent=plan)

        # Let's create a new wall. The wall does not have any geometry yet.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's use the "3D Body" representation we created earlier to add a
        # new wall-like body geometry, 5 meters long, 3 meters high, and
        # 200mm thick
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.2)

        # Assign our new body geometry back to our wall
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)

        # Place our wall at the origin
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "context_type": context_type,
        "parent": parent,
        "context_identifier": context_identifier,
        "target_view": target_view,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        if not self.settings["parent"]:
            if self.settings["context_type"] == "Plan":
                self.create_2d_origin()
                context = self.file.createIfcGeometricRepresentationContext(None, "Plan", 2, 1.0e-05, self.origin)
            else:
                self.create_3d_origin()
                context = self.file.createIfcGeometricRepresentationContext(
                    None, self.settings["context_type"], 3, 1.0e-05, self.origin
                )

            project = self.file.by_type("IfcProject")[0]

            if project.RepresentationContexts:
                contexts = list(project.RepresentationContexts)
            else:
                contexts = []
            contexts.append(context)
            project.RepresentationContexts = contexts
            return context
        return self.file.create_entity(
            "IfcGeometricRepresentationSubContext",
            **{
                "ContextIdentifier": self.settings["context_identifier"],
                "ContextType": self.settings["context_type"],
                "ParentContext": self.settings["parent"],
                "TargetView": self.settings["target_view"],
            }
        )

    def create_3d_origin(self):
        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )

    def create_2d_origin(self):
        self.origin = self.file.createIfcAxis2Placement2D(
            self.file.createIfcCartesianPoint((0.0, 0.0)),
            self.file.createIfcDirection((1.0, 0.0)),
        )
