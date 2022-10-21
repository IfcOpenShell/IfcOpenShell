# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 @Andrej730
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

import json
from pathlib import Path

try:
    import glob
    import warnings
    import requests
    import urllib.parse
    from markdown import markdown
    from bs4 import BeautifulSoup
    from bs4 import MarkupResemblesLocatorWarning
except:
    pass  # Only necessary if you're using it to generate the docs database


BASE_MODULE_PATH = Path(__file__).parent
IFC2x3_DOCS_LOCATION = BASE_MODULE_PATH / "Ifc2.3.0.1"
IFC4_DOCS_LOCATION = BASE_MODULE_PATH / "Ifc4.0.2.1"

SCHEMA_FILES = {
    "IFC2X3": {
        "entities": BASE_MODULE_PATH / "schema/ifc2x3_entities.json",
        "properties": BASE_MODULE_PATH / "schema/ifc2x3_properties.json",
    },
    "IFC4": {
        "entities": BASE_MODULE_PATH / "schema/ifc4_entities.json",
        "properties": BASE_MODULE_PATH / "schema/ifc4_properties.json",
    },
}

db = None


def get_db(version):
    global db
    if not db:
        db = {ifc_version: dict() for ifc_version in SCHEMA_FILES}
        for ifc_version in SCHEMA_FILES:
            for data_type in SCHEMA_FILES[ifc_version]:
                schema_path = SCHEMA_FILES[ifc_version][data_type]
                if not schema_path.is_file():
                    print(f"Schema file {schema_path} wasn't found.")
                    files_missing = True
                    continue

                with open(schema_path, "r") as fi:
                    db[ifc_version][data_type] = json.load(fi)
    return db.get(version)


def get_entity_doc(version, entity):
    db = get_db(version)
    if db:
        return db["entities"].get(entity)


def get_attribute_doc(version, entity, attribute):
    db = get_db(version)
    if db:
        entity = db["entities"].get(entity)
        if entity:
            return entity["attributes"].get(attribute)


def get_property_set_doc(version, pset):
    db = get_db(version)
    if db:
        return db["properties"].get(pset)


def get_property_doc(version, pset, prop):
    db = get_db(version)
    if db:
        pset = db["properties"].get(pset)
        if pset:
            return pset["properties"].get(prop)


