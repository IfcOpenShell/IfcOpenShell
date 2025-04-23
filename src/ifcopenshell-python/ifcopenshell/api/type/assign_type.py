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
import ifcopenshell.api.type
import ifcopenshell.api.owner
import ifcopenshell.api.material
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Union, Iterable, Any


def assign_type(
    file: ifcopenshell.file,
    related_objects: list[ifcopenshell.entity_instance],
    relating_type: ifcopenshell.entity_instance,
    should_map_representations=True,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns a type to occurrences of an object

    IFC supports the concept of occurrences and types. An occurrence is an
    actual physical product in the real world: like a wall, a chair, a door,
    a column, a pump, and so on.

    Most occurrences have a corresponding type. A type describes either a
    common shape and set of properties of a particular model of equipment,
    or a construction typology. An occurrence may only have zero or one
    type.

    For example, architects would typically have a door schedule for
    individual occurrences of doors and a door types schedule for a handful
    of door types, described by the door hardware, frame, and panel. Other
    examples might be window types or wall types. Structural engineers would
    have a list of column types, beam types, slab types, etc, such as a 400
    diameter column, a 500 diameter column, and so on. Services consultant
    might nominate a particular type of sprinkler which have many
    occurrences, or light fixture types, and so on.

    Types are critical as they communicate to the procurement team what
    types of equipment and products need to be procured. The individual
    occurrences of that type tell them how many to procure. Types are also
    critical in construction as they indicate succinctly how to manufacture
    or construct something. For example, a wall type is enough information
    for a builder to understand the build up and construction of a wall.
    Types are used to help break down cost plans, or isolate portions of an
    assembly process for construction scheduling. Types are also used in
    facility maintenance, as occurrences sharing the same type can be
    repaired in the same way or by replacing the same parts.

    An occurrence of a type inherits all the properties and materials of the
    type. For example, a 2HR fire rated wall type implies that all
    wall occurrences of that wall type will also be 2HR fire rated.

    A type may or may not have a geometric representation. If a type does
    not have any representation, then the occurrences are free to have any
    representation of their own. However, if a type has a representation,
    all occurrences must have the same representation. For example, if a
    light fixture downlight type has a representation of a cylinder, then
    all occurrences must have exactly the same cylinder as its
    representation. If you change the cylinder's shape of the type, then all
    occurrence representations will also change.

    If a type does not have any geometric representation, they may have a
    parametric material representation. This may be either a parametric
    layered material or parametric cross-sectional profile material. If this
    is the case, the occurrence must be constructed out of the parametric
    material. For example, if a wall type uses a list of parametric layers
    indicating a thickness of 13mm plasterboard and 90mm stud, then the
    thickness of every wall occurrence representation must be 103mm. The
    length of each wall, however, may vary. Similarly, if a beam type has a
    parametric profile material of an I-beam, then all beam occurrences must
    also be this I-beam shape, though the length may vary.

    It is highly recommended for every occurrence to have a type. There are
    some exceptions to the rule, such as in heritage architecture or
    as-built or dilapidation models, where existing conditions are
    ambiguous, unknown or are so bespoke as to have no logical type.

    :param related_objects: The IfcElement occurrences.
    :param relating_type: The IfcElementType type.
    :param should_map_representations: If a type has a representation map,
        IFC requires all occurrences to map those representations. Some IFC
        vendors might disobey this, or you might want to handle it
        yourusecase. In this scenario, you may set this to False.
        This also enabled adding material usages mapping.
    :return: The IfcRelDefinesByType relationship
        or `None` if `related_objects` was empty list.

    Example:

    .. code:: python

        # A furniture type. This would correlate to a particular model in a
        # manufacturer's catalogue. Like an Ikea sofa :)
        furniture_type = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcFurnitureType", name="FUN01")

        # An individual occurrence of a that sofa.
        furniture = ifcopenshell.api.root.create_entity(model, ifc_class="IfcFurniture")

        # Assign the furniture to the furniture type.  If the furniture_type
        # had a representation, the furniture occurrence will also now have
        # the exact same representation. This is highly efficient as you
        # don't need to define the representation for every occurrence.
        ifcopenshell.api.type.assign_type(model, related_objects=[furniture], relating_type=furniture_type)

        # Let's imagine a parametric material layer set
        wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType", name="WAL01")

        # First, let's create a material set. This will later be assigned
        # to our wall type element.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="GYP-ST-GYP", set_type="IfcMaterialLayerSet")

        # Let's create a few materials, it's important to also give them
        # categories. This makes it easy for model recipients to do things
        # like "show me everything made out of aluminium / concrete / steel
        # / glass / etc". The IFC specification states a list of categories
        # you can use.
        gypsum = ifcopenshell.api.material.add_material(model, name="PB01", category="gypsum")
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel")

        # Now let's use those materials as three layers in our set, such
        # that the steel studs are sandwiched by the gypsum. Let's imagine
        # we're setting the layer thickness in millimeters.
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=gypsum)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": .013})
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=steel)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": .092})
        layer = ifcopenshell.api.material.add_layer(model, layer_set=material_set, material=gypsum)
        ifcopenshell.api.material.edit_layer(model, layer=layer, attributes={"LayerThickness": .013})

        # Great! Let's assign our material set to our wall type.
        ifcopenshell.api.material.assign_material(model, products=[wall_type], material=material_set)

        # Now, let's create a wall.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # The wall is a WAL01 wall type.
        ifcopenshell.api.type.assign_type(model, related_objects=[wall], relating_type=wall_type)

        # A bit of preparation, let's create some geometric contexts since
        # we want to create some geometry for our wall.
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # Notice how our thickness of 0.118 must equal .013 + .092 + .013 from our type
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.118)

        # Assign our new body geometry back to our wall
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)

        # Place our wall at the origin
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(related_objects, relating_type, should_map_representations)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self,
        related_objects: list[ifcopenshell.entity_instance],
        relating_type: ifcopenshell.entity_instance,
        should_map_representations: bool,
    ):
        if not related_objects:
            return

        related_objects_set = set(related_objects)

        ifc2x3 = self.file.schema == "IFC2X3"

        related_objects_set = set(related_objects)
        if ifc2x3:
            types = next(iter(relating_type.ObjectTypeOf), None)
        else:
            types = next(iter(relating_type.Types), None)

        previous_types_rels: set[ifcopenshell.entity_instance] = set()
        objects_without_types: list[ifcopenshell.entity_instance] = []
        objects_with_types: list[ifcopenshell.entity_instance] = []

        # check if there is anything to change
        for obj in related_objects_set:
            if ifc2x3:
                object_rel = next((i for i in obj.IsDefinedBy if i.is_a("IfcRelDefinesByType")), None)
            else:
                object_rel = next(iter(obj.IsTypedBy), None)

            if object_rel is None:
                objects_without_types.append(obj)
                continue

            # either rel doesn't exist or product is part of different rel
            if object_rel != types:
                previous_types_rels.add(object_rel)
                objects_with_types.append(obj)

        objects_to_change = objects_without_types + objects_with_types
        # nothing to change
        if not objects_to_change:
            return types

        # unassign from previous types
        for is_typed_by in previous_types_rels:
            cur_related_objects = set(is_typed_by.RelatedObjects) - related_objects_set
            if cur_related_objects:
                is_typed_by.RelatedObjects = list(cur_related_objects)
                ifcopenshell.api.owner.update_owner_history(self.file, **{"element": is_typed_by})
            else:
                history = is_typed_by.OwnerHistory
                self.file.remove(is_typed_by)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)

        # assign objects to a new type
        if types:
            types.RelatedObjects = list(set(types.RelatedObjects) | related_objects_set)
            ifcopenshell.api.owner.update_owner_history(self.file, **{"element": types})
        else:
            types = self.file.create_entity(
                "IfcRelDefinesByType",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
                RelatedObjects=list(related_objects_set),
                RelatingType=relating_type,
            )

        if should_map_representations:
            if getattr(relating_type, "RepresentationMaps", None):
                for related_object in objects_to_change:
                    ifcopenshell.api.type.map_type_representations(
                        self.file,
                        related_object=related_object,
                        relating_type=relating_type,
                    )
            self.map_material_usages(objects_to_change, relating_type)
        return types

    def map_material_usages(
        self, related_objects: list[ifcopenshell.entity_instance], relating_type: ifcopenshell.entity_instance
    ) -> None:
        type_material = ifcopenshell.util.element.get_material(relating_type)
        if not type_material:
            return
        ifc_class = type_material.is_a()
        if ifc_class in ("IfcMaterialLayerSet", "IfcMaterialProfileSet"):
            ifcopenshell.api.material.assign_material(
                self.file,
                products=related_objects,
                type=f"{ifc_class}Usage",
            )
