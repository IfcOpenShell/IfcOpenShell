import ifcopenshell
import ifcopenshell.api
from geometry import GeometryIO
from datetime import datetime

JSON_TO_IFC = {
    "Building": ["IfcBuilding"],
    "BuildingPart": ["IfcBuilding", {"CompositionType": "Partial"}],  # CompositionType: Partial
    "BuildingInstallation": ["IfcDistributionElement"],
    "Road": ["IfcCivilElement"],
    "TransportSquare": ["IfcSpace"],
    "TINRelief": ["IfcGeographicElement"],
    "WaterBody": ["IfcGeographicElement"],  # Update for IFC4.3
    "LandUse": ["IfcGeographicElement"],
    "PlantCover": ["IfcGeographicElement"],
    "SolitaryVegetationObject": ["IfcGeographicElement"],
    "CityFurniture": ["IfcFurnishingElement"],
    "GenericCityObject": ["IfcCivilElement"],
    "Bridge": ["IfcCivilElement"],  # Update for IFC4.3
    "BridgePart": ["IfcCivilElement"],  # Update for IFC4.3
    "BridgeInstallation": ["IfcCivilElement"],  # Update for IFC4.3
    "BridgeConstructionElement": ["IfcCivilElement"],  # Update for IFC4.3
    "Tunnel": ["IfcCivilElement"],  # Update for IFC4.3
    "TunnelPart": ["IfcCivilElement"],  # Update for IFC4.3
    "TunnelInstallation": ["IfcCivilElement"],  # Update for IFC4.3
    "CityObjectGroup": ["IfcCivilElement"],
    "GroundSurface": ["IfcSlab", {"PredefinedType": "BASESLAB"}],
    "RoofSurface": ["IfcRoof"],
    "WallSurface": ["IfcWall"],
    "ClosureSurface": ["IfcSpace"],
    "OuterCeilingSurface": ["IfcCovering", {"PredefinedType": "CEILING"}],
    "OuterFloorSurface": ["IfcSlab", {"PredefinedType": "FLOOR"}],
    "Window": ["IfcWindow"],
    "Door": ["IfcDoor"],
    "WaterSurface": ["IfcGeographicElement"],  # Update for IFC4.3
    "WaterGroundSurface": ["IfcGeographicElement"],  # Update for IFC4.3
    "WaterClosureSurface": ["IfcGeographicElement"],  # Update for IFC4.3
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


    def configuration(self, file_destination="output.ifc", name_attribute=None):
        self.properties["file_destination"] = file_destination
        self.properties["name_attribute"] = name_attribute


    def convert(self, city_model):
        self.city_model = city_model
        self.create_new_file()
        self.create_metadata()
        self.geometry.build_vertices(self.IFC_model,
                                     coords=city_model.j["vertices"],
                                     scale=self.properties["local_scale"])
        # self.build_vertices()
        self.create_IFC_classes()
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
            crs = self.IFC_model.create_entity("IfcProjectedCrs", Name=f"epsg:{epsg}")
            self.IFC_model.create_entity("IfcMapConversion", self.IFC_representation_context, **self.properties["local_translation"])

    def create_new_file(self):
        self.IFC_model = ifcopenshell.api.run("project.create_file")
        self.IFC_project = ifcopenshell.api.run("root.create_entity", self.IFC_model, **{"ifc_class": "IfcProject"})
        self.properties["owner_history"] = self.create_owner_history()
        ifcopenshell.api.run("unit.assign_unit", self.IFC_model)
        self.IFC_representation_context = ifcopenshell.api.run("context.add_context", self.IFC_model,
                                                               **{"context": "Model"})
        self.IFC_representation_sub_context = ifcopenshell.api.run("context.add_context", self.IFC_model,
                                                                **{"context": "Model",
                                                                   "subcontext": "Body", # LODs as subcontext
                                                                   "target_view": "MODEL_VIEW"})

        self.IFC_site = ifcopenshell.api.run("root.create_entity", self.IFC_model,
                                                                **{"ifc_class": "IfcSite",
                                                                   "name": "My Site"})

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
        ownerHistory = self.IFC_model.createIfcOwnerHistory(p_o, application, "READWRITE", None, None, None, None, timestamp)

        return ownerHistory

    def write_file(self):
        self.IFC_model.write(self.properties["file_destination"])

    def create_IFC_classes(self):
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
            IFC_name = None
            if "name_attribute" in self.properties and self.properties["name_attribute"] in obj.attributes:
                IFC_name = obj.attributes[self.properties["name_attribute"]]

            # TODO children

            # TODO parents

            # TODO geometry_type

            # geometry_lod
            lod = 0
            geometry = None
            for geom in obj.geometry:
                if geom.lod > lod:
                    geometry = geom
                    lod = geom.lod

            IFC_children = []
            if geometry.surfaces:
                for surface_id in geometry.surfaces:
                    IFC_child_class = JSON_TO_IFC[geometry.surfaces[surface_id]["type"]][0]
                    child_data = {"GlobalId": ifcopenshell.guid.new(),
                                  "Name": IFC_child_class
                                  }
                    # CREATE ENTITY
                    surface_geometry = self.geometry.create_IFC_surface(self.IFC_model, geometry, surface_id)
                    if surface_geometry:
                        child_data["Representation"] = self.create_IFC_representation(surface_geometry)
                    IFC_children.append(self.IFC_model.create_entity(IFC_child_class, **child_data))

            else:
                IFC_geometry = self.geometry.create_IFC_geometry(self.IFC_model, geometry)
                if IFC_geometry:
                    data["Representation"] = self.create_IFC_representation(IFC_geometry)
            data["GlobalId"] = ifcopenshell.guid.new()
            data["Name"] = IFC_name

            IFC_object = self.IFC_model.create_entity(IFC_class, **data)
            # Define aggregation
            self.IFC_model.create_entity("IfcRelAggregates",
                                         **{"GlobalId": ifcopenshell.guid.new(),
                                            "RelatedObjects": [IFC_object],
                                            "RelatingObject": self.IFC_site}
                                         )
            if IFC_children:
                self.IFC_model.create_entity("IfcRelAggregates",
                                         **{"GlobalId": ifcopenshell.guid.new(),
                                            "RelatedObjects": IFC_children,
                                            "RelatingObject": IFC_object})

            self.create_property_set(obj.attributes, IFC_object)

    def create_IFC_representation(self, IFC_geometry):
        shape_representation = self.IFC_model.create_entity("IfcShapeRepresentation",
                                                            self.IFC_representation_sub_context, 'Body', 'Brep',
                                                            [IFC_geometry])
        product_representation = self.IFC_model.create_entity("IfcProductDefinitionShape",
                                                              Representations=[shape_representation])
        return product_representation

    def create_property_set(self, CJ_attributes, IFC_entity):
        IFC_object_properties = []
        for property, val in CJ_attributes.items():
            if val == None:
                continue

            if type(val) == int:
                IFC_type = "IfcInteger"
            elif type(val) == float:
                IFC_type = "IfcReal"
            elif type(val) == bool:
                IFC_type = "IfcBoolean"
            else:
                IFC_type = "IfcText"

            IFC_object_properties.append(
                self.IFC_model.createIfcPropertySingleValue(property, property,
                                                            self.IFC_model.create_entity(IFC_type, val), None)
            )
        property_set = self.IFC_model.createIfcPropertySet(ifcopenshell.guid.new(),
                                                           self.properties["owner_history"],
                                                           "CityJSON_attributes",
                                                           None,
                                                           IFC_object_properties)

        self.IFC_model.createIfcRelDefinesByProperties(ifcopenshell.guid.new(),
                                                       self.properties["owner_history"],
                                                       None, None, [IFC_entity],
                                                       property_set)
