# ifccityjson - Python CityJSON to IFC converter
# Copyright (C) 2021 Laurens J.N. Oostwegel <l.oostwegel@gmail.com>
#
# This file is part of ifccityjson.
#
# ifccityjson is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ifccityjson is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ifccityjson.  If not, see <http://www.gnu.org/licenses/>.

import os
import ifcopenshell
import ifcopenshell.api
from datetime import datetime

from .geometry import GeometryIO

JSON_TO_IFC = {
    "Building": ["IfcBuilding"],
    "BuildingPart": ["IfcBuilding", {"CompositionType": "PARTIAL"}],
    "BuildingInstallation": ["IfcBuildingElementProxy"],
    "Road": ["IfcCivilElement"],  # Update for IFC4.3
    "Railway": ["IfcCivilElement"],  # Update for IFC4.3
    "TransportSquare": ["IfcCivilElement"],  # Update for IFC4.3
    "TINRelief": ["IfcGeographicElement", {"PredefinedType": "TERRAIN"}],
    "WaterBody": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                           "ObjectType": "WaterBody"}],  # Update for IFC4.3
    "LandUse": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                         "ObjectType": "LandUse"}],
    "PlantCover": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                            "ObjectType": "Plantcover"}],
    "SolitaryVegetationObject": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                                          "ObjectType": "SolitaryVegetationObject"}],
    "CityFurniture": ["IfcFurnishingElement"],
    "GenericCityObject": ["IfcCivilElement"],
    "Bridge": ["IfcCivilElement"],  # Update for IFC4.3
    "BridgePart": ["IfcCivilElement"],  # Update for IFC4.3
    "BridgeInstallation": ["IfcCivilElement"],  # Update for IFC4.3
    "BridgeConstructionElement": ["IfcCivilElement"],  # Update for IFC4.3
    "Tunnel": ["IfcCivilElement"],  # Update for IFC4.3
    "TunnelPart": ["IfcCivilElement"],  # Update for IFC4.3
    "TunnelInstallation": ["IfcCivilElement"],  # Update for IFC4.3
    "CityObjectGroup": ["IfcBuilding"],  # Update for IFC4.3
    "GroundSurface": ["IfcSlab", {"PredefinedType": "BASESLAB"}],
    "RoofSurface": ["IfcRoof"],
    "WallSurface": ["IfcWall"],
    "ClosureSurface": ["IfcSpace"],
    "OuterCeilingSurface": ["IfcCovering", {"PredefinedType": "CEILING"}],
    "OuterFloorSurface": ["IfcSlab", {"PredefinedType": "FLOOR"}],
    "Window": ["IfcWindow"],
    "Door": ["IfcDoor"],
    "WaterSurface": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                              "ObjectType": "WaterSurface"}],  # Update for IFC4.3
    "WaterGroundSurface": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                                    "ObjectType": "WaterGroundSurface"}],  # Update for IFC4.3
    "WaterClosureSurface": ["IfcGeographicElement", {"PredefinedType": "USERDEFINED",
                                                     "ObjectType": "WaterClosureSurface"}],  # Update for IFC4.3
    "TrafficArea": ["IfcCivilElement"],  # Update for IFC4.3
    "AuxiliaryTrafficArea": ["IfcCivilElement"]  # Update for IFC4.3
}


