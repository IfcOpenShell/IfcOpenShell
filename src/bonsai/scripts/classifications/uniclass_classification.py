import os
import ifcopenshell
import pandas as pd

directory_path = "uniclass/"

edition = "July 2023"

ifc = ifcopenshell.file(schema="IFC4")
classification = ifc.create_entity(
    "IfcClassification",
    Source="RIBA Enterprises Ltd",
    Edition=edition,
    EditionDate="2023-07-01",
    Name="Uniclass",
    Description="Uniclass is a unified classification system made up of a set of tables that can be used by different parts of the industry in various ways.",
    Location="https://uniclass.thenbs.com/",
    ReferenceTokens=["_"],
)

references = {}

tables = [
    ("Ac", "Activities"),
    ("Co", "Complexes"),
    ("En", "Entities"),
    ("SL", "Spaces / Locations"),
    ("EF", "Elements / Functions"),
    ("Ss", "Systems"),
    ("Pr", "Products"),
    ("TE", "Tools and equipment"),
    ("PM", "Project management"),
    ("FI", "Form of information"),
    ("Ro", "Roles"),
    ("Ma", "Materials"),
    ("PC", "Properties and characteristics"),
    ("Zz", "CAD"),
]

for identification, name in tables:
    ref = ifc.create_entity("IfcClassificationReference", Identification=identification, Name=name)
    references[identification] = ref
    ref.ReferencedSource = classification

for filename in os.listdir(directory_path):
    if filename.endswith(".xlsx") and "change-log" not in filename and "codes-not-in-use" not in filename:
        file_path = os.path.join(directory_path, filename)
        df = pd.read_excel(file_path, header=2)
        for index, row in df.iterrows():
            identification = row["Code"]
            name = row["Title"]
            ref = ifc.create_entity("IfcClassificationReference", Identification=identification, Name=name)
            references[identification] = ref
            parent = "_".join(identification.split("_")[0:-1])
            if parent in references:
                ref.ReferencedSource = references[parent]
            else:
                ref.ReferencedSource = classification

ifc.write(f"Uniclass {edition}.ifc")