class DocExtractor:
    def extract_ifc2x3(self):
        print("Parsing data for Ifc2.3.0.1")
        if not IFC2x3_DOCS_LOCATION.is_dir():
            raise Exception(
                f'Docs for IFC 2.3.0.1 expected to be in folder "{IFC2x3_DOCS_LOCATION.resolve()}\\"\n'
                "For doc extraction please either setup docs as described above \n"
                "or change IFC2x3_DOCS_LOCATION in doc.py accordingly. \n"
                "You can download docs from the repository: \n"
                "https://github.com/buildingSMART/IFC/tree/Ifc2.3.0.1"
            )

        # need to parse actual domains from the website
        # since domains from github paths do not match domains from the websites
        # probably due domains on the website being from 4_0
        # example (property set / github domain / website domain):
        # Pset_AirTerminalBoxPHistory IfcControlExtension IfcHvacDomain
        self.extract_ifc2x3_property_sets_site_domains()
        self.extract_ifc2x3_entities()
        self.extract_ifc2x3_property_sets()

    def extract_ifc2x3_property_sets_site_domains(self):
        property_sets_domains = dict()
        r = requests.get("https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/psd/psd_index.htm")
        html = BeautifulSoup(r.content, features="lxml")
        for a in html.find_all("a"):
            domain, pset = a["href"].removeprefix("./").removesuffix(".xml").split("/")
            property_sets_domains[pset] = domain

        # export property sets data
        with open(BASE_MODULE_PATH / "schema/ifc2x3_property_sets_site_domains.json", "w", encoding="utf-8") as fo:
            print(f"{len(property_sets_domains)} property sets domains were parsed from the website")
            json.dump(property_sets_domains, fo, sort_keys=True, indent=4)

    def extract_ifc2x3_entities(self):
        entities_dict = dict()

        # search
        entities_paths = [
            filepath for filepath in glob.iglob(f"{IFC2x3_DOCS_LOCATION}/Sections/**/Entities", recursive=True)
        ]
        for parse_folder_path in entities_paths:
            for entity_path in glob.iglob(f"{parse_folder_path}/**/"):
                entity_path = Path(entity_path)
                entity_name = entity_path.stem
                entities_dict[entity_name] = dict()

                # utf-8-sig because of \ufeff occcurs - meaning it's utf bom encoded
                md_path = entity_path / "Documentation.md"
                xml_path = entity_path / "DocEntity.xml"
                md_url_part = urllib.parse.quote(str(md_path.relative_to(Path(__file__).parent).as_posix()))
                github_md_url = f"https://github.com/buildingSMART/IFC/blob/{md_url_part}"

                with open(md_path, "r", encoding="utf-8-sig") as fi:
                    # convert markdown to html for easier parsing
                    html = markdown(fi.read())
                    entity_description = BeautifulSoup(html, features="lxml").find("p").text
                    entity_description = entity_description.replace("\n", " ")
                    entity_description = entity_description.replace("\u00a0", " ")

                with open(xml_path, "r", encoding="utf-8") as fi:
                    bs_tree = BeautifulSoup(fi.read(), features="lxml")
                    entity_attrs = dict()
                    # temporarily disable MarkupResemblesLocatorWarning
                    # because BeautifulSoup wrongly assume we confused
                    # html code for filepath and gives warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=MarkupResemblesLocatorWarning)

                        for html_attr in bs_tree.find_all("docattribute"):
                            html_description = BeautifulSoup(html_attr.text, features="lxml")
                            attr_description = html_description.get_text()

                            attr_description = attr_description.replace("\n", " ")
                            attr_description = attr_description.replace("\u00a0", " ")
                            attr_description = attr_description.replace("&npsp;", " ")

                            # discard part of the description with changelog
                            # Example:
                            # https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifcpresentationdefinitionresource/lexical/ifcannotationfillarea.htm
                            attr_description = attr_description.split("IFC2x Edition 3 CHANGE", 1)[0]
                            attr_description = attr_description.split("IFC2x Edition 2 Addendum 2 CHANGE", 1)[0]
                            attr_description = attr_description.split("IFC2x2 Addendum 1 change", 1)[0]
                            attr_description = attr_description.split("IFC2x PLATFORM CHANGE", 1)[0]
                            attr_description = attr_description.split("IFC2x3 CHANGE", 1)[0]
                            attr_description = attr_description.split("IFC2x Edition3 CHANGE", 1)[0]

                            attr_description = attr_description.strip().rstrip(">").strip()
                            entity_attrs[html_attr["name"]] = attr_description

                    if entity_attrs:
                        entities_dict[entity_name]["attributes"] = entity_attrs

                entities_dict[entity_name]["description"] = entity_description
                spec_url = (
                    "https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/"
                    f"{md_path.parents[2].name.lower()}/lexical/{entity_name.lower()}.htm"
                )
                entities_dict[entity_name]["spec_url"] = spec_url

        # export entities data
        with open(BASE_MODULE_PATH / "schema/ifc2x3_entities.json", "w", encoding="utf-8") as fo:
            print(f"{len(entities_dict)} entities parsed")
            json.dump(entities_dict, fo, sort_keys=True, indent=4)

    def extract_ifc2x3_property_sets(self):
        property_sets_dict = dict()
        property_sets_references = dict()
        property_sets_spec_urls = dict()

        # extract lists of properties and theirs references for each property set
        parsed_paths = [
            filepath for filepath in glob.iglob(f"{IFC2x3_DOCS_LOCATION}/Sections/**/PropertySets", recursive=True)
        ]

        # prepare property sets domains from the website we extracted earlier
        with open(BASE_MODULE_PATH / "schema/ifc2x3_property_sets_site_domains.json", "r") as fi:
            property_sets_site_domains = json.load(fi)

        for parse_folder_path in parsed_paths:
            for property_set_path in glob.iglob(f"{parse_folder_path}/**/"):
                property_set_path = Path(property_set_path)
                property_set_name = property_set_path.stem

                property_references = list()
                xml_path = property_set_path / "DocPropertySet.xml"
                with open(xml_path, "r", encoding="utf-8") as fi:
                    bs_tree = BeautifulSoup(fi.read(), features="lxml")
                    for html_attr in bs_tree.find_all("docproperty"):
                        property_references.append(html_attr["href"])

                property_sets_references[property_set_name] = property_references
                property_set_domain = property_sets_site_domains[property_set_name]
                spec_url = (
                    "https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML"
                    f"/psd/{property_set_domain}/{property_set_name}.xml"
                )
                property_sets_spec_urls[property_set_name] = spec_url

        # setup references look up tables to convert property hrefs to actual data paths
        references_paths_lookup = dict()
        glob_query = f"{IFC2x3_DOCS_LOCATION}/Properties/*/*"
        for parsed_path in [filepath for filepath in glob.iglob(glob_query, recursive=False)]:
            parsed_path = Path(parsed_path)
            # all references omit "$" character, I've checked it on 2_3
            # need to check it if moving to next IFC version
            property_reference = parsed_path.name.replace("$", "")
            references_paths_lookup[property_reference] = parsed_path

        # setup a function because we'll need to check child properties recusively
        def get_property_info_by_href(href):
            property_dict = dict()
            property_path = references_paths_lookup[href]

            md_path = property_path / "Documentation.md"
            xml_path = property_path / "DocProperty.xml"
            md_url_part = urllib.parse.quote(str(md_path.relative_to(Path(__file__).parent).as_posix()))
            xml_url_part = urllib.parse.quote(str(xml_path.relative_to(Path(__file__).parent).as_posix()))
            github_md_url = f"https://github.com/buildingSMART/IFC/blob/{md_url_part}"
            github_xml_url = f"https://github.com/buildingSMART/IFC/blob/{xml_url_part}"

            with open(xml_path, "r", encoding="utf-8") as fi:
                bs_tree = BeautifulSoup(fi.read(), features="lxml")
                tags = bs_tree.find_all("docproperty")

                # check for child properties - if they are present parse their data recursively
                elements_tag = bs_tree.find("elements")
                if elements_tag is not None:
                    child_tags = elements_tag.find_all("docproperty")
                    child_tags_dict = dict()

                    for child_tag in child_tags:
                        child_tag_href = child_tag["href"]
                        child_tag_name, child_tag_dict = get_property_info_by_href(child_tag_href)
                        child_tags_dict[child_tag_name] = child_tag_dict
                        tags.remove(child_tag)
                    property_dict["children"] = child_tags_dict
                    print(f"Child nodes found inside property xml. Url: {github_xml_url}")

                if len(tags) != 1:
                    print(
                        f"WARNING. Found more properties inside property xml, "
                        f"only first one were parsed (number of properties: {len(tags)}). Url: {github_xml_url}."
                    )
                property_name = tags[0]["name"]

            if not md_path.is_file():
                print(
                    f"WARNING. Property {property_name} is missing documentation.md, "
                    f"property will be left without description. Url: {github_xml_url}"
                )
            else:
                with open(md_path, "r", encoding="utf-8-sig") as fi:
                    # convert markdown to html for easier parsing
                    html = markdown(fi.read())
                    description = BeautifulSoup(html, features="lxml").find("p").text
                    description = description.replace("\n", " ")
                    description = description.replace("\u00a0", " ")
                    property_dict["description"] = description
            return (property_name, property_dict)

        # lookup each property reference and save it's name and description
        for property_set_name in property_sets_references:
            properties_dict = dict()
            for property_reference in property_sets_references[property_set_name]:
                property_name, property_dict = get_property_info_by_href(property_reference)
                properties_dict[property_name] = property_dict
            property_sets_dict[property_set_name] = {
                "properties": properties_dict,
                "spec_url": property_sets_spec_urls[property_set_name],
            }

        # export property sets data
        with open(BASE_MODULE_PATH / "schema/ifc2x3_properties.json", "w", encoding="utf-8") as fo:
            print(f"{len(property_sets_dict)} property sets parsed")
            json.dump(property_sets_dict, fo, sort_keys=True, indent=4)

    def extract_ifc4(self):
        print("Parsing data for Ifc4.0.2.1")
        if not IFC4_DOCS_LOCATION.is_dir():
            raise Exception(
                f'Docs for Ifc4.0.2.1 expected to be in folder "{IFC4_DOCS_LOCATION.resolve()}\\"\n'
                "For doc extraction please either setup docs as described above \n"
                "or change IFC4_DOCS_LOCATION in doc.py accordingly."
                "You can download docs from the repository: \n"
                "https://github.com/buildingSMART/IFC/tree/Ifc4.0.2.1"
            )

        # actually domains in Ifc 4.0 are consistent between website and docs
        # BUT there are two property sets that site is missing and therefore they won't have spec_url
        # because of them I left the site parsing too
        # missed property sets:
        # Pset_BuildingElementCommon Pset_ElementCommon
        self.extract_ifc4_property_sets_site_domains()
        self.extract_ifc4_entities()
        self.extract_ifc4_property_sets()

    def extract_ifc4_property_sets_site_domains(self):
        property_sets_domains = dict()
        with requests.get(
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1"
            "/HTML/annex/annex-b/alphabeticalorder_psets.htm"
        ) as r:
            html = BeautifulSoup(r.content, features="lxml")
            for a in html.find_all("a", {"class": "listing-link"}):
                href_split = a["href"].split("/")
                domain = href_split[3]
                pset = href_split[5].removesuffix(".htm")
                property_sets_domains[pset] = domain

        with requests.get(
            "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/"
            "/HTML/annex/annex-b/alphabeticalorder_qsets.htm"
        ) as r:
            html = BeautifulSoup(r.content, features="lxml")
            for a in html.find_all("a", {"class": "listing-link"}):
                href_split = a["href"].split("/")
                domain = href_split[3]
                pset = href_split[5].removesuffix(".htm")
                property_sets_domains[pset] = domain

        # export property sets data
        with open(BASE_MODULE_PATH / "schema/ifc4_property_sets_site_domains.json", "w", encoding="utf-8") as fo:
            print(f"{len(property_sets_domains)} property sets domains were parsed from the website")
            json.dump(property_sets_domains, fo, sort_keys=True, indent=4)

    def extract_ifc4_entities(self):
        entities_dict = dict()

        # search
        entities_paths = [
            filepath for filepath in glob.iglob(f"{IFC4_DOCS_LOCATION}/Sections/**/Entities", recursive=True)
        ]
        for parse_folder_path in entities_paths:
            for entity_path in glob.iglob(f"{parse_folder_path}/**/"):
                entity_path = Path(entity_path)
                entity_name = entity_path.stem
                entities_dict[entity_name] = dict()

                # utf-8-sig because of \ufeff occcurs - meaning it's utf bom encoded
                md_path = entity_path / "Documentation.md"
                xml_path = entity_path / "DocEntity.xml"
                md_url_part = urllib.parse.quote(str(md_path.relative_to(Path(__file__).parent).as_posix()))
                github_md_url = f"https://github.com/buildingSMART/IFC/blob/{md_url_part}"

                with open(md_path, "r", encoding="utf-8-sig") as fi:
                    # convert markdown to html for easier parsing
                    html = markdown(fi.read())
                    entity_description = BeautifulSoup(html, features="lxml").find("p").text
                    entity_description = entity_description.replace("\n", " ")
                    entity_description = entity_description.replace("\u00a0", " ")
                    entity_description = entity_description.replace("{ .extDef}", "")
                    entity_description = entity_description.strip()

                with open(xml_path, "r", encoding="utf-8") as fi:
                    bs_tree = BeautifulSoup(fi.read(), features="lxml")
                    entity_attrs = dict()
                    # temporarily disable MarkupResemblesLocatorWarning
                    # because BeautifulSoup wrongly assume we confused
                    # html code for filepath and gives warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=MarkupResemblesLocatorWarning)
                        for html_attr in bs_tree.find_all("docattribute"):
                            html_description = BeautifulSoup(html_attr.text, features="lxml")
                            attr_description = html_description.get_text()
                            attr_description = attr_description.replace("\n", " ")
                            attr_description = attr_description.replace("\u00a0", " ")

                            # discard part of the description with changelog, notes and examples etc.
                            # Those notes actually can be useful but we'll need a way to reformat them
                            # Example:
                            # https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifcsharedbldgelements/lexical/ifcrelconnectspathelements.htm
                            attr_description = attr_description.split("{ .change-ifc", 1)[0]
                            attr_description = attr_description.split("{ .note", 1)[0]
                            attr_description = attr_description.split("{ .examples", 1)[0]
                            attr_description = attr_description.split("{ .deprecated", 1)[0]
                            attr_description = attr_description.split("{ .history", 1)[0]

                            attr_description = attr_description.strip()
                            entity_attrs[html_attr["name"]] = attr_description

                    if entity_attrs:
                        entities_dict[entity_name]["attributes"] = entity_attrs

                entities_dict[entity_name]["description"] = entity_description
                spec_url = (
                    "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/"
                    f"{md_path.parents[2].name.lower()}/lexical/{entity_name.lower()}.htm"
                )
                entities_dict[entity_name]["spec_url"] = spec_url
                # entities_dict[entity_name]['github_url'] = github_md_url

        # export entities data
        with open(BASE_MODULE_PATH / "schema/ifc4_entities.json", "w", encoding="utf-8") as fo:
            print(f"{len(entities_dict)} entities parsed")
            json.dump(entities_dict, fo, sort_keys=True, indent=4)

    def extract_ifc4_property_sets(self):
        # function parses both property and quantity sets
        property_sets_dict = dict()
        property_sets_references = dict()
        property_sets_spec_urls = dict()

        # extract lists of properties and theirs references for each property set
        parsed_paths = [
            filepath for filepath in glob.iglob(f"{IFC4_DOCS_LOCATION}/Sections/**/PropertySets", recursive=True)
        ]
        parsed_paths += [
            filepath for filepath in glob.iglob(f"{IFC4_DOCS_LOCATION}/Sections/**/QuantitySets", recursive=True)
        ]

        # prepare property sets domains from the website we extracted earlier
        with open(BASE_MODULE_PATH / "schema/ifc4_property_sets_site_domains.json", "r") as fi:
            property_sets_site_domains = json.load(fi)

        psets_test = set()
        for parse_folder_path in parsed_paths:
            for property_set_path in glob.iglob(f"{parse_folder_path}/**/"):
                property_set_path = Path(property_set_path)
                property_set_name = property_set_path.stem

                property_references = list()
                property_quantity = property_set_path.parents[0].name == "QuantitySets"
                xml_path = property_set_path / ("DocQuantitySet.xml" if property_quantity else "DocPropertySet.xml")

                with open(xml_path, "r", encoding="utf-8") as fi:
                    bs_tree = BeautifulSoup(fi.read(), features="lxml")
                    for html_attr in bs_tree.find_all("docquantity" if property_quantity else "docproperty"):
                        property_references.append(html_attr["href"])

                property_sets_references[property_set_name] = property_references

                if property_set_name.lower() not in property_sets_site_domains:
                    print(
                        f"WARNING. {property_set_name} was not found on the spec website, "
                        "this property set won't have any spec_url in schema."
                    )
                else:
                    property_set_domain = property_sets_site_domains.get(property_set_name.lower(), "")
                    spec_url = (
                        "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML"
                        f"/schema/{property_set_domain}"
                        f'/{"qset" if property_quantity else "pset"}'
                        f"/{property_set_name.lower()}.htm"
                    )
                    property_sets_spec_urls[property_set_name] = spec_url

        # setup references look up tables to convert property hrefs to actual data paths
        references_paths_lookup = dict()
        parsed_paths = [filepath for filepath in glob.iglob(f"{IFC4_DOCS_LOCATION}/Properties/*/*", recursive=False)]
        parsed_paths += [filepath for filepath in glob.iglob(f"{IFC4_DOCS_LOCATION}/Quantities/*/*", recursive=False)]
        for parsed_path in parsed_paths:
            parsed_path = Path(parsed_path)
            # all references omit "$" character, I've checked it on 4_0
            # need to check it if moving to next IFC version
            # btw no reason to check if all references were used in properties
            # because there are also child properties
            property_reference = parsed_path.name.replace("$", "")
            references_paths_lookup[property_reference] = parsed_path

        # setup a function because we'll need to check child properties recusively
        def get_property_info_by_href(href):
            property_dict = dict()
            property_path = references_paths_lookup[href]

            property_quantity = property_path.parents[1].name == "Quantities"

            md_path = property_path / "Documentation.md"
            xml_path = property_path / ("DocQuantity.xml" if property_quantity else "DocProperty.xml")
            md_url_part = urllib.parse.quote(str(md_path.relative_to(Path(__file__).parent).as_posix()))
            github_md_url = f"https://github.com/buildingSMART/IFC/blob/{md_url_part}"
            xml_url_part = urllib.parse.quote(str(xml_path.relative_to(Path(__file__).parent).as_posix()))
            github_xml_url = f"https://github.com/buildingSMART/IFC/blob/{xml_url_part}"

            with open(xml_path, "r", encoding="utf-8") as fi:
                bs_tree = BeautifulSoup(fi.read(), features="lxml")
                tags = bs_tree.find_all("docquantity" if property_quantity else "docproperty")

                # check for child properties - if they are present parse their data recursively
                elements_tag = bs_tree.find("elements")
                if elements_tag is not None:
                    child_tags = elements_tag.find_all("docquantity" if property_quantity else "docproperty")
                    child_tags_dict = dict()

                    for child_tag in child_tags:
                        child_tag_href = child_tag["href"]
                        child_tag_name, child_tag_dict = get_property_info_by_href(child_tag_href)
                        child_tags_dict[child_tag_name] = child_tag_dict
                        tags.remove(child_tag)
                    property_dict["children"] = child_tags_dict
                    print(f"Child nodes found inside property xml. Url: {github_xml_url}")

                if len(tags) != 1:
                    print(
                        f"WARNING. Found more properties inside property xml, "
                        f"only first one were parsed (number of properties: {len(tags)}). Url: {github_xml_url}."
                    )
                property_name = tags[0]["name"]

            if not md_path.is_file():
                print(
                    f"WARNING. Property {property_name} is missing documentation.md, property will be left without description. "
                    f"Url: {github_xml_url}"
                )
            else:
                with open(md_path, "r", encoding="utf-8-sig") as fi:
                    # convert markdown to html for easier parsing
                    html = markdown(fi.read())
                    description = BeautifulSoup(html, features="lxml").find("p").text
                    description = description.replace("\n", " ")
                    description = description.replace("\u00a0", " ")
                    property_dict["description"] = description
            return (property_name, property_dict)

        # lookup each property reference and save it's name and description
        for property_set_name in property_sets_references:
            properties_dict = dict()
            for property_reference in property_sets_references[property_set_name]:
                property_name, property_dict = get_property_info_by_href(property_reference)
                properties_dict[property_name] = property_dict
            property_sets_dict[property_set_name] = {"properties": properties_dict}
            if property_set_name in property_sets_spec_urls:
                spec_url = property_sets_spec_urls[property_set_name]
                property_sets_dict[property_set_name]["spec_url"] = spec_url

        # export property sets data
        with open(BASE_MODULE_PATH / "schema/ifc4_properties.json", "w", encoding="utf-8") as fo:
            print(f"{len(property_sets_dict)} property sets parsed")
            json.dump(property_sets_dict, fo, sort_keys=True, indent=4)


def run_doc_api_examples():
    print("Entities:")
    print(get_entity_doc("IFC2X3", "IfcActionRequest"))
    print(get_entity_doc("IFC4", "IfcActionRequest"))

    print("Entity attributes:")
    print(get_attribute_doc("IFC2X3", "IfcActionRequest", "RequestID"))
    print(get_attribute_doc("IFC4", "IfcActionRequest", "PredefinedType"))

    print("Propety sets:")
    print(get_property_set_doc("IFC2X3", "Pset_ZoneCommon"))
    print(get_property_set_doc("IFC4", "Pset_ZoneCommon"))

    print("Propety sets attributes:")
    print(get_property_doc("IFC2X3", "Pset_ZoneCommon", "Category"))
    print(get_property_doc("IFC4", "Pset_ZoneCommon", "NetPlannedArea"))


if __name__ == "__main__":
    extractor = DocExtractor()
    extractor.extract_ifc2x3()
    extractor.extract_ifc4()

    # run_doc_api_examples()
