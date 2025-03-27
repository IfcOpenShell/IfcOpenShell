# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.owner
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.style
import ifcopenshell.api.unit
import ifcopenshell.util.schema
import ifcopenshell.util.shape_builder
import bonsai.tool as tool
from pathlib import Path


def sync_guids(target_file: ifcopenshell.file, source_file: ifcopenshell.file) -> None:

    def sync_guid(element: ifcopenshell.entity_instance) -> None:
        """Try to sync `element` guid with `source_file`.

        Sync is assigning guid based on the first element from `source_file` that has a matching type and name.
        """

        # In IFC2X3 IfcProject is not IfcContext.
        if element.is_a("IfcTypeProduct") or element.is_a("IfcContext") or element.is_a("IfcProject"):
            assert element.Name, element
            elements = source_file.by_type(element.is_a(), False)
            for element_ in elements:
                if element.Name == element_.Name:
                    element.GlobalId = element_.GlobalId
                    return
        print(
            f"WARNING! Couldn't find a matching element in the GUID source to sync guid for '{element.Name}' ({element})."
        )

    def sync_pset(pset: ifcopenshell.entity_instance) -> None:
        element_types = pset.DefinesType
        assert len(element_types) == 1
        element_type: ifcopenshell.entity_instance = element_types[0]
        try:
            element_type_ = source_file.by_guid(element_type.GlobalId)
        except RuntimeError:
            # New type with pset was added.
            print(f"WARNING! Couldn't find a matching pset for '{pset.Name}' ({pset}).")
            return
        assert len(element_type_.HasPropertySets) == 1
        pset_ = element_type_.HasPropertySets[0]
        assert pset.Name == pset_.Name
        pset.GlobalId = pset_.GlobalId

    def sync_rel(rel: ifcopenshell.entity_instance) -> None:
        if rel.is_a("IfcRelAssociatesMaterial"):
            related_objects = rel.RelatedObjects
            assert len(related_objects) == 1
            related_object = related_objects[0]
            try:
                related_object_ = source_file.by_guid(related_object.GlobalId)
            except RuntimeError:
                # New type with material was added.
                print(f"WARNING! Couldn't find a matching rel for '{rel}'.")
                return
            rel_ = next((r for r in related_object_.HasAssociations if r.is_a("IfcRelAssociatesMaterial")))
            assert rel_
            rel.GlobalId = rel_.GlobalId
        elif rel.is_a("IfcRelDeclares"):
            context = rel.RelatingContext
            try:
                context_ = source_file.by_guid(context.GlobalId)
            except RuntimeError:
                # New context was added.
                print(f"WARNING! Couldn't find a matching context for '{context}'.")
                return
            rel_ = context_.Declares[0]
            rel.GlobalId = rel_.GlobalId
        else:
            print(f"WARNING! Couldn't find a matching element in the GUID source to sync guid for '{rel}'.")

    roots = target_file.by_type("IfcRoot")
    psets: list[ifcopenshell.entity_instance] = []
    rels: list[ifcopenshell.entity_instance] = []
    for element in roots:
        if element.is_a("IfcPropertySet"):
            psets.append(element)
            continue
        elif element.is_a("IfcRelationship"):
            rels.append(element)
            continue
        sync_guid(element)

    for rel in rels:
        sync_rel(rel)

    for pset in psets:
        sync_pset(pset)


