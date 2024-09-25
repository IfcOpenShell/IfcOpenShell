# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020-2022 Dion Moult <dion@thinkmoult.com>
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
import json
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.classification
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.bim.helper
from bonsai.bim.ifc import IfcStore


class LoadClassificationLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_classification_library"
    bl_label = "Load Classification Library"
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def _execute(self, context):
        IfcStore.classification_file = ifcopenshell.open(self.filepath)


class AddClassification(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_classification"
    bl_label = "Add Classification"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMClassificationProperties
        ifcopenshell.api.run(
            "classification.add_classification",
            tool.Ifc.get(),
            classification=IfcStore.classification_file.by_id(int(props.available_classifications)),
        )


class AddManualClassification(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_manual_classification"
    bl_label = "Add Manual Classification"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMClassificationProperties
        attributes = bonsai.bim.helper.export_attributes(props.classification_attributes)
        classification = ifcopenshell.api.run(
            "classification.add_classification", tool.Ifc.get(), classification="Unnamed"
        )
        ifcopenshell.api.run(
            "classification.edit_classification", tool.Ifc.get(), classification=classification, attributes=attributes
        )
        props.is_adding = False


class AddManualClassificationReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_manual_classification_reference"
    bl_label = "Add Manual Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        if self.obj_type == "Object":
            if context.selected_objects:
                objects = [o.name for o in context.selected_objects]
            else:
                objects = [context.active_object.name]
        else:
            objects = [self.obj]
        props = context.scene.BIMClassificationReferenceProperties
        attributes = bonsai.bim.helper.export_attributes(props.reference_attributes)
        products = [
            tool.Ifc.get().by_id(ifc_definition_id)
            for obj in objects
            if (ifc_definition_id := tool.Blender.get_obj_ifc_definition_id(obj, self.obj_type, context))
        ]
        if products:
            classification = tool.Ifc.get().by_id(int(props.classifications))
            reference = ifcopenshell.api.run(
                "classification.add_reference",
                tool.Ifc.get(),
                products=products,
                classification=classification,
                identification="X",
                name="Unnamed",
            )
            ifcopenshell.api.run(
                "classification.edit_reference", tool.Ifc.get(), reference=reference, attributes=attributes
            )
        props.is_adding = False


class AddClassificationFromBSDD(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_classification_from_bsdd"
    bl_label = "Add Classification From bSDD"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMBSDDProperties
        domain = next((d for d in props.domains if d.name == props.active_domain and d.uri == props.active_uri), None)

        # Maybe user loaded preview domains, set it as active
        # and then reloaded them without preview domains.
        if not domain:
            self.report(
                {"INFO"},
                f"Couldn't find domain '{props.active_domain}' ({props.active_uri}). Try to reload bSDD dictionaries.",
            )
            return

        for element in tool.Ifc.get().by_type("IfcClassification"):
            if element.Name == props.active_domain or (tool.Classification.get_location(element) == domain.uri):
                self.report({"INFO"}, f"Classification '{props.active_domain}' is already added to the project.")
                return

        classification = ifcopenshell.api.run(
            "classification.add_classification", tool.Ifc.get(), classification=props.active_domain
        )
        classification.Source = domain.organization_name_owner
        classification.Edition = domain.version
        tool.Classification.set_location(classification, domain.uri)


class EnableAddingManualClassification(bpy.types.Operator):
    bl_idname = "bim.enable_adding_manual_classification"
    bl_label = "Enable Adding Manual Classification"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        props.is_adding = True
        props.active_classification_id = 0
        props.classification_attributes.clear()
        bonsai.bim.helper.import_attributes2("IfcClassification", props.classification_attributes)
        return {"FINISHED"}


class DisableAddingManualClassification(bpy.types.Operator):
    bl_idname = "bim.disable_adding_manual_classification"
    bl_label = "Disable Adding Manual Classification"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        props.is_adding = False
        return {"FINISHED"}


class EnableAddingManualClassificationReference(bpy.types.Operator):
    bl_idname = "bim.enable_adding_manual_classification_reference"
    bl_label = "Enable Adding Manual Classification Reference"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMClassificationReferenceProperties
        props.is_adding = True
        props.reference_attributes.clear()
        bonsai.bim.helper.import_attributes2("IfcClassificationReference", props.reference_attributes)
        return {"FINISHED"}


class DisableAddingManualClassificationReference(bpy.types.Operator):
    bl_idname = "bim.disable_adding_manual_classification_reference"
    bl_label = "Disable Adding Manual Classification Reference"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMClassificationReferenceProperties
        props.is_adding = False
        return {"FINISHED"}


class EnableEditingClassification(bpy.types.Operator):
    bl_idname = "bim.enable_editing_classification"
    bl_label = "Enable Editing Classification"
    bl_options = {"REGISTER", "UNDO"}
    classification: bpy.props.IntProperty()

    def execute(self, context):
        def callback(name, prop, data):
            if name == "ReferenceTokens":
                new = bpy.context.scene.BIMGeoreferenceProperties.projected_crs.add()
                new.name = name
                new.data_type = "string"
                new.is_null = data[name] is None
                new.is_optional = True
                new.string_value = "" if new.is_null else json.dumps(data[name])
                return True

        props = context.scene.BIMClassificationProperties
        props.classification_attributes.clear()
        bonsai.bim.helper.import_attributes2(
            tool.Ifc.get().by_id(self.classification), props.classification_attributes, callback
        )
        props.active_classification_id = self.classification
        return {"FINISHED"}


class DisableEditingClassification(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification"
    bl_label = "Disable Editing Classification"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMClassificationProperties.active_classification_id = 0
        return {"FINISHED"}


class RemoveClassification(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_classification"
    bl_label = "Remove Classification"
    bl_description = (
        "The classification and all of its relationships, children references, "
        "and relationships between objects and child references will be completely removed from a project"
    )
    bl_options = {"REGISTER", "UNDO"}
    classification: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "classification.remove_classification",
            tool.Ifc.get(),
            classification=self.file.by_id(self.classification),
        )


class EditClassification(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_classification"
    bl_label = "Edit Classification"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMClassificationProperties
        attributes = {}
        for attribute in props.classification_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            elif attribute.name == "ReferenceTokens":
                attributes[attribute.name] = json.loads(attribute.string_value)
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "classification.edit_classification",
            self.file,
            **{"classification": self.file.by_id(props.active_classification_id), "attributes": attributes},
        )
        bpy.ops.bim.disable_editing_classification()


class EnableEditingClassificationReference(bpy.types.Operator):
    bl_idname = "bim.enable_editing_classification_reference"
    bl_label = "Enable Editing Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMClassificationReferenceProperties
        props.reference_attributes.clear()
        bonsai.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.reference), props.reference_attributes)
        props.active_reference_id = self.reference
        return {"FINISHED"}


class DisableEditingClassificationReference(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification_reference"
    bl_label = "Disable Editing Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.BIMClassificationReferenceProperties.active_reference_id = 0
        return {"FINISHED"}


class RemoveClassificationReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_classification_reference"
    bl_label = "Remove Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        if self.obj_type == "Object":
            if context.selected_objects:
                objects = [o.name for o in context.selected_objects]
            else:
                objects = [context.active_object.name]
        else:
            objects = [self.obj]

        active_reference = tool.Ifc.get().by_id(self.reference)
        identification = active_reference[1]

        elements_by_references: dict[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]] = {}
        for obj in objects:
            ifc_definition_id = tool.Blender.get_obj_ifc_definition_id(obj, self.obj_type, context)
            element = tool.Ifc.get().by_id(ifc_definition_id)
            references = ifcopenshell.util.classification.get_references(element, should_inherit=False)
            for reference in references:
                if (identification and reference[1] == identification) or (
                    not identification and reference == active_reference
                ):
                    elements_by_references.setdefault(reference, []).append(element)

        if elements_by_references:
            for reference, products in elements_by_references.items():
                ifcopenshell.api.run(
                    "classification.remove_reference",
                    tool.Ifc.get(),
                    reference=reference,
                    products=products,
                )


class EditClassificationReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_classification_reference"
    bl_label = "Edit Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMClassificationReferenceProperties
        attributes = {}
        for attribute in props.reference_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "classification.edit_reference",
            self.file,
            reference=self.file.by_id(props.active_reference_id),
            attributes=attributes,
        )
        bpy.ops.bim.disable_editing_classification_reference()


class AddClassificationReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_classification_reference"
    bl_label = "Add Classification Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        if self.obj_type == "Object":
            if context.selected_objects:
                objects = [o.name for o in context.selected_objects]
            else:
                objects = [context.active_object.name]
        else:
            objects = [self.obj]
        props = context.scene.BIMClassificationProperties
        classification = None
        classification_name = IfcStore.classification_file.by_id(int(props.available_classifications)).Name
        for element in tool.Ifc.get().by_type("IfcClassification"):
            if element.Name == classification_name:
                classification = element
                break

        products = [
            tool.Ifc.get().by_id(ifc_definition_id)
            for obj in objects
            if (ifc_definition_id := tool.Blender.get_obj_ifc_definition_id(obj, self.obj_type, context))
        ]
        if products:
            ifcopenshell.api.run(
                "classification.add_reference",
                tool.Ifc.get(),
                reference=IfcStore.classification_file.by_id(self.reference),
                products=products,
                classification=classification,
            )


class AddClassificationReferenceFromBSDD(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_classification_reference_from_bsdd"
    bl_label = "Add Classification Reference From bSDD"
    bl_description = (
        "Add classification reference from BSDD to the selected objects. "
        "If class properties are loaded, they also will be assigned as psets/qsets"
    )
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        if self.obj_type == "Object":
            if context.selected_objects:
                objects = [o.name for o in context.selected_objects]
            else:
                objects = [context.active_object.name]
        else:
            objects = [self.obj]
        props = context.scene.BIMClassificationProperties
        bprops = context.scene.BIMBSDDProperties
        use_only_ifc_properties: bool = bprops.use_only_ifc_properties

        bsdd_classification = bprops.classifications[bprops.active_classification_index]

        classification = None
        for element in tool.Ifc.get().by_type("IfcClassification"):
            if element.Name == bsdd_classification.domain_name or (
                tool.Classification.get_location(element) == bsdd_classification.domain_namespace_uri
            ):
                classification = element
                break

        if not classification:
            classification = ifcopenshell.api.run(
                "classification.add_classification", tool.Ifc.get(), classification=bsdd_classification.domain_name
            )
            tool.Classification.set_location(classification, bsdd_classification.domain_namespace_uri)

        for obj in objects:
            ifc_definition_id = tool.Blender.get_obj_ifc_definition_id(obj, self.obj_type, context)
            if not ifc_definition_id:
                continue
            element = tool.Ifc.get().by_id(ifc_definition_id)
            reference = ifcopenshell.api.run(
                "classification.add_reference",
                tool.Ifc.get(),
                products=[element],
                classification=classification,
                identification=bsdd_classification.reference_code,
                name=bsdd_classification.name,
            )
            reference.Location = bsdd_classification.uri

            for classification_pset in bprops.classification_psets:
                properties = {}

                blender_properties = classification_pset.properties
                if use_only_ifc_properties:
                    blender_properties = [p for p in blender_properties if p.metadata == "IFC"]

                for prop in blender_properties:
                    properties[prop.name] = prop.get_value()

                if classification_pset.name == "undefined_set":
                    if "ObjectType" in properties:
                        if hasattr(element, "ObjectType"):
                            element.ObjectType = properties["ObjectType"]
                        del properties["ObjectType"]
                if not properties:
                    continue

                is_pset = not classification_pset.name.startswith("Qto_")

                if is_pset:
                    pset = ifcopenshell.util.element.get_pset(element, classification_pset.name, psets_only=True)
                else:
                    pset = ifcopenshell.util.element.get_pset(element, classification_pset.name, qtos_only=True)

                if pset:
                    pset = tool.Ifc.get().by_id(pset["id"])
                elif is_pset:
                    pset = ifcopenshell.api.run(
                        "pset.add_pset", tool.Ifc.get(), product=element, name=classification_pset.name
                    )
                else:
                    pset = ifcopenshell.api.run(
                        "pset.add_qto", tool.Ifc.get(), product=element, name=classification_pset.name
                    )

                if is_pset:
                    ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties=properties)
                else:
                    ifcopenshell.api.run("pset.edit_qto", tool.Ifc.get(), qto=pset, properties=properties)


class ChangeClassificationLevel(bpy.types.Operator):
    bl_idname = "bim.change_classification_level"
    bl_label = "Change Classification Level"
    bl_options = {"REGISTER", "UNDO"}
    parent_id: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        props.available_library_references.clear()
        for reference in IfcStore.classification_file.by_id(self.parent_id).HasReferences:
            new = props.available_library_references.add()
            new.identification = reference.Identification or ""
            new.name = reference.Name or ""
            new.ifc_definition_id = reference.id()
            new.has_references = bool(reference.HasReferences)
            new.referenced_source
        if reference.ReferencedSource.is_a("IfcClassificationReference"):
            props.active_library_referenced_source = reference.ReferencedSource.ReferencedSource.id()
        else:
            props.active_library_referenced_source = 0
        return {"FINISHED"}


class DisableEditingClassificationReferences(bpy.types.Operator):
    bl_idname = "bim.disable_editing_classification_references"
    bl_label = "Disable Editing Classification References"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMClassificationProperties
        props.available_library_references.clear()
        return {"FINISHED"}
