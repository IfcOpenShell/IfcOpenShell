import ifcopenshell
from brickschema.graph import Graph


class Generator:
    def __init__(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.schema = Graph()
        self.schema.load_file("Brick.ttl")  # stable 1.3 loaded from external file

    def generate(self):
        classification = self.file.create_entity(
            "IfcClassification",
            **{
                "Source": "Brick",
                "Edition": "August-11",
                "EditionDate": "2023-08-11",
                "Name": "Brick",
                "Description": "",
                "Location": "https://brickschema.org/schema/Brick",
                "ReferenceTokens": [],
            }
        )

        query = self.schema.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            SELECT ?entity ?label ?definition WHERE {
                {
                    ?entity rdfs:subClassOf* brick:Equipment .
                } UNION {
                    ?entity rdfs:subClassOf* brick:Location .
                } UNION {
                    ?entity rdfs:subClassOf* brick:Collection .
                } UNION {
                    ?entity rdfs:subClassOf* brick:Alarm .
                } UNION {
                    ?entity rdfs:subClassOf* brick:Sensor .
                }
                FILTER NOT EXISTS {
                    ?entity owl:deprecated true .
                } 
                OPTIONAL {
                    ?entity rdfs:label ?label .
                    ?entity skos:definition ?definition .
                }
            }
            GROUP BY ?entity
            """
        )

        # create references dictionary
        references = {}

        for row in query:
            # location is the entity URI
            location = row.get("entity")

            # description is the entity's definition
            description = row.get("definition")
            if not description:
                description = ""

            # name is the entity's label if it exists, else the name in the URI
            name = row.get("label")
            if not name:
                name = location.split("#")[-1].replace("_", " ")

            # create the reference
            ref = self.file.create_entity(
                "IfcClassificationReference",
                **{"Location": location, "Description": description, "Identification": name, "Name": name}
            )

            # get all parents of the entity
            query = self.schema.query(
                """
                PREFIX brick: <https://brickschema.org/schema/Brick#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?parent WHERE {
                    brick:{entity} rdfs:subClassOf ?parent .
                }
                """.replace(
                    "{entity}", location.split("#")[-1]
                )
            )
            # filter parents for the brick entity
            for row in query:
                parent = row.get("parent").toPython()
                if "brickschema.org" in parent and parent in references.keys():
                    # some parents are not a brick type, so those should be ignored
                    # some entities have multiple parents that are a brick type
                    # since the query traverses down the graph, we can assume at least one parent has been seen, so pick that one
                    # if no parent is found, then it must mean it is the top level of what was queried
                    break
                parent = None

            # assign reference source
            if parent:
                ref.ReferencedSource = references[parent]
            else:
                ref.ReferencedSource = classification

            # save this reference for future reference sources
            references[location.toPython()] = ref

        self.file.write("Brick.ifc")


generator = Generator()
generator.generate()