class LibraryGenerator:
    output_filename = "Demo Library.ifc"

    guid_source: ifcopenshell.file
    """Guid sync is needed to avoid unnecessary diffs
    and to avoid `append_asset` from identifying existing elements and as new ones.
    """

    def generate(self, schema: ifcopenshell.util.schema.IFC_SCHEMA) -> None:
        assert bpy.context.blend_data
        opened_blend_file = Path(bpy.context.blend_data.filepath)
        assert (
            opened_blend_file.name == "demo-library.blend"
        ), "This script must be run from the demo-library.blend file as it's using Blender objects to create representations."
        libraries_path = opened_blend_file.parent.parent / "bonsai" / "bim" / "data" / "libraries"

        guid_source_filepath = libraries_path / f"{schema} {self.output_filename}"
        self.guid_source = ifcopenshell.open(guid_source_filepath)

        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.file = ifcopenshell.api.project.create_file(schema)
        self.builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)

        if schema == "IFC2X3":
            ifcopenshell.api.owner.settings.factory_reset()
            person = ifcopenshell.api.owner.add_person(self.file)
            organization = ifcopenshell.api.owner.add_organisation(self.file)
            user = ifcopenshell.api.owner.add_person_and_organisation(
                self.file, person=person, organisation=organization
            )
            application = ifcopenshell.api.owner.add_application(
                self.file, application_full_name="Bonsai", application_identifier="Bonsai"
            )
            ifcopenshell.api.owner.settings.get_user = lambda x: user
            ifcopenshell.api.owner.settings.get_application = lambda x: application

        # Basic project setup.
        self.project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Bonsai Demo")

        if schema != "IFC2X3":
            self.library = ifcopenshell.api.root.create_entity(
                self.file, ifc_class="IfcProjectLibrary", name="Bonsai Demo Library"
            )
            ifcopenshell.api.project.assign_declaration(
                self.file, definitions=[self.library], relating_context=self.project
            )
        ifcopenshell.api.unit.assign_unit(self.file, length={"is_metric": True, "raw": "METERS"})
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        plan = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        self.representations = {
            "model_body": ifcopenshell.api.context.add_context(
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=model,
            ),
            "plan_body": ifcopenshell.api.context.add_context(
                self.file,
                context_type="Plan",
                context_identifier="Body",
                target_view="PLAN_VIEW",
                parent=plan,
            ),
            "model_annotation": ifcopenshell.api.context.add_context(
                self.file,
                context_type="Model",
                context_identifier="Annotation",
                target_view="MODEL_VIEW",
                parent=plan,
            ),
        }

        self.material = ifcopenshell.api.material.add_material(self.file, name="Unknown")

        # IfcWallType.
        self.create_layer_type("IfcWallType", "WAL50", 0.05)
        self.create_layer_type("IfcWallType", "WAL100", 0.1)
        self.create_layer_type("IfcWallType", "WAL200", 0.2)
        self.create_layer_type("IfcWallType", "WAL300", 0.3)

        # IfcCoveringType.
        self.create_layer_type("IfcCoveringType", "COV10", 0.01)

        product = self.create_layer_type("IfcCoveringType", "COV20", 0.02)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=product, name="EPset_Parametric")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"LayerSetDirection": "AXIS2"})

        product = self.create_layer_type("IfcCoveringType", "COV30", 0.03)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=product, name="EPset_Parametric")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"LayerSetDirection": "AXIS3"})

        if schema != "IFC2X3":
            self.create_layer_type("IfcRampType", "RAM200", 0.2)

            profile = self.file.create_entity("IfcCircleProfileDef", ProfileType="AREA", Radius=0.3)
            self.create_profile_type("IfcPileType", "P1", profile)

        self.create_layer_type("IfcSlabType", "FLR200", 0.2)
        self.create_layer_type("IfcSlabType", "FLR300", 0.3)

        if schema != "IFC2X3":
            # No profile sets in IFC2X3 :(
            profile = self.file.create_entity(
                "IfcRectangleProfileDef", ProfileName="500x600", ProfileType="AREA", XDim=0.5, YDim=0.6
            )
            self.create_profile_type("IfcColumnType", "C1", profile)

            profile = self.file.create_entity(
                "IfcCircleHollowProfileDef",
                ProfileName="500.0x5.0 CHS",
                ProfileType="AREA",
                Radius=0.25,
                WallThickness=0.005,
            )
            self.create_profile_type("IfcColumnType", "C2", profile)

            profile = self.file.create_entity(
                "IfcRectangleHollowProfileDef",
                ProfileName="150x75x2.0 RHS",
                ProfileType="AREA",
                XDim=0.075,
                YDim=0.15,
                WallThickness=0.002,
                InnerFilletRadius=0.005,
                OuterFilletRadius=0.005,
            )
            self.create_profile_type("IfcColumnType", "C3", profile)

            profile = self.file.create_entity(
                "IfcIShapeProfileDef",
                ProfileName="DEMO-I",
                ProfileType="AREA",
                OverallWidth=0.1,
                OverallDepth=0.2,
                WebThickness=0.005,
                FlangeThickness=0.01,
                FilletRadius=0.005,
            )
            self.create_profile_type("IfcBeamType", "B1", profile)

            profile = self.file.create_entity(
                "IfcCShapeProfileDef",
                ProfileName="DEMO-C",
                ProfileType="AREA",
                Depth=0.2,
                Width=0.1,
                WallThickness=0.0015,
                Girth=0.03,
                InternalFilletRadius=0.005,
            )
            self.create_profile_type("IfcBeamType", "B2", profile)

        self.create_type(
            "IfcWindowType" if schema != "IFC2X3" else "IfcWindowStyle",
            "WT01",
            {"model_body": "Window", "plan_body": "Window-Plan"},
        )
        self.create_type(
            "IfcDoorType" if schema != "IFC2X3" else "IfcDoorStyle",
            "DT01",
            {"model_body": "Door", "plan_body": "Door-Plan"},
        )
        self.create_type("IfcFurnitureType", "BUN01", {"model_body": "Bunny", "plan_body": "Bunny-Plan"})

        # IfcAnnotation types.
        self.create_symbol_type("SETOUT-POINT", "setout-point")
        self.create_symbol_type("CONTROL-POINT", "control-point")
        self.create_symbol_type("TRAVERSE-POINT", "traverse-point")

        self.create_line_type("DASHED", "dashed")
        self.create_line_type("FINE", "fine")
        self.create_line_type("THIN", "thin")
        self.create_line_type("MEDIUM", "medium")
        self.create_line_type("THICK", "thick")
        self.create_line_type("STRONG", "strong")

        self.create_text_type(
            "SETOUT-TAG", "setout-tag", ["E ``round({{easting}}, 0.001)``", "N ``round({{northing}}, 0.001)``"]
        )
        self.create_text_type("DOOR-TAG", "door-tag", ["{{type.Name}}", "{{Name}}"])
        self.create_text_type("WINDOW-TAG", "window-tag", ["{{Name}}"])
        self.create_text_type(
            "SPACE-TAG",
            "space-tag",
            ["{{Name}}", "{{Description}}", "``round({{Qto_SpaceBaseQuantities.NetFloorArea}}, 0.01)``"],
        )
        self.create_text_type("MATERIAL-TAG", "rectangle-tag", ["{{material.Name}}"])
        self.create_text_type("TYPE-TAG", "capsule-tag", ["{{type.Name}}"])
        self.create_text_type("NAME-TAG", "capsule-tag", ["{{Name}}"])

        sync_guids(self.file, self.guid_source)
        self.file.write(libraries_path / f"{self.file.schema} {self.output_filename}")

        if schema == "IFC2X3":
            ifcopenshell.api.owner.settings.restore()

    def create_symbol_type(self, name: str, symbol: str) -> None:
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTypeProduct", name=name)
        element.ApplicableOccurrence = "IfcAnnotation/SYMBOL"
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Symbol": symbol})

    def create_line_type(self, name: str, classes: str) -> None:
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTypeProduct", name=name)
        element.ApplicableOccurrence = "IfcAnnotation/LINEWORK"
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Classes": classes})

    def create_text_type(self, name: str, symbol: str, literals: list[str]) -> None:
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTypeProduct", name=name)
        element.ApplicableOccurrence = "IfcAnnotation/TEXT"
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Symbol": symbol})
        items: list[ifcopenshell.entity_instance] = []
        for literal in literals:
            origin = self.builder.create_axis2_placement_3d()
            items.append(
                self.file.create_entity(
                    "IfcTextLiteralWithExtent",
                    literal,
                    origin,
                    "RIGHT",
                    self.file.create_entity("IfcPlanarExtent", 1000, 1000),
                    "center",
                ),
            )

        representation = self.file.create_entity(
            "IfcShapeRepresentation",
            self.representations["model_annotation"],
            self.representations["model_annotation"].ContextIdentifier,
            "Annotation2D",
            items,
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=representation)

    def create_layer_type(self, ifc_class: str, name: str, thickness: float) -> ifcopenshell.entity_instance:
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialLayerSet")
        assert isinstance(rel, ifcopenshell.entity_instance)
        layer_set = rel.RelatingMaterial
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=layer_set, material=self.material)
        layer.LayerThickness = thickness
        if self.file.schema != "IFC2X3":
            ifcopenshell.api.project.assign_declaration(self.file, definitions=[element], relating_context=self.library)
        return element

    def create_profile_type(self, ifc_class: str, name: str, profile: ifcopenshell.entity_instance) -> None:
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class=ifc_class, name=name)
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialProfileSet")
        assert isinstance(rel, ifcopenshell.entity_instance)
        profile_set = rel.RelatingMaterial
        material_profile = ifcopenshell.api.material.add_profile(
            self.file, profile_set=profile_set, material=self.material
        )
        ifcopenshell.api.material.assign_profile(self.file, material_profile=material_profile, profile=profile)
        if self.file.schema != "IFC2X3":
            ifcopenshell.api.project.assign_declaration(self.file, definitions=[element], relating_context=self.library)

    def create_type(self, ifc_class: str, name: str, representations: dict[str, str]) -> None:
        """ "
        :param representations: Mapping of representation contexts to Blender objects names to be used
            as a representation source.
        """
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class=ifc_class, name=name)
        for rep_name, obj_name in representations.items():
            obj = bpy.data.objects[obj_name]
            assert isinstance(obj.data, bpy.types.Mesh)
            representation = ifcopenshell.api.geometry.add_representation(
                self.file,
                context=self.representations[rep_name],
                blender_object=obj,
                geometry=obj.data,
                total_items=max(1, len(obj.material_slots)),
            )
            assert representation
            styles: list[ifcopenshell.entity_instance] = []
            for slot in obj.material_slots:
                material = slot.material
                assert material
                style = ifcopenshell.api.style.add_style(self.file, name=material.name)
                attributes = tool.Style.get_surface_shading_attributes(material)
                if self.file.schema == "IFC2X3":
                    del attributes["Transparency"]
                ifcopenshell.api.style.add_surface_style(
                    self.file,
                    style=style,
                    ifc_class="IfcSurfaceStyleShading",
                    attributes=attributes,
                )
                styles.append(style)
            if styles:
                ifcopenshell.api.style.assign_representation_styles(
                    self.file, shape_representation=representation, styles=styles
                )
            ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=representation)

        if self.file.schema != "IFC2X3":
            ifcopenshell.api.project.assign_declaration(self.file, definitions=[element], relating_context=self.library)


if __name__ == "__main__":
    LibraryGenerator().generate("IFC2X3")
    LibraryGenerator().generate("IFC4")
    LibraryGenerator().generate("IFC4X3")
