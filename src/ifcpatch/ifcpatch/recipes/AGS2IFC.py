# IfcPatch - IFC patching utiliy
# Copyright (C) 2025 David Bayliss <david.bayliss@transport.nsw.gov.au>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.


import os
import csv
import numpy as np
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.style
import ifcopenshell.api.context
import ifcopenshell.api.document
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.util.shape_builder
from itertools import cycle
from ifcopenshell.util.shape_builder import V


class Patcher:
    def __init__(
        self,
        file,
        logger,
        ags_file: str,
        docs_dir: str = ".",
    ):
        """Converts AGS to IFC

        This is for AGS version 3.

        :param ags_file: The AGS file to convert.
        :filter_glob ags_file: *.ags
        :param docs_dir: The directory URI where documents are stored

        Example:

        .. code:: python

            result = ifcpatch.execute({"input": fn, "file": model, "recipe": "ExtractPropertiesToSQLite"})
            ifcpatch.write(result, "output.sqlite")
        """
        self.file = file
        self.logger = logger
        self.ags_file = ags_file
        self.docs_dir = docs_dir

    def patch(self):
        model = ifcopenshell.api.project.create_file(version="IFC4X3")
        project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="My Project")

        length = ifcopenshell.api.unit.add_si_unit(model, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(model, units=[length])

        context = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
        )
        site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="My Site")
        ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])

        doc_files = list(os.listdir(self.docs_dir))
        doc_references = {}

        def read_csv_line(line: str) -> list[str]:
            r = csv.reader([line])
            return next(iter(r))

        ags = {}
        with open(self.ags_file, "r") as f:
            line_type = None
            group = None
            group_line = -1
            unit_line = -1
            header = []
            for i, line in enumerate(f.readlines()):
                if line.startswith('"**'):
                    line_type = "GROUP"
                    r = csv.reader([line])
                    group_line = i
                    group = read_csv_line(line)[0].strip("**?")
                    # print(group)
                    ags.setdefault(group, {})
                elif i == group_line + 1:
                    line_type = "HEADER"
                    r = [x.strip("*?") for x in read_csv_line(line) if x]
                    ags[group]["header"] = r
                    header = r
                    # print(r)
                elif line.startswith('"<UNITS'):
                    line_type = "UNITS"
                    unit_line = i
                elif line_type == "HEADER":
                    r = [x.strip("*?") for x in read_csv_line(line) if x]
                    ags[group]["header"].extend(r)
                elif i == unit_line + 1:
                    line_type = "DATA"
                    data = read_csv_line(line)
                    data = {header[i]: data[i] for i in range(len(data))}
                    if data:
                        ags[group].setdefault("data", []).append(data)
                elif line_type == "DATA":
                    data = read_csv_line(line)
                    if data:
                        if data[0] == "<CONT>":
                            old_data = ags[group]["data"][-1]
                            for i in range(len(data)):
                                if i == 0:
                                    continue
                                old_data[header[i]] += data[i]
                        else:
                            data = {header[i]: data[i] for i in range(len(data))}
                            ags[group].setdefault("data", []).append(data)

        # header = ags["PROJ"]["header"]
        # print(header)
        # for item in ags["GOSA"]["data"]:
        #     print(item)
        #
        # for a in sorted(ags):
        #     print(a)

        data = ags["PROJ"]["data"]
        data_dict = data[0]
        # print(data)
        proj_pset = ifcopenshell.api.pset.add_pset(model, product=project, name="PROJ - Project Information")
        ifcopenshell.api.pset.edit_pset(model, pset=proj_pset, properties={k: v for k, v in data_dict.items() if v})

        samp_des_rgb = {
            "SANDSTONE": (176 / 255.0, 164 / 255.0, 67 / 255.0),
            "ASPHALT": (51 / 255.0, 51 / 255.0, 48 / 255.0),
            "CONCRETE": (145 / 255.0, 145 / 255.0, 139 / 255.0),
            "SHALE": (135 / 255.00, 105 / 255.0, 0 / 255.0),
            "SILTSTONE": (135 / 255.0, 46 / 255.0, 0 / 255.0),
            "FILL": (64 / 255.0, 82 / 255.0, 2 / 255.0),
            "INTERBEDDED SILTSTONE AND SANDSTONE": (5 / 255.0, 26 / 255.0, 45 / 255.0),
            "INTERBEDDED SILTSTONE & SANDSTONE": (5 / 255.0, 26 / 255.0, 45 / 255.0),
            "NO_CORE": (10 / 255.0, 10 / 255.0, 10 / 255.0),
            "CORE LOSS": (10 / 255.0, 10 / 255.0, 10 / 255.0),
            "CH": (237 / 255.0, 166 / 255.0, 32 / 255.0),
            "CI": (237 / 255.0, 166 / 255.0, 32 / 255.0),
            "CL": (219 / 255.0, 110 / 255.0, 23 / 255.0),
            "ML": (118 / 255.0, 157 / 255.0, 161 / 255.0),
            "CL-CI": (143 / 255.0, 69 / 255.0, 9 / 255.0),
            "CI-CH": (235 / 255.0, 152 / 255.0, 0 / 255.0),
            "BRECCIA": (232 / 255.0, 72 / 255.0, 197 / 255.0),
            "ARGILLITE": (232 / 255.0, 72 / 255.0, 197 / 255.0),
            "LAMINITE": (232 / 255.0, 72 / 255.0, 197 / 255.0),
            "CLAY": (219 / 255.0, 110 / 255.0, 23 / 255.0),
            "CLAYEY SILTY SAND": (89 / 255.0, 72 / 255.0, 0 / 255.0),
            "CLAYEY SAND": (209 / 255.0, 169 / 255.0, 5 / 255.0),
            "SC": (209 / 255.0, 169 / 255.0, 5 / 255.0),
            "SANDY SILT": (161 / 255.0, 166 / 255.0, 5 / 255.0),
            "SILTY SAND": (102 / 255.0, 100 / 255.0, 0 / 255.0),
            "LINE": (0 / 255.0, 45 / 255.0, 102 / 255.0),
            "SILTY CLAY": (77 / 255.0, 55 / 255.0, 1 / 255.0),
            "SAND": (235 / 255.0, 227 / 255.0, 0 / 255.0),
            "SILTY CLAYEY SAND": (135 / 255.0, 133 / 255.0, 105 / 255.0),
            "SANDY CLAY": (219 / 255.0, 171 / 255.0, 41 / 255.0),
        }

        styles = {}
        for description, rgb in samp_des_rgb.items():
            style = ifcopenshell.api.style.add_style(model)
            ifcopenshell.api.style.add_surface_style(
                model,
                style=style,
                ifc_class="IfcSurfaceStyleShading",
                attributes={
                    "SurfaceColour": {"Name": None, "Red": rgb[0], "Green": rgb[1], "Blue": rgb[2]},
                    "Transparency": 0,  # 0 is opaque, 1 is transparent
                },
            )
            styles[description] = style

        elements = []
        header = ags["HOLE"]["header"]
        # print(header)
        # print(len(header))
        for item in ags["HOLE"]["data"]:
            if not item["HOLE_LOCX"]:
                continue
            if not item["HOLE_LOCY"]:
                continue
            if not item["HOLE_LOCZ"]:
                continue
            print(item["HOLE_ID"], item["HOLE_LOCX"], item["HOLE_LOCY"])
            element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBorehole", name=item["HOLE_ID"])
            elements.append(element)
            matrix = np.eye(4)
            matrix[0][3] = float(item["HOLE_LOCX"])
            matrix[1][3] = float(item["HOLE_LOCY"])
            matrix[2][3] = float(item["HOLE_LOCZ"])
            ifcopenshell.api.geometry.edit_object_placement(model, product=element, matrix=matrix)
            hole_pset = ifcopenshell.api.pset.add_pset(model, product=element, name="HOLE")
            ifcopenshell.api.pset.edit_pset(model, pset=hole_pset, properties={k: v for k, v in item.items() if v})
            # print(matrix)

            for file in doc_files:
                if item["HOLE_ID"].lower() in file.lower():
                    if not (reference := doc_references.get(file)):
                        document = ifcopenshell.api.document.add_information(model)
                        ifcopenshell.api.document.edit_information(
                            model,
                            information=document,
                            attributes={
                                "Identification": file,
                                "Name": file,
                                "Location": os.path.join(self.docs_dir, file),
                            },
                        )
                        reference = ifcopenshell.api.document.add_reference(model, information=document)
                        doc_references[file] = reference
                    ifcopenshell.api.document.assign_document(model, products=[element], document=reference)

            subelements = []
            for sample in ags["GEOL"]["data"]:
                if sample["HOLE_ID"] != item["HOLE_ID"]:
                    continue
                if not sample["GEOL_LEG"]:
                    sample["GEOL_LEG"] = "Unknown"
                    continue

                diameter = 150 / 1000
                depth = float(sample["GEOL_BASE"]) - float(sample["GEOL_TOP"])
                subelement = ifcopenshell.api.root.create_entity(
                    model,
                    ifc_class="IfcGeotechnicalStratum",
                    predefined_type="SOLID",
                    name=sample["GEOL_LEG"] + f"_{len(subelements)}",
                )

                samp_pset = ifcopenshell.api.pset.add_pset(
                    model, product=subelement, name="GEOL - Stratum Descriptions"
                )
                ifcopenshell.api.pset.edit_pset(
                    model, pset=samp_pset, properties={k: v for k, v in sample.items() if v}
                )

                if "GORA" not in ags:
                    pass
                else:
                    for gora in ags["GORA"]["data"]:
                        if gora["HOLE_ID"] != item["HOLE_ID"]:
                            continue
                        if gora["GEOL_BASE"] != sample["GEOL_BASE"]:
                            continue
                        gora_pset = ifcopenshell.api.pset.add_pset(
                            model, product=subelement, name="GORA - Rock Stratum Descriptions"
                        )
                        ifcopenshell.api.pset.edit_pset(
                            model, pset=gora_pset, properties={k: v for k, v in gora.items() if v}
                        )

                if "GORB" not in ags:
                    pass
                else:
                    for gorb in ags["GORB"]["data"]:
                        if gorb["HOLE_ID"] != item["HOLE_ID"]:
                            continue
                        if gorb["GEOL_BASE"] != sample["GEOL_BASE"]:
                            continue
                        gorb_pset = ifcopenshell.api.pset.add_pset(
                            model, product=subelement, name="GORB - Composite Rock Stratum Descriptions"
                        )
                        ifcopenshell.api.pset.edit_pset(
                            model, pset=gorb_pset, properties={k: v for k, v in gorb.items() if v}
                        )

                if "GOSA" not in ags:
                    pass
                else:
                    for gosa in ags["GOSA"]["data"]:
                        if gosa["HOLE_ID"] != item["HOLE_ID"]:
                            continue
                        if gosa["GEOL_BASE"] != sample["GEOL_BASE"]:
                            continue
                        gosa_pset = ifcopenshell.api.pset.add_pset(
                            model, product=subelement, name="GOSA - Soil Stratum Descriptions"
                        )
                        ifcopenshell.api.pset.edit_pset(
                            model, pset=gosa_pset, properties={k: v for k, v in gosa.items() if v}
                        )

                if "GOSB" not in ags:
                    pass
                else:
                    for gosb in ags["GOSB"]["data"]:
                        if gosb["HOLE_ID"] != item["HOLE_ID"]:
                            continue
                        if gosb["GEOL_BASE"] != sample["GEOL_BASE"]:
                            continue
                        gosb_pset = ifcopenshell.api.pset.add_pset(
                            model, product=subelement, name="GOSB - Composite Soil Stratum Descriptions"
                        )
                        ifcopenshell.api.pset.edit_pset(
                            model, pset=gosb_pset, properties={k: v for k, v in gosb.items() if v}
                        )

                ifcopenshell.api.geometry.edit_object_placement(model, product=subelement, matrix=matrix)
                subelements.append(subelement)
                builder = ifcopenshell.util.shape_builder.ShapeBuilder(model)
                profile = builder.circle()
                cylinder = builder.extrude(profile, magnitude=depth, position=V(0, 0, -float(sample["GEOL_BASE"])))
                representation = builder.get_representation(body, items=[cylinder])
                ifcopenshell.api.geometry.assign_representation(
                    model, product=subelement, representation=representation
                )

                if style := styles.get(sample["GEOL_LEG"], None):
                    ifcopenshell.api.style.assign_representation_styles(
                        model, shape_representation=representation, styles=[style]
                    )
            bh_assemblies = ifcopenshell.api.aggregate.assign_object(
                model, products=subelements, relating_object=element
            )

        ifcopenshell.api.spatial.assign_container(model, relating_structure=site, products=elements)
        self.file_patched = model
