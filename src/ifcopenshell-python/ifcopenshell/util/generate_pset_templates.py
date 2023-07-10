# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 @Andrej730
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

RUN_FROM_DEV_REPO = False

import ifcopenshell.api
import ifcopenshell.util.attribute
from pathlib import Path
from lxml import etree
import glob
import sys

if not RUN_FROM_DEV_REPO:
    import zipfile
    import shutil

BASE_MODULE_PATH = Path(__file__).parent
IFC4x3_HTML_LOCATION = BASE_MODULE_PATH / "IFC4.3-html-iso-release"

if not RUN_FROM_DEV_REPO:
    IFC4x3_OUTPUT_PATH = BASE_MODULE_PATH / "schema/Pset_IFC4X3.ifc"
else:
    IFC4x3_PSD_LOCATION = BASE_MODULE_PATH / "../output/psd"
    try:
        IFC4x3_OUTPUT_PATH = sys.argv[1]
    except:
        IFC4x3_OUTPUT_PATH = BASE_MODULE_PATH / "../output/Pset_IFC4X3.ifc"

IFC2x3_HTML_ZIP_LOCATION = BASE_MODULE_PATH / "IFC2x3_TC1_HTML_distribution-pset_errata.zip"
IFC2x3_OUTPUT_PATH = BASE_MODULE_PATH / "schema/Pset_IFC2X3.ifc"

PROPERTY_TYPES_DICT = {
    "TypePropertySingleValue": ("P_SINGLEVALUE", "type"),
    # in IFC2X3 weirdly xmls have TypeSimpleProperty
    # no difference with TypePropertySingleValue though
    "TypeSimpleProperty": ("P_SINGLEVALUE", "type"),
    "TypePropertyListValue": ("P_LISTVALUE", "type"),
    "TypePropertyBoundedValue": ("P_BOUNDEDVALUE", "type"),
    "TypePropertyReferenceValue": ("P_REFERENCEVALUE", "reftype"),
    "TypePropertyEnumeratedValue": ("P_ENUMERATEDVALUE", ""),
    "TypePropertyTableValue": ("P_TABLEVALUE", "type"),
    "TypeComplexProperty": ("P_COMPLEX", ""),
}


