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

import glob
from pathlib import Path
import json
import urllib.parse
from markdown import markdown
from bs4 import BeautifulSoup
from pprint import pprint
import requests

IFC2x3_DOCS_LOCATION = 'Ifc2.3.0.1'

class DocExtractor:

    def extract_ifc2x3(self):
        parse_data_location = Path(IFC2x3_DOCS_LOCATION)
        if not parse_data_location.is_dir():
            raise Exception(
                f'Docs for IFC 2.3.0.1 expected to be in folder "{parse_data_location.resolve()}\\"\n'
                'For doc extraction please either setup docs as described above \n'
                'or change IFC2x3_DOCS_LOCATION in doc.py accordingly.'
            )

        # need to parse actual domains from the website
        # since domains from github paths do not match domains from the websites
        # probably due domains on the website being from 4_0
        # example (property set / github domain / website domain):
        # Pset_AirTerminalBoxPHistory IfcControlExtension IfcHvacDomain
        self.extract_ifc2x3_property_sets_domains()
        self.extract_ifc2x3_entities()
        self.extract_ifc2x3_property_sets()
    
    def extract_ifc2x3_property_sets_domains(self):
        property_sets_domains = dict()
        r = requests.get('https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/psd/psd_index.htm')
        html = BeautifulSoup(r.content, features='lxml')
        for a in html.find_all('a'):
            domain, pset = a['href'].removeprefix('./').removesuffix('.xml').split('/')
            property_sets_domains[pset] = domain

        # export property sets data
        with open('schema/ifc2x3_property_sets_domains.json', 'w', encoding='utf-8') as fo:
            print(f'{len(property_sets_domains)} property sets domains were parsed from the website')
            json.dump(
                property_sets_domains, fo,
                sort_keys=True, indent=4
            )

    def extract_ifc2x3_entities(self):
        entities_dict = dict()

        # search 
        entities_paths = [filepath for filepath in glob.iglob(f'{IFC2x3_DOCS_LOCATION}/Sections/**/Entities', recursive=True)]
        for parse_folder_path in entities_paths:
            for entity_path in glob.iglob(f'{parse_folder_path}/**/'):
                entity_path = Path(entity_path)
                entity_name = entity_path.stem
                entities_dict[entity_name] = dict()

                # utf-8-sig because of \ufeff occcurs - meaning it's utf bom encoded
                md_path = entity_path / 'Documentation.md'
                xml_path = entity_path / 'DocEntity.xml'
                github_md_url = f'https://github.com/buildingSMART/IFC/blob/{urllib.parse.quote(str(md_path.as_posix()))}'

                with open(md_path, 'r', encoding='utf-8-sig') as fi:
                    # convert markdown to html for easier parsing
                    html = markdown(fi.read())
                    entity_description = BeautifulSoup(html, features="lxml").find('p').text
                    entity_description = entity_description.replace('\n', ' ')
                    entity_description = entity_description.replace('\u00a0', ' ')

                with open(xml_path, 'r', encoding='utf-8') as fi:
                    bs_tree = BeautifulSoup(fi.read(), features='lxml')
                    entity_attrs = dict()
                    for html_attr in bs_tree.find_all('docattribute'):

                        attr_description = html_attr.text.strip()
                        attr_description = attr_description.replace('\n', ' ')
                        attr_description = attr_description.replace('\u00a0', ' ')
                        entity_attrs[html_attr['name']] = attr_description

                    if entity_attrs:
                        entities_dict[entity_name]['attributes'] = entity_attrs

                entities_dict[entity_name]['description'] = entity_description
                spec_url = 'https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/' \
                        f'{md_path.parents[2].name.lower()}/lexical/{entity_name.lower()}.htm'
                entities_dict[entity_name]['spec_url'] = spec_url

        # export entities data
        with open('schema/ifc2x3_entities.json', 'w', encoding='utf-8') as fo:
            print(f'{len(entities_dict)} entities parsed')
            json.dump(
                entities_dict, fo,
                sort_keys=True, indent=4
            )

    def extract_ifc2x3_property_sets(self):
        property_sets_dict = dict()
        property_sets_references = dict()
        property_sets_spec_urls = dict()

        # extract lists of properties and theirs references for each property set
        parsed_paths = [filepath for filepath in glob.iglob(f'{IFC2x3_DOCS_LOCATION}/Sections/**/PropertySets', recursive=True)]

        # prepare property sets domains from the website we extracted earlier
        with open('schema/ifc2x3_property_sets_domains.json', 'r') as fi:
            property_sets_site_domains = json.load(fi)

        for parse_folder_path in parsed_paths:
            for property_set_path in glob.iglob(f'{parse_folder_path}/**/'):
                property_set_path = Path(property_set_path)
                property_set_name = property_set_path.stem

                property_references = list()
                xml_path = property_set_path / 'DocPropertySet.xml'
                with open(xml_path, 'r', encoding='utf-8') as fi:
                    bs_tree = BeautifulSoup(fi.read(), features='lxml')
                    entity_attrs = dict()
                    for html_attr in bs_tree.find_all('docproperty'):
                        property_references.append(html_attr['href'])

                property_sets_references[property_set_name] = property_references
                property_set_domain = property_sets_site_domains[property_set_name]
                spec_url = f'https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/psd/{property_set_domain}/{property_set_name}.xml'
                property_sets_spec_urls[property_set_name] = spec_url

        # setup references look up tables to convert property hrefs to actual data paths
        references_paths_lookup = dict()
        glob_query = f'{IFC2x3_DOCS_LOCATION}/Properties/*/*'
        for parsed_path in [filepath for filepath in glob.iglob(glob_query, recursive=False)]:
            parsed_path = Path(parsed_path)
            # all references omit "$" character, I've checked
            # need to check it if moving to next IFC version
            property_reference = parsed_path.name.replace('$', '')
            references_paths_lookup[property_reference] = parsed_path

        # setup a function because we'll need to check child properties recusively
        def get_property_info_by_href(href):
            property_dict = dict()
            property_path = references_paths_lookup[href]

            md_path = property_path / 'Documentation.md'
            xml_path = property_path / 'DocProperty.xml'
            github_md_url = f'https://github.com/buildingSMART/IFC/blob/{urllib.parse.quote(str(md_path.as_posix()))}'
            github_xml_url = f'https://github.com/buildingSMART/IFC/blob/{urllib.parse.quote(str(xml_path.as_posix()))}'

            with open(xml_path, 'r', encoding='utf-8') as fi:
                bs_tree = BeautifulSoup(fi.read(), features='lxml')
                entity_attrs = dict()
                tags = bs_tree.find_all('docproperty')

                # check for child properties - if they are present parse their data recursively
                elements_tag = bs_tree.find('elements')
                if elements_tag is not None:
                    child_tags = elements_tag.find_all('docproperty')
                    child_tags_dict = dict()

                    for child_tag in child_tags:
                        child_tag_href = child_tag['href']
                        child_tag_name, child_tag_dict = get_property_info_by_href(child_tag_href)
                        child_tags_dict[child_tag_name] = child_tag_dict
                        tags.remove(child_tag)
                    property_dict['children'] = child_tags_dict
                    print(f'Child nodes found inside property xml. Url: {github_xml_url}')

                if len(tags) != 1:
                    print(f'WARNING. Found more properties inside property xml, '
                        f'only first one were parsed (number of properties: {len(tags)}). Url: {github_xml_url}.')
                property_name = tags[0]['name']


            if not md_path.is_file():
                print('WARNING. Property is missing documentation.md, description will be set to empty. '
                    f'Url: {github_xml_url}')
                description = ''
            else:
                with open(md_path, 'r', encoding='utf-8-sig') as fi:
                    # convert markdown to html for easier parsing
                    html = markdown(fi.read())
                    description = BeautifulSoup(html, features="lxml").find('p').text
                    description = description.replace('\n', ' ')
                    description = description.replace('\u00a0', ' ')
            property_dict['description'] = description
            return (property_name, property_dict)

            
        # lookup each property reference and save it's name and description
        for property_set_name in property_sets_references:
            properties_dict = dict()
            for property_reference in property_sets_references[property_set_name]:
                property_name, property_dict = get_property_info_by_href(property_reference)
                properties_dict[property_name] = property_dict
            property_sets_dict[property_set_name] = {
                'properties': properties_dict,
                'spec_url': property_sets_spec_urls[property_set_name]
            }


        # export property sets data
        with open('schema/ifc2x3_properties.json', 'w', encoding='utf-8') as fo:
            print(f'{len(property_sets_dict)} property sets parsed')
            json.dump(
                property_sets_dict, fo,
                sort_keys=True, indent=4
            )


if __name__ == '__main__':
    extractor = DocExtractor()
    extractor.extract_ifc2x3()