class Cityjson2ifc:
    def __init__(self):
        self.city_model = None
        self.IFC_model = None
        self.properties = {}
        self.geometry = GeometryIO()
        self.configuration()

    def configuration(self, file_destination="output.ifc", name_attribute=None, split=True, lod=None):
        self.properties["file_destination"], self.properties["file_extension"] = os.path.splitext(file_destination)
        self.properties["name_attribute"] = name_attribute
        self.properties["split"] = split
        self.properties["lod"] = lod

    def convert(self, city_model):
        self.city_model = city_model
        self.create_new_file()
        self.create_metadata()
        self.geometry.set_scale(self.properties["local_scale"])
        #self.geometry.build_vertices(self.IFC_model,
        #                             coords=city_model.j["vertices"],
        #                             scale=self.properties["local_scale"])
        # self.build_vertices()
        self.create_IFC_classes()
        if self.properties["lod"]:
            self.write_file()
        elif self.properties["split"]:
            self.write_files()
        else:
            self.write_file()

    def create_metadata(self):
        # Georeferencing
        self.properties["local_translation"] = None
        self.properties["local_scale"] = None
        if self.city_model.is_transform():
            self.properties["local_scale"] = self.city_model.j['transform']['scale']
            local_translation = self.city_model.j['transform']['translate']
            self.properties["local_translation"] = {
                "Eastings": local_translation[0],
                "Northings": local_translation[1],
                "OrthogonalHeight": local_translation[2]
            }

        epsg = self.city_model.get_epsg()
        if epsg:
            # Meter is assumed as unit for now
            unit = self.IFC_model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
            self.properties["local_translation"]["TargetCRS"] = self.IFC_model.create_entity("IfcProjectedCrs", Name=f"epsg:{epsg}")
            self.properties["local_translation"]["SourceCRS"] = self.IFC_representation_context
            self.IFC_model.create_entity("IfcMapConversion", **self.properties["local_translation"])

    def create_new_file(self):
        self.IFC_model = ifcopenshell.api.run("project.create_file")
        self.IFC_project = ifcopenshell.api.run("root.create_entity", self.IFC_model, **{"ifc_class": "IfcProject", "name": "My Project"})
        ifcopenshell.api.run("unit.assign_unit", self.IFC_model, length={"is_metric": True, "raw": "METERS"})
        self.properties["owner_history"] = self.create_owner_history()
        self.IFC_representation_context = ifcopenshell.api.run("context.add_context", self.IFC_model,
                                                               **{"context": "Model"})

        if not self.city_model.has_metadata() or "presentLoDs" not in self.city_model.j["metadata"]:
            self.city_model.update_metadata()

        # create IFC representation subcontexts from lods
        self.create_representation_sub_contexts()

        self.IFC_site = ifcopenshell.api.run("root.create_entity", self.IFC_model,
                                             **{"ifc_class": "IfcSite",
                                                "name": "My Site"})
        self.IFC_model.create_entity("IfcRelAggregates",
                                     **{"GlobalId": ifcopenshell.guid.new(),
                                        "RelatedObjects": [self.IFC_site],
                                        "RelatingObject": self.IFC_project})

    def create_representation_sub_contexts(self):
        self.IFC_representation_sub_contexts = {}
        # for lod in self.city_model.j["metadata"]["presentLoDs"]:
        #     self.IFC_representation_sub_contexts[str(lod)] = self.create_representation_sub_context(lod)

    def create_representation_sub_context(self, lod):
        # TODO in ifcopenshell.api.context.add_context add support for UserDefinedTargetView
        # self.IFC_representation_sub_contexts[str(lod)] = ifcopenshell.api.run("context.add_context", self.IFC_model,
        #                                                            **{"context": "Model",
        #                                                               "subcontext": "Body",
        #                                                               "target_view": "USERDEFINED",
        #                                                               "UserDefinedTargetView":str(lod)})
        return self.IFC_model.create_entity("IfcGeometricRepresentationSubContext",
                                         **{"ContextType": "Model",
                                        "ContextIdentifier": "Body",
                                        "TargetView": "USERDEFINED",
                                        "ParentContext": self.IFC_representation_context,
                                        "UserDefinedTargetView": "LOD" + str(lod)})

    def create_owner_history(self):
        actor = self.IFC_model.createIfcActorRole("ENGINEER", None, None)
        person = self.IFC_model.createIfcPerson("Oostwegel", None, "L.J.N.", None, None, None, (actor,))
        organization = self.IFC_model.createIfcOrganization(
            None,
            "IfcOpenShell",
            "IfcOpenShell, an open source (LGPL) software library that helps users and software developers to work with the IFC file format.",
        )
        p_o = self.IFC_model.createIfcPersonAndOrganization(person, organization)
        application = self.IFC_model.createIfcApplication(organization, "v0.0.x", "ifccityjson", "ifccityjson")
        timestamp = int(datetime.now().timestamp())
        ownerHistory = self.IFC_model.createIfcOwnerHistory(p_o, application, "READWRITE", None, None, None, None,
                                                            timestamp)

        return ownerHistory

    def write_file(self):
        file = self.properties["file_destination"] + self.properties["file_extension"]
        self.IFC_model.write(file)

    def write_files(self):
        for lod, IFC_representation_sub_context in self.IFC_representation_sub_contexts.items():
            sub_context_id = IFC_representation_sub_context.id()

            # TODO this method makes a copy of the IFC_model by writing it and importing it,
            # TODO but maybe there is a better method.
            file = self.properties["file_destination"] + lod + self.properties["file_extension"]
            self.IFC_model.write(file)
            IFC_copied_model = ifcopenshell.open(file)
            IFC_copied_model_sub_contexts = IFC_copied_model.by_type('IfcGeometricRepresentationSubContext')
            for sub_context in IFC_copied_model_sub_contexts:
                if sub_context.id() == sub_context_id:
                    continue

                representations_in_context = sub_context.RepresentationsInContext
                for element in representations_in_context:
                    IFC_copied_model.remove(element)
                    # slow:
                    # ifcopenshell.api.run("geometry.remove_representation", IFC_copied_model, representation=element)

                ifcopenshell.api.run("context.remove_context", IFC_copied_model, context=sub_context)

            IFC_copied_model.write(file)
            del IFC_copied_model

    def create_IFC_classes(self):
        parents_children_relations = {"IfcSite": {'Parent': self.IFC_site, 'Children': []}}
        geometries = {}
        for obj_id, obj in self.city_model.get_cityobjects().items():
            # CityJSON type to class
            mapping = JSON_TO_IFC[obj.type]
            IFC_class = mapping[0]
            data = {}
            # Add attributes if it is specified in mapping
            # Example: BuildingPart to IfcBuilding with CompositionType: Partial
            if len(mapping) > 1:
                data.update(mapping[1])

            # attributes
            IFC_name = obj_id
            if "name_attribute" in self.properties and self.properties["name_attribute"] in obj.attributes:
                IFC_name = obj.attributes[self.properties["name_attribute"]]

            if len(obj.geometry) == 0:
                print(f"Warning: Object {obj_id} has no geometry.")

            IFC_semantic_surface_children = []
            IFC_shape_representations = []
            for geometry in obj.geometry:
                lod = geometry.lod
                if self.properties["lod"] is not None and str(lod) != self.properties["lod"]:
                    continue
                if str(lod) not in self.IFC_representation_sub_contexts:
                    self.IFC_representation_sub_contexts[str(lod)] = self.create_representation_sub_context(lod)

                IFC_geometry, shape_representation_type = None, None

                if geometry and geometry.surfaces:
                    IFC_semantic_surface_children.extend(self.create_IFC_semantic_surface_children(geometry, lod))
                elif geometry:
                    IFC_geometry, shape_representation_type = self.geometry.create_IFC_geometry(self.IFC_model,
                                                                                                geometry)
                if IFC_geometry:
                    IFC_shape_representation = self.create_IFC_shape_representation(IFC_geometry,
                                                                                shape_representation_type,
                                                                                lod)
                    IFC_shape_representations.append(IFC_shape_representation)

            if len(IFC_shape_representations) > 0:
                data["Representation"] = self.IFC_model.create_entity("IfcProductDefinitionShape",
                                                              Representations=IFC_shape_representations)
            data["GlobalId"] = ifcopenshell.guid.new()
            data["Name"] = IFC_name

            IFC_object = self.IFC_model.create_entity(IFC_class, **data)

            # Define aggregation
            if len(obj.parents) == 0:
                parents_children_relations["IfcSite"]['Children'].append(IFC_object)

            for parent in obj.parents:
                if parent not in parents_children_relations:
                    parents_children_relations[parent] = {'Parent': None, 'Children': []}
                parents_children_relations[parent]['Children'].append(IFC_object)

            if len(obj.children) > 0:
                if obj_id not in parents_children_relations:
                    parents_children_relations[obj_id] = {'Parent': None, 'Children': []}
                parents_children_relations[obj_id]['Parent'] = IFC_object

            if IFC_semantic_surface_children:
                self.IFC_model.create_entity("IfcRelContainedInSpatialStructure",
                                             **{"GlobalId": ifcopenshell.guid.new(),
                                                "RelatedElements": IFC_semantic_surface_children,
                                                "RelatingStructure": IFC_object})

            self.create_property_set(obj.attributes, IFC_object)

        for parent, parent_children in parents_children_relations.items():
            self.IFC_model.create_entity("IfcRelAggregates",
                                         **{"GlobalId": ifcopenshell.guid.new(),
                                            "RelatedObjects": parent_children['Children'],
                                            "RelatingObject": parent_children['Parent']}
                                         )

    def create_IFC_semantic_surface_children(self, geometry, lod):
        IFC_semantic_surface_children = []
        for surface_id in geometry.surfaces:
            IFC_child_class = JSON_TO_IFC[geometry.surfaces[surface_id]["type"]][0]
            child_data = {"GlobalId": ifcopenshell.guid.new(),
                          "Name": IFC_child_class
                          }

            # CREATE ENTITY
            surface_geometry = self.geometry.create_IFC_surface(self.IFC_model, geometry, surface_id)
            if surface_geometry:
                IFC_shape_representation =self.create_IFC_shape_representation(surface_geometry, 'brep', lod)

                child_data["Representation"] = self.IFC_model.create_entity("IfcProductDefinitionShape",
                                             Representations=[IFC_shape_representation])
            IFC_semantic_surface_children.append(self.IFC_model.create_entity(IFC_child_class, **child_data))

        return IFC_semantic_surface_children

    def create_IFC_shape_representation(self, IFC_geometry, shape_representation_type, lod):
        if not isinstance(IFC_geometry, list):
            IFC_geometry = [IFC_geometry]

        shape_representation = self.IFC_model.create_entity("IfcShapeRepresentation",
                                                            self.IFC_representation_sub_contexts[str(lod)], 'Body',
                                                            shape_representation_type,
                                                            IFC_geometry)
        return shape_representation

    def create_property_set(self, CJ_attributes, IFC_entity):
        if len(CJ_attributes) == 0:
            return

        pset = ifcopenshell.api.run("pset.add_pset", self.IFC_model, product=IFC_entity, name="CityJSON_attributes")
        ifcopenshell.api.run("pset.edit_pset", self.IFC_model, pset=pset, properties=CJ_attributes)