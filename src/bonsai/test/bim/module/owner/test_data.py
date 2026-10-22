# This file was generated with the assistance of an AI coding tool.

import ifcopenshell

import bonsai.tool as tool
from bonsai.bim.module.owner.data import ActorData
from test.bim.bootstrap import NewFile


class TestActors(NewFile):
    def list_actors(self, ifc):
        tool.Ifc.set(ifc)
        ActorData.load()
        tool.Owner.get_owner_props().actor_class = "IfcActor"
        return ActorData.actors()

    def test_ifc2x3_identification_is_read_from_the_id_attribute(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        person = ifc.createIfcPerson(Id="P1")
        ifc.createIfcActor(Name="Person", TheActor=person)
        organization = ifc.createIfcOrganization(Id="O1", Name="Organization")
        ifc.createIfcActor(Name="Organization", TheActor=organization)
        person_and_organization = ifc.createIfcPersonAndOrganization(ThePerson=person, TheOrganization=organization)
        ifc.createIfcActor(Name="Both", TheActor=person_and_organization)
        assert [a["the_actor"] for a in self.list_actors(ifc)] == ["P1", "O1", "P1-O1"]

    def test_ifc4_identification(self):
        ifc = ifcopenshell.file(schema="IFC4")
        person = ifc.createIfcPerson(Identification="P1")
        ifc.createIfcActor(Name="Person", TheActor=person)
        assert [a["the_actor"] for a in self.list_actors(ifc)] == ["P1"]