class PsetTemplatesGenerator:
    def parse_ifc4x3_data(self):
        print("Starting parsing data for IFC4X3...")

        if not RUN_FROM_DEV_REPO:
            if not IFC4x3_HTML_LOCATION.is_dir():
                raise Exception(
                    f'ISO release for Ifc4.3.0.1 expected to be in folder "{IFC4x3_HTML_LOCATION.resolve()}\\"\n'
                    "For generating ifc pset library please either setup docs as described above \n"
                    "or change IFC4x3_HTML_LOCATION in the script accordingly.\n"
                    "You can download docs from the repository: \n"
                    "https://github.com/buildingSMART/IFC4.3-html/releases/tag/sep-13-release"
                )
            # unzip the data
            if not RUN_FROM_DEV_REPO:
                pset_data_zip = IFC4x3_HTML_LOCATION / "IFC/RELEASE/IFC4x3/HTML/annex-a-psd.zip"
                pset_data_location = BASE_MODULE_PATH / "temp/annex-a-psd"
                with zipfile.ZipFile(pset_data_zip, "r") as fi_zip:
                    fi_zip.extractall(pset_data_location)
        else:
            if not IFC4x3_PSD_LOCATION.is_dir():
                raise Exception(
                    f'Psets xmls files expected to be in folder "{IFC4x3_PSD_LOCATION.resolve()}\\"\n'
                    "For generating ifc pset library please either setup docs as described above \n"
                    "or change IFC4x3_PSD_LOCATION in the script accordingly."
                )
            pset_data_location = IFC4x3_PSD_LOCATION

        pset_data_glob = f"{pset_data_location}/*.xml"
        self.parse_psets_data("IFC4X3", pset_data_glob, "IFC4X3 Property Set Templates", str(IFC4x3_OUTPUT_PATH))

        if not RUN_FROM_DEV_REPO:
            shutil.rmtree(pset_data_location)

    def parse_ifc2x3_data(self):
        print("Starting parsing data for IFC2X3...")
        if not IFC2x3_HTML_ZIP_LOCATION.is_file():
            raise Exception(
                f'ISO release for IFC2x3 TC1 expected to be in folder "{IFC2x3_HTML_ZIP_LOCATION.resolve()}\\"\n'
                "For doc extraction please either setup docs as described above \n"
                "or change IFC2x3_HTML_LOCATION in the script accordingly.\n"
                "You can download docs from the url: \n"
                "https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/IFC2x3_TC1_HTML_distribution-pset_errata.zip"
            )

        # unzip the data
        pset_data_location = BASE_MODULE_PATH / "temp/ifc2x3_html"
        with zipfile.ZipFile(IFC2x3_HTML_ZIP_LOCATION, "r") as fi_zip:
            fi_zip.extractall(pset_data_location)

        pset_data_glob = f"{pset_data_location}/**/pset*.xml"
        # we're using IFC4X3 since IfcPropertySetTemplate and IfcRelDeclares
        # are not available in IFC2X3
        self.parse_psets_data("IFC4X3", pset_data_glob, "IFC2X3 Property Set Templates", str(IFC2x3_OUTPUT_PATH))
        shutil.rmtree(pset_data_location)

    def ifc_entity(self, entity_name, **kwargs):
        entity = self.ifc_file.create_entity(entity_name, **kwargs)
        return entity

    def parse_psets_data(self, schema_name, pset_data_glob, project_name, ifc_output_path):
        schema_name = schema_name.upper()
        self.ifc_file = ifcopenshell.api.run("project.create_file", version=schema_name)
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name)

        self.ifc_derived_unit_enum = (
            schema.declaration_by_name("IfcDerivedUnitEnum").as_enumeration_type().enumeration_items()
        )
        self.ifc_unit_enum = schema.declaration_by_name("IfcUnitEnum").as_enumeration_type().enumeration_items()

        project = self.ifc_entity("IfcProject", Name=project_name, GlobalId=ifcopenshell.guid.new())
        psets_list = []
        if schema_name == "IFC2X3":
            rel = None
        else:
            rel = self.ifc_entity(
                "IfcRelDeclares",
                RelatedDefinitions=psets_list,
                RelatingContext=project,
                GlobalId=ifcopenshell.guid.new(),
            )

        # in IFC4 there is also
        # IFCLIBRARYREFERENCE after each (sometimes multiple of them if there are several languages involved)
        # 1) enumeration item (also with IFCRELASSOCIATESLIBRARY)
        # 2) enumeration
        # 3) property set (also with IFCRELASSOCIATESLIBRARY)
        # 4) property definition (also with IFCRELASSOCIATESLIBRARY)
        # but in ifc4x3 there is no data for those library refernces
        # TODO: need to add it to .ifc for IFC4X3 too
        # if https://github.com/buildingSMART/IFC4.3.x-development/issues/587 is resolved

        # iterate through all xmls files
        for pset_path in glob.iglob(pset_data_glob, recursive=True):
            pset_path = Path(pset_path)

            with open(pset_path, "r", encoding="utf-8") as fi:
                root_xml = etree.fromstring(fi.read())
            pset_name = root_xml.find("Name").text
            # pset / qset
            pset_type = True if pset_name.split("_")[0] == "Pset" else False

            # TODO: if guids provided in xml should use them instead
            pset_guid = ifcopenshell.guid.new()
            applicable_entities = [i.text for i in root_xml.find("ApplicableClasses").findall("ClassName")]
            pset = self.ifc_entity(
                "IfcPropertySetTemplate",
                GlobalId=pset_guid,
                TemplateType=root_xml.get("templatetype"),
                Name=pset_name,
                Description=root_xml.find("Definition").text,
                ApplicableEntity=",".join(applicable_entities),
            )

            # NOTE: there is also Applicability tag
            # but it's seems always empty in ifc4 and ifc4x3
            # in ifc2x3 it's present but contains just applicability string description
            # e.g. "IfcElectricMotorType, IfcFlowMovingDeviceType entities." for "Pset_ElectricMotorTypeCommon"

            pdef_entities = []
            for pdef in root_xml.find("PropertyDefs" if pset_type else "QtoDefs").getchildren():
                pset_property = self.get_property_from_pdef(pset_name, pset_type, pdef)
                if not pset_property:
                    continue
                pdef_entities.append(pset_property)
            pset.HasPropertyTemplates = pdef_entities
            psets_list.append(pset)

        print(f"{len(psets_list)} psets parsed.")
        if rel:
            rel.RelatedDefinitions = psets_list
        self.ifc_file.write(ifc_output_path)

    def get_property_from_pdef(self, pset_name, pset_type, pdef):
        pset_prop_guid = ifcopenshell.guid.new()
        pset_property_name = pdef.find("Name").text

        # figuring pset property types and related values
        if not pset_type:
            property_type_tag = None
        else:
            try:
                assert len(pdef.find("PropertyType").getchildren()) == 1, "Not implemented case"
            except AssertionError:
                warning_message = (
                    f"WARNING: met not handles case with multiple property types "
                    f"- {pset_name}/{pset_property_name}."
                    "This property may have incorrect data parsed."
                )
                print(warning_message)

            property_type_tag = pdef.find("PropertyType").getchildren()[0].tag
            if property_type_tag not in PROPERTY_TYPES_DICT:
                warning_message = (
                    f"WARNING: not implemented property type "
                    f"{property_type_tag} ({pset_name}/{pset_property_name}). "
                    "This property will be skipped. Need to rework the code to support that type of property."
                )
                print(warning_message)
                return

        # NOTE: there is also ValueDef tag
        # which could have two subtags - MinValue and MaxValue
        # but it's seems to be present only in ifc2x3 and everywhere values are either "", "0", "?"
        # so just ignoring it

        # create pset property
        if not pset_type or property_type_tag != "TypeComplexProperty":
            pset_property = self.ifc_entity("IfcSimplePropertyTemplate")
            # tested on IFC4_ADD2.ifc - all props are READWRITE by default
            pset_property.AccessState = "READWRITE"
        else:
            pset_property = self.ifc_entity("IfcComplexPropertyTemplate")
            complex_prop_xml = pdef.find("PropertyType/TypeComplexProperty")
            child_properties = [
                self.get_property_from_pdef(pset_name, pset_type, child_pdef)
                for child_pdef in complex_prop_xml.findall("PropertyDef")
            ]
            pset_property.UsageName = complex_prop_xml.get("name")
            pset_property.HasPropertyTemplates = child_properties

        pset_property.GlobalId = pset_prop_guid
        pset_property.Description = pdef.find("Definition").text
        pset_property.Name = pset_property_name

        self.add_prop_type_params_to_prop(pset_type, pdef, pset_property, property_type_tag)
        return pset_property

    def add_prop_type_params_to_prop(self, pset_type, pdef, pset_property, property_type_tag):
        if not pset_type:
            property_type = pdef.find("QtoType").text
        else:
            property_type, property_type_parse = PROPERTY_TYPES_DICT[property_type_tag]
        pset_property.TemplateType = property_type

        if not pset_type or property_type == "P_COMPLEX":
            # qsets and complex props don't have measure types
            return

        property_type_path = f"PropertyType/{property_type_tag}"
        property_type_xml = pdef.find(property_type_path)

        # usually it's only for P_TABLEVALUE
        expression_xml = property_type_xml.find("Expression")
        if expression_xml is not None and expression_xml.text != "-":
            pset_property.Expression = expression_xml.text

        # figure measure type for property sets
        if property_type == "P_ENUMERATEDVALUE":
            # always create new enumeration for the new properties
            # even if the same enumeration was already used before
            # example of reoccuring enumeration in .ifc for ifc4 - PEnum_ElementStatus
            enum_items = [i.text for i in property_type_xml.findall(f"EnumList/EnumItem")]
            enum_items = [self.ifc_entity("IfcLabel", wrappedValue=i) for i in enum_items]
            prop_enumeration = self.ifc_entity(
                "IfcPropertyEnumeration",
                Name=property_type_xml.find("EnumList").get("name"),
                EnumerationValues=enum_items,
            )
            pset_property.Enumerators = prop_enumeration
            pset_property.PrimaryMeasureType = "IfcLabel"

        elif property_type == "P_TABLEVALUE":
            pset_property.PrimaryMeasureType = property_type_xml.find("DefiningValue/DataType").get("type")
            pset_property.SecondaryMeasureType = property_type_xml.find("DefinedValue/DataType").get("type")
        else:
            if property_type == "P_REFERENCEVALUE":
                pset_property.PrimaryMeasureType = property_type_xml.get(property_type_parse)
                # TODO: ifc4add2 seems to have some secondary measure types
                # need to add it in ifc4x3 too
                # if https://github.com/buildingSMART/IFC4.3.x-development/issues/586 is resolved
            else:
                if property_type == "P_LISTVALUE":
                    property_type_node = "ListValue"
                if property_type in ("P_SINGLEVALUE", "P_BOUNDEDVALUE"):
                    property_type_node = "DataType"

                    # only used only in ifc2x3, omitted in ifc4 and ifc4x3
                    unit_type_xml = property_type_xml.find("UnitType")
                    if unit_type_xml is not None:
                        unit_type = unit_type_xml.get(property_type_parse).strip()
                        if unit_type.lower().startswith("ifc"):
                            unit_entity = self.ifc_entity(unit_type)
                        else:
                            if unit_type in self.ifc_derived_unit_enum:
                                unit_entity = self.ifc_entity("IfcDerivedUnit", UnitType=unit_type)
                            elif unit_type in self.ifc_unit_enum:
                                unit_entity = self.ifc_entity("IfcNamedUnit", UnitType=unit_type)
                            else:
                                print("WARNING. Wasn't able to find units {unit_type} in schema.")
                        pset_property.PrimaryUnit = unit_entity

                type_xml = property_type_xml.find(property_type_node)
                if property_type_node == "ListValue":
                    # for ListValue data type is contained in a single <DataType>
                    primary_measure_type = type_xml.find("DataType").get(property_type_parse)
                else:
                    primary_measure_type = type_xml.get(property_type_parse)

                pset_property.PrimaryMeasureType = primary_measure_type


if __name__ == "__main__":
    templates_generator = PsetTemplatesGenerator()
    templates_generator.parse_ifc4x3_data()
    if not RUN_FROM_DEV_REPO:
        templates_generator.parse_ifc2x3_data()
