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
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.api.geometry
import ifcopenshell.api.type
import ifcopenshell.api.project
import ifcopenshell.api.context
import ifcopenshell.api.owner.settings
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.unit
from typing import Optional, Any, Union, Literal, get_args, Callable
from functools import partial


APPENDABLE_ASSET = Literal[
    "IfcTypeProduct",
    "IfcProduct",
    "IfcMaterial",
    "IfcCostSchedule",
    "IfcProfileDef",
    "IfcPresentationStyle",
]
APPENDABLE_ASSET_TYPES = get_args(APPENDABLE_ASSET)


def append_asset(
    file: ifcopenshell.file,
    library: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    reuse_identities: Optional[dict[int, ifcopenshell.entity_instance]] = None,
    assume_asset_uniqueness_by_name: bool = True,
) -> ifcopenshell.entity_instance:
    """Appends an asset from a library into the active project

    A BIM library asset may be a type product (e.g. wall type), product
    (e.g. pump), material, profile, or cost schedule.

    This copies the asset from the specified library file into the active
    project. It handles all details like ensuring that product materials,
    styles, properties, quantities, and so on are preserved.

    If an asset contains geometry, the geometric contexts are also
    intelligentely transplanted such that existing equivalent contexts are
    reused.

    Do not mix units.

    :param library: The file object containing the asset.
    :param element: An element in the library file of the asset. It may be
        an IfcTypeProduct, IfcProduct, IfcMaterial, IfcCostSchedule, or
        IfcProfileDef.
    :param reuse_identities: Optional dictionary of mapped entities' identities to the
        already created elements. It will be used to avoid creating
        duplicated inverse elements during multiple `project.append_asset` calls. If you want
        to add just 1 asset or if added assets won't have any shared elements, then it can be left empty.
    :param assume_asset_uniqueness_by_name: If True, checks if elements (profiles, materials, styles)
        with the same name already exist in the project and reuses them instead of appending new ones.
    :return: The appended element

    Example:

    .. code:: python

        # Programmatically generate a library. You could do this visually too.
        library = ifcopenshell.api.project.create_file()
        root = ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject", name="Demo Library")
        context = ifcopenshell.api.root.create_entity(library,
            ifc_class="IfcProjectLibrary", name="Demo Library")
        ifcopenshell.api.project.assign_declaration(library, definitions=[context], relating_context=root)

        # Assign units for our example library
        unit = ifcopenshell.api.unit.add_si_unit(library,
            unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(library, units=[unit])

        # Let's create a single asset of a 200mm thick concrete wall
        wall_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType", name="WAL01")
        concrete = ifcopenshell.api.material.add_material(usecase.file, name="CON", category="concrete")
        rel = ifcopenshell.api.material.assign_material(library,
            products=[wall_type], type="IfcMaterialLayerSet")
        layer = ifcopenshell.api.material.add_layer(library,
            layer_set=rel.RelatingMaterial, material=concrete)
        layer.Name = "Structure"
        layer.LayerThickness = 200

        # Mark our wall type as a reusable asset in our library.
        ifcopenshell.api.project.assign_declaration(library,
            definitions=[wall_type], relating_context=context)

        # Let's imagine we're starting a new project
        model = ifcopenshell.api.project.create_file()
        project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="Test")

        # Now we can easily append our wall type from our library
        wall_type = ifcopenshell.api.project.append_asset(model, library=library, element=wall_type)

    Example of adding multiple assets and avoiding duplicated inverses:

    .. code:: python

        # since occurrences of IfcWindow of the same type
        # might have shared inverses (e.g. IfcStyledItem)
        # we provide a dictionary that will be populated with newly created items
        # and reused to avoid duplicated elements
        reuse_identities = dict()

        for element in ifcopenshell.util.selector.filter_elements(model, "IfcWindow"):
            ifcopenshell.api.project.append_asset(
                model, library=library,
                element=wall_type
                reuse_identities=reuse_identities
            )

    """
    usecase = Usecase()
    usecase.file: ifcopenshell.file = file
    usecase.settings = {
        "library": library,
        "element": element,
        "reuse_identities": {} if reuse_identities is None else reuse_identities,
        "assume_asset_uniqueness_by_name": assume_asset_uniqueness_by_name,
    }
    return usecase.execute()


