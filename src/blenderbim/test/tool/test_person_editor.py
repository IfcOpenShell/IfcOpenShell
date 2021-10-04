# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell
import test.bim.bootstrap
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.person_editor import PersonEditor as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.PersonEditor)


class TestSetPerson(test.bim.bootstrap.NewFile):
    def test_run(self):
        person = ifcopenshell.file().createIfcPerson()
        subject().set_person(person)
        assert bpy.context.scene.BIMOwnerProperties.active_person_id == person.id()


class TestImportAttributes(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        person.Identification = "identification"
        person.GivenName = "given_name"
        person.FamilyName = "family_name"
        person.MiddleNames = ("middle", "names")
        person.PrefixTitles = ("prefix", "titles")
        person.SuffixTitles = ("suffix", "titles")
        subject().set_person(person)
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.person_attributes.get("Identification").string_value == "identification"
        assert props.person_attributes.get("GivenName").string_value == "given_name"
        assert props.person_attributes.get("FamilyName").string_value == "family_name"
        assert len(props.middle_names) == 2
        assert props.middle_names[0].name == "middle"
        assert props.middle_names[1].name == "names"
        assert len(props.prefix_titles) == 2
        assert props.prefix_titles[0].name == "prefix"
        assert props.prefix_titles[1].name == "titles"
        assert len(props.suffix_titles) == 2
        assert props.suffix_titles[0].name == "suffix"
        assert props.suffix_titles[1].name == "titles"

    def test_overwriting_a_previous_import(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        person.Identification = "identification"
        person.GivenName = "given_name"
        subject().set_person(person)
        subject().import_attributes()
        person.Identification = "identification2"
        person.GivenName = None
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.person_attributes.get("Identification").string_value == "identification2"
        assert props.person_attributes.get("GivenName").string_value == ""


class TestClearPerson(test.bim.bootstrap.NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMOwnerProperties
        props.active_person_id = 1
        subject().clear_person()
        assert props.active_person_id == 0


class TestExportAttributes(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        person.Identification = "identification"
        person.GivenName = "given_name"
        person.FamilyName = "family_name"
        person.MiddleNames = ("middle", "names")
        person.PrefixTitles = ("prefix", "titles")
        person.SuffixTitles = ("suffix", "titles")
        subject().set_person(person)
        subject().import_attributes()
        assert subject().export_attributes() == {
            "Identification": "identification",
            "GivenName": "given_name",
            "FamilyName": "family_name",
            "MiddleNames": ["middle", "names"],
            "PrefixTitles": ["prefix", "titles"],
            "SuffixTitles": ["suffix", "titles"],
        }

    def test_getting_empty_list_attributes_as_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        result = subject().export_attributes()
        assert result["MiddleNames"] is None
        assert result["PrefixTitles"] is None
        assert result["SuffixTitles"] is None


class TestGetPerson(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        subject().set_person(person)
        assert subject().get_person() == person


class TestAddAttribute(test.bim.bootstrap.NewFile):
    def test_run(self):
        subject().add_attribute("MiddleNames")
        subject().add_attribute("PrefixTitles")
        subject().add_attribute("SuffixTitles")
        props = bpy.context.scene.BIMOwnerProperties
        assert len(props.middle_names) == 1
        assert len(props.prefix_titles) == 1
        assert len(props.suffix_titles) == 1


class TestRemoveAttribute(test.bim.bootstrap.NewFile):
    def test_run(self):
        subject().add_attribute("MiddleNames")
        subject().remove_attribute("MiddleNames", 0)
        subject().add_attribute("PrefixTitles")
        subject().remove_attribute("PrefixTitles", 0)
        subject().add_attribute("SuffixTitles")
        subject().remove_attribute("SuffixTitles", 0)
        props = bpy.context.scene.BIMOwnerProperties
        assert len(props.middle_names) == 0
        assert len(props.prefix_titles) == 0
        assert len(props.suffix_titles) == 0
