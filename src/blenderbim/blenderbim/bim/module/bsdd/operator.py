# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import bsdd
import json
import ifcopenshell
import blenderbim.tool as tool


class LoadBSDDDomains(bpy.types.Operator):
    bl_idname = "bim.load_bsdd_domains"
    bl_label = "Load bSDD Domains"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMBSDDProperties
        props.domains.clear()
        client = bsdd.Client()

        if props.load_preview_domains:
            domains = client.Domain()
        else:
            domains = [d for d in client.Domain() if d["status"] == "Active"]

        for domain in sorted(domains, key=lambda x: x["name"]):
            new = props.domains.add()
            new.name = domain["name"]
            new.namespace_uri = domain["namespaceUri"]
            new.default_language_code = domain["defaultLanguageCode"]
            new.organization_name_owner = domain["organizationNameOwner"]
            new.status = domain["status"]
            new.version = domain["version"]
        return {"FINISHED"}


class SetActiveBSDDDomain(bpy.types.Operator):
    bl_idname = "bim.set_active_bsdd_domain"
    bl_label = "Load bSDD Domains"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    uri: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMBSDDProperties
        props.active_domain = self.name
        props.active_uri = self.uri
        return {"FINISHED"}


class SearchBSDDClassifications(bpy.types.Operator):
    bl_idname = "bim.search_bsdd_classifications"
    bl_label = "Search bSDD Classifications"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMBSDDProperties
        props.classifications.clear()
        client = bsdd.Client()
        related_ifc_entities = []
        if len(props.keyword) < 3:
            return {"FINISHED"}
        if props.should_filter_ifc_class and context.active_object:
            element = tool.Ifc.get_entity(context.active_object)
            if element:
                related_ifc_entities = [element.is_a()]
        results = client.ClassificationSearchOpen(props.keyword, DomainNamespaceUris=[props.active_uri], RelatedIfcEntities=related_ifc_entities)
        for result in sorted(results["classifications"], key=lambda x: x["referenceCode"]):
            new = props.classifications.add()
            new.name = result["name"]
            new.reference_code = result["referenceCode"]
            new.description = result.get("description", "")
            new.namespace_uri = result["namespaceUri"]
            new.domain_name = result["domainName"]
            new.domain_namespace_uri = result["domainNamespaceUri"]
        return {"FINISHED"}


class GetBSDDClassificationProperties(bpy.types.Operator):
    bl_idname = "bim.get_bsdd_classification_properties"
    bl_label = "Search bSDD Classifications"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bprops = context.scene.BIMBSDDProperties
        bprops.classification_psets.clear()
        bsdd_classification = bprops.classifications[bprops.active_classification_index]
        client = bsdd.Client()
        data = client.Classification(bsdd_classification.namespace_uri)

        properties = data.get("classificationProperties", None)
        if not properties:
            return {"FINISHED"}

        psets = {}

        for prop in properties:
            if prop.get("propertyDomainName") != "IFC":
                continue
            pset = prop.get("propertySet", None)
            if not pset:
                continue
            psets.setdefault(pset, {})

            predefined_value = prop.get("predefinedValue")
            if predefined_value:
                possible_values = [predefined_value]
            else:
                possible_values = prop.get("possibleValues", []) or []
                possible_values = [v["value"] for v in possible_values]

            psets[pset][prop["name"]] = {"data_type": prop["dataType"], "possible_values": possible_values}

        data_type_map = {
            "String": "string",
            "Real": "float",
            "Boolean": "boolean",
        }

        for pset_name, pset in psets.items():
            new = bprops.classification_psets.add()
            new.name = pset_name
            for name, data in pset.items():
                new2 = new.properties.add()
                new2.name = name
                if data["possible_values"]:
                    new2.enum_items = json.dumps(data["possible_values"])
                    new2.data_type = "enum"
                else:
                    new2.data_type = data_type_map[data["data_type"]]
        return {"FINISHED"}