class SafeRemovalContext:
    """Context manager to ensure `remove_deep` won't create invalid entities
    in `reuse_identities` leading to possible crashes.

    Should be always used if removing an entity that was possibly added by `file_add`.
    """

    file: ifcopenshell.file
    reuse_identities: dict[int, ifcopenshell.entity_instance]

    assume_asset_uniqueness_by_name: bool
    """If `False`, then all job is done by `file.add`
    and we don't need to worry about invalid entities."""

    def __init__(
        self,
        ifc_file: ifcopenshell.file,
        reuse_identities: dict[int, ifcopenshell.entity_instance],
        assume_asset_uniqueness_by_name: bool,
    ):
        self.file = ifc_file
        self.reuse_identities = reuse_identities
        self.assume_asset_uniqueness_by_name = assume_asset_uniqueness_by_name

    def __enter__(self):
        if not self.assume_asset_uniqueness_by_name:
            return

        ifcopenshell.util.element.batch_remove_deep2(self.file)

    def __exit__(self, *args):
        if not self.assume_asset_uniqueness_by_name:
            return

        # Collect identities.
        removed_identities: dict[ifcopenshell.entity_instance, int] = {}
        assert self.file.to_delete is not None
        removed_elements = self.file.to_delete
        for identity, element in self.reuse_identities.items():
            if element in removed_elements:
                removed_identities[element] = identity
        assert len(removed_identities) == len(removed_elements)

        # Actually remove elements.
        for element in self.file.to_delete:
            if element in self.file.to_delete:
                self.file.remove(element)
        self.file.to_delete = None

        # Clean up dead identities.
        for identity in removed_identities.values():
            del self.reuse_identities[identity]


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]
    assume_asset_uniqueness_by_name: bool
    whitelisted_inverse_attributes: dict[str, list[str]]

    added_elements: dict[int, ifcopenshell.entity_instance]
    """Elements added with ``add_element``."""

    reuse_identities: dict[int, ifcopenshell.entity_instance]
    """Mapping of old element ids to new elements, usually fiiled by ``file_add``."""

    def execute(self):
        # mapping of old element ids to new elements
        self.added_elements: dict[int, ifcopenshell.entity_instance] = {}
        self.reuse_identities: dict[int, ifcopenshell.entity_instance] = self.settings["reuse_identities"]
        self.whitelisted_inverse_attributes = {}
        self.base_material_class = "IfcMaterial" if self.file.schema == "IFC2X3" else "IfcMaterialDefinition"
        self.assume_asset_uniqueness_by_name = self.settings["assume_asset_uniqueness_by_name"]

        if self.settings["element"].is_a("IfcTypeProduct"):
            self.target_class = "IfcTypeProduct"
            return self.append_type_product()
        elif self.settings["element"].is_a("IfcProduct"):
            self.target_class = "IfcProduct"
            return self.append_product()
        elif self.settings["element"].is_a("IfcMaterial"):
            self.target_class = "IfcMaterial"
            return self.append_material()
        elif self.settings["element"].is_a("IfcCostSchedule"):
            self.target_class = "IfcCostSchedule"
            return self.append_cost_schedule()
        elif self.settings["element"].is_a("IfcProfileDef"):
            self.target_class = "IfcProfileDef"
            return self.append_profile_def()
        elif self.settings["element"].is_a("IfcPresentationStyle"):
            self.target_class = "IfcPresentationStyle"
            return self.append_presentation_style()

    def by_guid(self, guid: str) -> Union[ifcopenshell.entity_instance, None]:
        try:
            return self.file.by_guid(guid)
        except RuntimeError:
            return None

    def get_existing_element(self, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        """Get existing element for a library element.

        Return element if it was already added with ``add_element``
        or if it's not necessary (model already has a replacement for it).

        Note that if element is returned, it will be accepted as-is,
        it's subgraph inverses won't be checked.

        Return ``None`` if element wasn't added before and needs to be added.
        """
        if element.id() in self.added_elements:
            return self.added_elements[element.id()]
        if element.is_a("IfcRoot"):
            return self.by_guid(element.GlobalId)
        elif not self.assume_asset_uniqueness_by_name:
            return None
        elif element.is_a("IfcMaterial"):
            name = element.Name
            return next((e for e in self.file.by_type("IfcMaterial") if e.Name == name), None)
        elif element.is_a("IfcProfileDef"):
            profile_name = element.ProfileName
            if profile_name is None:
                return None
            return next((e for e in self.file.by_type("IfcProfileDef") if e.ProfileName == profile_name), None)
        elif element.is_a("IfcPresentationStyle"):
            name = element.Name
            if name is None:
                return None
            return next((e for e in self.file.by_type(element.is_a()) if e.Name == name), None)

        # Not really assets but if we don't check them here,
        # their subgraph entities may be appended twice.
        elif (ifc_class := element.is_a()) == "IfcOrganization":
            attr_name = "Id" if self.file.schema == "IFC2X3" else "Identification"
            org_id = getattr(element, attr_name)
            if org_id is not None:
                return next((e for e in self.file.by_type("IfcOrganization") if getattr(e, attr_name) == org_id), None)
        elif ifc_class == "IfcPerson":
            attr_name = "Id" if self.file.schema == "IFC2X3" else "Identification"
            person_id = getattr(element, attr_name)
            if person_id is not None:
                return next((e for e in self.file.by_type("IfcPerson") if getattr(e, attr_name) == person_id), None)

        else:
            return None

    def append_material(self):
        self.whitelisted_inverse_attributes = {
            "IfcMaterial": ["HasExternalReferences", "HasProperties", "HasRepresentation"]
        }
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        element = self.add_element(self.settings["element"])
        if element.HasRepresentation:
            self.reuse_existing_contexts()
        return element

    def append_cost_schedule(self):
        self.whitelisted_inverse_attributes = {"IfcCostSchedule": ["Controls"], "IfcCostItem": ["IsNestedBy"]}
        return self.add_element(self.settings["element"])

    def append_profile_def(self):
        self.whitelisted_inverse_attributes = {"IfcProfileDef": ["HasProperties"]}
        return self.add_element(self.settings["element"])

    def append_presentation_style(self):
        self.whitelisted_inverse_attributes = {}
        return self.add_element(self.settings["element"])

    def append_type_product(self):
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            self.base_material_class: ["HasExternalReferences", "HasProperties", "HasRepresentation"],
            "IfcRepresentationItem": ["StyledByItem", "LayerAssignment"],
            "IfcRepresentation": ["LayerAssignments"],
            "IfcProductDefinitionShape": ["HasShapeAspects"],
            "IfcRepresentationMap": ["HasShapeAspects"],
        }
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        element = self.add_element(self.settings["element"])
        self.reuse_existing_contexts()
        return element

    def append_product(self):
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            "IfcObject": ["IsDefinedBy.IfcRelDefinesByProperties"],
            "IfcElement": ["HasOpenings"],
            self.base_material_class: ["HasExternalReferences", "HasProperties", "HasRepresentation"],
            "IfcRepresentationItem": [
                "StyledByItem",
                "LayerAssignments" if self.file.schema == "IFC2X3" else "LayerAssignment",
            ],
            "IfcRepresentation": ["LayerAssignments"],
            "IfcProductDefinitionShape": ["HasShapeAspects"],
            "IfcRepresentationMap": ["HasShapeAspects"],
        }
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        element = self.add_element(self.settings["element"])
        self.reuse_existing_contexts()

        placement = element.ObjectPlacement
        if placement is not None:
            matrix = ifcopenshell.util.placement.get_local_placement(placement)
            matrix = ifcopenshell.util.geolocation.auto_local2global(self.settings["library"], matrix)
            matrix = ifcopenshell.util.geolocation.auto_global2local(self.file, matrix)
            with SafeRemovalContext(self.file, self.reuse_identities, self.assume_asset_uniqueness_by_name):
                ifcopenshell.api.geometry.edit_object_placement(self.file, element, matrix, is_si=False)

        element_type = ifcopenshell.util.element.get_type(self.settings["element"])
        if element_type:
            ifcopenshell.api.owner.settings.factory_reset()
            new_type = ifcopenshell.api.project.append_asset(
                self.file,
                library=self.settings["library"],
                element=element_type,
                reuse_identities=self.reuse_identities,
            )
            ifcopenshell.api.type.assign_type(
                self.file,
                should_run_listeners=False,
                related_objects=[element],
                relating_type=new_type,
                should_map_representations=False,
            )
            ifcopenshell.api.owner.settings.restore()

        return element

    def add_element(self, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        """Add element and check all it's subgraph inverses."""
        if element.id() == 0:
            return
        existing_element = self.get_existing_element(element)
        if existing_element:
            return existing_element
        new = self.file_add(element)
        self.added_elements[element.id()] = new
        self.check_inverses(element)
        subelement_queue = self.settings["library"].traverse(element, max_levels=1)[1:]
        while subelement_queue:
            subelement = subelement_queue.pop(0)
            existing_element = self.get_existing_element(subelement)
            if existing_element:
                self.added_elements[subelement.id()] = existing_element
                if not self.has_whitelisted_inverses(existing_element):
                    self.check_inverses(subelement)
            else:
                self.added_elements[subelement.id()] = self.file_add(subelement)
                self.check_inverses(subelement)
                subelement_queue.extend(self.settings["library"].traverse(subelement, max_levels=1)[1:])
        return new

    def has_whitelisted_inverses(self, element: ifcopenshell.entity_instance) -> bool:
        for source_class, attributes in self.whitelisted_inverse_attributes.items():
            if not element.is_a(source_class):
                continue
            for attribute in attributes:
                attribute_class = None
                if "." in attribute:
                    attribute, attribute_class = attribute.split(".")
                value = getattr(element, attribute, [])
                if attribute_class:
                    for subvalue in value:
                        if subvalue.is_a(attribute_class):
                            return True
                elif value:
                    return True
        return False

    def check_inverses(self, element: ifcopenshell.entity_instance) -> None:
        """Add inverse elements for the whitelisted inverse attributes."""
        for source_class, attributes in self.whitelisted_inverse_attributes.items():
            if not element.is_a(source_class):
                continue
            for attribute in attributes:
                attribute_class = None
                if "." in attribute:
                    attribute, attribute_class = attribute.split(".")
                for inverse in getattr(element, attribute, []):
                    if attribute_class and inverse.is_a(attribute_class):
                        self.add_inverse_element(inverse)
                    elif not attribute_class:
                        self.add_inverse_element(inverse)

    def add_inverse_element(self, element: ifcopenshell.entity_instance) -> None:
        """Add inverse element.

        Inverse elements are requiring different method than ``file_add``
        because they can reference many other assets that we are not
        interested in.

        E.g. a IfcRelAssociatesMaterial referencing products unrelated
        to the current asset.
        """
        # For layer assignment we don't want to add it's items
        # to avoid adding representations / items that are not related to current append_asset.
        skip_not_reused_entities_attr_i = None
        if element.is_a("IfcPresentationLayerAssignment"):
            # 3 IfcPresentationLayerAssignment.AssignedItems
            skip_not_reused_entities_attr_i = 2

        element_identity = element.wrapped_data.identity()

        # Check if inverse element was created before.
        # Still need to recreate it again - e.g. it could be some rel
        # that now needs it's RelatingObjects to be extended by the current asset.
        existing_rel = None
        if (new := self.reuse_identities.get(element_identity)) is not None:
            # Currently known cases requiring attributes reassignment are rels.
            if not new.is_a("IfcRelationship"):
                return
        elif element.is_a("IfcRelationship") and (existing_rel := self.by_guid(element.GlobalId)):
            new = existing_rel
        else:
            new = self.file.create_entity(element.is_a())
            self.reuse_identities[element_identity] = new

        for i, attribute in enumerate(element):
            new_attribute = None
            if isinstance(attribute, ifcopenshell.entity_instance):
                if not self.is_another_asset(attribute):
                    new_attribute = self.add_element(attribute)
            elif isinstance(attribute, tuple) and attribute and isinstance(attribute[0], ifcopenshell.entity_instance):
                new_attribute = []
                for item in attribute:
                    if self.is_another_asset(item):
                        continue
                    if skip_not_reused_entities_attr_i is not None and i == skip_not_reused_entities_attr_i:
                        identity = item.wrapped_data.identity()
                        if (item := self.reuse_identities.get(identity)) is None:
                            continue
                    else:
                        item = self.add_element(item)
                    new_attribute.append(item)
                # If rel exists we need to make sure previously assigned elements are untouched
                # e.g. not to assign a material or a pset from element.
                if existing_rel:
                    new_attribute.extend(existing_rel[i])
                    new_attribute = list(set(new_attribute))
            else:
                new_attribute = attribute
            if new_attribute is not None:
                new[i] = new_attribute

    def is_another_asset(self, element: ifcopenshell.entity_instance) -> bool:
        """Is IFC entity from inverse attribute is another asset to append that should be skipped."""
        if element == self.settings["element"]:
            return False
        elif element.is_a("IfcFeatureElement"):
            # Feature elements match the target class but aren't considered "assets"
            return False
        elif element.is_a("IfcRoot") and self.by_guid(element.GlobalId) is not None:
            return False
        elif element.is_a(self.target_class):
            return True
        elif self.target_class == "IfcProduct" and element.is_a("IfcTypeProduct"):
            return True
        elif self.target_class == "IfcTypeProduct" and element.is_a("IfcProduct"):
            return True
        return False

    def reuse_existing_contexts(self) -> None:
        added_contexts = set([e for e in self.added_elements.values() if e.is_a("IfcGeometricRepresentationContext")])
        added_contexts -= set(self.existing_contexts)
        for added_context in added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if not equivalent_existing_context:
                equivalent_existing_context = self.create_equivalent_context(added_context)
            for inverse in self.file.get_inverse(added_context):
                ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)

        with SafeRemovalContext(self.file, self.reuse_identities, self.assume_asset_uniqueness_by_name):
            for added_context in added_contexts:
                ifcopenshell.util.element.remove_deep2(self.file, added_context)

    def get_equivalent_existing_context(
        self, added_context: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        for context in self.existing_contexts:
            if context.is_a() != added_context.is_a():
                continue
            if context.is_a("IfcGeometricRepresentationSubContext"):
                if (
                    context.ContextType == added_context.ContextType
                    and context.ContextIdentifier == added_context.ContextIdentifier
                    and context.TargetView == added_context.TargetView
                ):
                    return context
            elif (
                context.ContextType == added_context.ContextType
                and context.ContextIdentifier == added_context.ContextIdentifier
            ):
                return context

    def create_equivalent_context(self, added_context: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        if added_context.is_a("IfcGeometricRepresentationSubContext"):
            parent = self.get_equivalent_existing_context(added_context.ParentContext)
            if not parent:
                parent = self.create_equivalent_context(added_context.ParentContext)
            return ifcopenshell.api.context.add_context(
                self.file,
                parent=parent,
                context_type=added_context.ContextType,
                context_identifier=added_context.ContextIdentifier,
                target_view=added_context.TargetView,
            )
        return ifcopenshell.api.context.add_context(
            self.file,
            context_type=added_context.ContextType,
            context_identifier=added_context.ContextIdentifier,
        )

    def file_add(
        self, element: ifcopenshell.entity_instance, conversion_factor: Optional[float] = None
    ) -> ifcopenshell.entity_instance:
        """Reimplementation of `file.add` but taking into account that some elements (profiles, materials)
        are already existing (checking by their name) and shouldn't be duplicated.

        The problem with `file.add` it's recursively adding element and all it's attributes
        and there is no control to prevent it from adding certain type of elements.
        """

        def get_conversion_factor() -> float:
            nonlocal conversion_factor
            if conversion_factor is not None:
                return conversion_factor
            library_scale = ifcopenshell.util.unit.calculate_unit_scale(self.settings["library"])
            current_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
            conversion_factor = library_scale / current_scale
            return conversion_factor

        ifc_file = self.file
        if not self.assume_asset_uniqueness_by_name or element.id() == 0:
            # file.add doesn't convert units for IfcLengthMeasure entities.
            if element.is_a("IfcLengthMeasure"):
                return ifc_file.create_entity(element.is_a(), element.wrappedValue * get_conversion_factor())
            return ifc_file.add(element)

        reuse_identities = self.reuse_identities
        element_identity = element.wrapped_data.identity()
        if added_element := reuse_identities.get(element_identity):
            return added_element

        ifc_class = element.is_a()
        attributes_ = None

        def get_attributes() -> tuple[W.attribute, ...]:
            nonlocal attributes_
            if attributes_ is not None:
                return attributes_
            attributes_ = element.wrapped_data.declaration().as_entity().all_attributes()
            return attributes_

        def get_existing_element_(
            subelement: ifcopenshell.entity_instance,
        ) -> Union[ifcopenshell.entity_instance, None]:
            # Check identity because `subelement` might not be the current `element`,
            # e.g. for IfcPersonAndOrganization.
            element_identity = subelement.wrapped_data.identity()
            if subelement_ := reuse_identities.get(element_identity):
                return subelement_

            ifc_class = subelement.is_a()
            assert ifc_class in ("IfcOrganization", "IfcPerson")
            attr_name = "Id" if ifc_file.schema == "IFC2X3" else "Identification"
            subelement_id = getattr(subelement, attr_name)

            if subelement_id is not None:
                existing_org = next(
                    (e for e in ifc_file.by_type(ifc_class) if getattr(e, attr_name) == subelement_id), None
                )
                if existing_org is not None:
                    reuse_identities[element_identity] = existing_org
                    return existing_org

        # Check if element already exists.
        # NOTE: Ensure this part is in sync with `get_existing_element`,
        # if some class is present here but not in `get_existing_element`,
        # then it might create duplicated subelements.
        if element.is_a("IfcProfileDef"):
            profile_name = element.ProfileName
            if profile_name is not None:
                existing_profile = next(
                    (e for e in ifc_file.by_type("IfcProfileDef") if e.ProfileName == profile_name), None
                )
                if existing_profile is not None:
                    reuse_identities[element_identity] = existing_profile
                    return existing_profile

        elif element.is_a("IfcMaterial"):
            material_name = element.Name
            existing_material = next((e for e in ifc_file.by_type("IfcMaterial") if e.Name == material_name), None)
            if existing_material is not None:
                reuse_identities[element_identity] = existing_material
                return existing_material

        elif element.is_a("IfcPresentationStyle"):
            style_name = element.Name
            if style_name is not None:
                existing_style = next((e for e in ifc_file.by_type(ifc_class) if e.Name == style_name), None)
                if existing_style is not None:
                    reuse_identities[element_identity] = existing_style
                    return existing_style

        elif ifc_class == "IfcApplication":
            app_id = element.ApplicationIdentifier
            if app_id is not None:
                existing_app = next(
                    (e for e in ifc_file.by_type("IfcApplication") if e.ApplicationIdentifier == app_id), None
                )
                if existing_app is not None:
                    reuse_identities[element_identity] = existing_app
                    return existing_app

        elif ifc_class == "IfcOrganization":
            existing_org = get_existing_element_(element)
            if existing_org is not None:
                reuse_identities[element_identity] = existing_org
                return existing_org

        elif ifc_class == "IfcPerson":
            existing_person = get_existing_element_(element)
            if existing_person is not None:
                reuse_identities[element_identity] = existing_person
                return existing_person

        elif ifc_class == "IfcPersonAndOrganization":
            if (person := get_existing_element_(element.ThePerson)) and (
                org := get_existing_element_(element.TheOrganization)
            ):
                for pao in ifc_file.by_type("IfcPersonAndOrganization"):
                    if pao.ThePerson == person and pao.TheOrganization == org:
                        reuse_identities[element_identity] = pao
                        return pao

        attrs: dict[int, Any] = {}

        # Utils method for the loop.
        def get_tuple_type(tuple_: tuple) -> type:
            while isinstance(tuple_, tuple):
                tuple_ = tuple_[0]
            return type(tuple_)

        def is_length_measure(attribute: W.attribute) -> bool:
            return "<type IfcLengthMeasure: <real>>" in str(attribute.type_of_attribute())

        def apply_to_array(arr: Any, func: Callable[[Any], Any]) -> Any:
            if isinstance(arr, tuple):
                return tuple(apply_to_array(sub, func) for sub in arr)
            return func(arr)

        file_add_ = partial(self.file_add, conversion_factor=conversion_factor)
        apply_conversion = lambda x: x * conversion_factor

        # Migrate attributes to another file.
        for attr_index, attr_value in enumerate(element):
            # `None` is set by default already.
            if attr_value is None:
                continue

            elif isinstance(attr_value, ifcopenshell.entity_instance):
                attr_value = file_add_(attr_value)

            elif isinstance(attr_value, tuple):
                # Assume type is consistent across the tuple.
                tuple_type = get_tuple_type(attr_value)
                if tuple_type == ifcopenshell.entity_instance:
                    attr_value = apply_to_array(attr_value, file_add_)
                elif tuple_type == float:
                    attributes = get_attributes()
                    if is_length_measure(attributes[attr_index]):
                        get_conversion_factor()  # Ensure conversion factor is not None.
                        attr_value = apply_to_array(attr_value, apply_conversion)

            elif isinstance(attr_value, float):
                attributes = get_attributes()
                if is_length_measure(attributes[attr_index]):
                    attr_value *= get_conversion_factor()

            attrs[attr_index] = attr_value

        # Adding entity at the end just to keep it consistent with `file.add`.
        new = ifc_file.create_entity(ifc_class)
        reuse_identities[element_identity] = new
        for attr_index, attr_value in attrs.items():
            new[attr_index] = attr_value

        return new
