# Ifc2CA - IFC Code_Aster utility
# Copyright (C) 2020, 2021 Ioannis P. Christovasilis <ipc@aethereng.com>
#
# This file is part of Ifc2CA.
#
# Ifc2CA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc2CA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc2CA.  If not, see <http://www.gnu.org/licenses/>.

import json
import numpy as np
import itertools
from pathlib import Path

flatten = itertools.chain.from_iterable

ScaleFactor = 1.0

AccelOfGravity = 9.806 * 1000


class COMMANDFILE:
    def __init__(self, dataFilename, asterFilename):
        self.dataFilename = dataFilename
        self.asterFilename = asterFilename
        self.create()

    def getGroupName(self, name):
        if "|" in name:
            info = name.split("|")
            sortName = "".join(c for c in info[0] if c.isupper())
            return f"{sortName[2:]}_{info[1]}"
        else:
            return name

    def create(self):
        # Read data from input file
        with open(self.dataFilename) as dataFile:
            data = json.load(dataFile)

        elements = data["elements"]
        connections = data["connections"]
        # --> Delete this reference data and repopulate it with the objects
        # while going through elements
        for conn in connections:
            conn["relatedElements"] = []
        for el in elements:
            for rel in el["connections"]:
                conn = [c for c in connections if c["referenceName"] == rel["relatedConnection"]][0]
                conn["relatedElements"].append(rel)
        # End <--

        materials = data["db"]["materials"]
        profiles = data["db"]["profiles"]

        edgeGroupNames = tuple(
            [self.getGroupName(el["referenceName"]) for el in elements if el["geometryType"] == "line"]
        )
        faceGroupNames = tuple(
            [self.getGroupName(el["referenceName"]) for el in elements if el["geometryType"] == "surface"]
        )

        rigidLinkGroupNames = []
        for conn in connections:
            rigidLinkGroupNames.extend(
                [
                    self.getGroupName(rel["relatingElement"]) + "_1DR_" + self.getGroupName(conn["referenceName"])
                    for rel in conn["relatedElements"]
                    if rel["eccentricity"]
                ]
            )
        rigidLinkGroupNames = tuple(rigidLinkGroupNames)

        # Define file to write command file for code_aster
        f = open(self.asterFilename, "w")

        f.write("# Command file generated by IfcOpenShell/ifc2ca scripts\n")
        f.write("\n")

        f.write("# Linear Static Analysis With Self-Weight\n")

        f.write(
            """
# STEP: INITIALIZE STUDY
DEBUT(
    PAR_LOT = 'NON'
)
"""
        )

        f.write(
            """
# STEP: READ MED FILE
mesh = LIRE_MAILLAGE(
    FORMAT = 'MED',
    UNITE = 20
)
"""
        )

        f.write(
            """
# STEP: DEFINE MODEL
model = AFFE_MODELE(
    MAILLAGE = mesh,
    AFFE = (
        _F(
            TOUT = 'OUI',
            PHENOMENE = 'MECANIQUE',
            MODELISATION = '3D'
        ),"""
        )

        if faceGroupNames:
            template = """
        _F(
            GROUP_MA = {groupNames},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'DKT'
        ),"""

            context = {"groupNames": faceGroupNames}

            f.write(template.format(**context))

        if edgeGroupNames:
            template = """
        _F(
            GROUP_MA = {groupNames},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        ),"""

            context = {"groupNames": edgeGroupNames}

            f.write(template.format(**context))

        if rigidLinkGroupNames:
            template = """
        _F(
            GROUP_MA = {groupNames},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        ),"""

            context = {"groupNames": rigidLinkGroupNames}

            f.write(template.format(**context))

        f.write(
            """
    )
)\n
"""
        )

        f.write("# STEP: DEFINE MATERIALS")

        for i, material in enumerate(materials):
            template = """
{matNameID} = DEFI_MATERIAU(
    ELAS = _F(
        E = {youngModulus},
        NU = {poissonRatio},
        RHO = {massDensity}
    )
)
"""
            if "poissonRatio" in material["mechProps"]:
                poissonRatio = material["mechProps"]["poissonRatio"]
            else:
                if "shearModulus" in material["mechProps"]:
                    poissonRatio = (
                        material["mechProps"]["youngModulus"] / 2.0 / material["mechProps"]["shearModulus"]
                    ) - 1
                else:
                    poissonRatio = 0.0

            context = {
                "matNameID": "mat" + "_%s" % i,
                "youngModulus": float(material["mechProps"]["youngModulus"]) * ScaleFactor**2,
                "poissonRatio": float(poissonRatio),
                "massDensity": float(material["commonProps"]["massDensity"]) * ScaleFactor**3,
            }

            f.write(template.format(**context))

        f.write(
            """
material = AFFE_MATERIAU(
    MAILLAGE = mesh,
    AFFE = ("""
        )

        for i, material in enumerate(materials):
            template = """
        _F(
            GROUP_MA = {groupNames},
            MATER = {matNameID},
        ),"""

            context = {
                "groupNames": tuple([self.getGroupName(rel) for rel in material["relatedElements"]]),
                "matNameID": "mat" + "_%s" % i,
            }

            f.write(template.format(**context))

        if rigidLinkGroupNames:
            template = """
        _F(
            GROUP_MA = {groupNames},
            MATER = {matNameID},
        ),"""

            context = {"groupNames": rigidLinkGroupNames, "matNameID": "mat_0"}

            f.write(template.format(**context))

        f.write(
            """
    )
)
"""
        )

        f.write(
            """
# STEP: DEFINE ELEMENTS
element = AFFE_CARA_ELEM(
    MODELE = model,
    POUTRE = ("""
        )

        for profile in profiles:
            if profile["profileShape"] == "rectangular" and profile["profileType"] == "AREA":
                template = """
        _F(
            GROUP_MA = {groupNames},
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = {profileDimensions}
        ),"""

                context = {
                    "groupNames": tuple([self.getGroupName(rel) for rel in profile["relatedElements"]]),
                    "profileDimensions": (
                        profile["xDim"] / ScaleFactor,
                        profile["yDim"] / ScaleFactor,
                    ),
                }

                f.write(template.format(**context))

            elif profile["profileShape"] == "iSymmetrical" and profile["profileType"] == "AREA":
                template = """
        _F(
            GROUP_MA = {groupNames},
            SECTION = 'GENERALE',
            CARA = ('A', 'IY', 'IZ', 'JX'),
            VALE = {profileProperties}
        ),"""

                context = {
                    "groupNames": tuple([self.getGroupName(rel) for rel in profile["relatedElements"]]),
                    "profileProperties": (
                        profile["mechProps"]["crossSectionArea"] / ScaleFactor**2,
                        profile["mechProps"]["momentOfInertiaY"] / ScaleFactor**4,
                        profile["mechProps"]["momentOfInertiaZ"] / ScaleFactor**4,
                        profile["mechProps"]["torsionalConstantX"] / ScaleFactor**4,
                    ),
                }

                f.write(template.format(**context))

        if rigidLinkGroupNames:
            template = """
        _F(
            GROUP_MA = {groupNames},
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = {profileDimensions}
        ),"""

            context = {"groupNames": rigidLinkGroupNames, "profileDimensions": (1, 1)}

            f.write(template.format(**context))

        f.write(
            """
    ),
    COQUE = ("""
        )

        for el in [el for el in elements if el["geometryType"] == "surface"]:

            template = """
        _F(
            GROUP_MA = '{groupName}',
            EPAIS = {thickness},
            VECTEUR = {localAxisX}
        ),"""

            context = {
                "groupName": self.getGroupName(el["referenceName"]),
                "thickness": el["thickness"] / ScaleFactor,
                "localAxisX": tuple(el["orientation"][0]),
            }

            f.write(template.format(**context))

        f.write(
            """
    ),"""
        )

        f.write(
            """
    ORIENTATION = ("""
        )

        for el in [el for el in elements if el["geometryType"] == "line"]:

            template = """
        _F(
            GROUP_MA = '{groupName}',
            CARA = 'VECT_Y',
            VALE = {localAxisY}
        ),"""

            context = {
                "groupName": self.getGroupName(el["referenceName"]),
                "localAxisY": tuple(el["orientation"][1]),
            }

            f.write(template.format(**context))

        f.write(
            """
    ),"""
        )

        f.write(
            """
)\n
"""
        )

        f.write("# STEP: DEFINE SUPPORTS AND CONSTRAINTS")

        f.write(
            """
liaisons = AFFE_CHAR_MECA(
    MODELE = model,
    DDL_IMPO = (
        _F(
            GROUP_NO = 'grdSupps',
            DX = 0.0,
            DY = 0.0,
            DZ = 0.0,
            DRX = 0.0,
            DRY = 0.0,
            DRZ = 0.0
        )
    ),"""
        )

        if rigidLinkGroupNames:
            f.write(
                """
    LIAISON_SOLIDE = ("""
            )

            for groupName in rigidLinkGroupNames:
                template = """
        _F(
            GROUP_MA = '{groupName}'
        ),"""

                context = {"groupName": groupName}

                f.write(template.format(**context))

            f.write(
                """
    ),"""
            )

        f.write(
            """
)
"""
        )

        template = """
# STEP: DEFINE LOAD
gravLoad = AFFE_CHAR_MECA(
    MODELE = model,
    PESANTEUR = _F(
        GRAVITE = {AccelOfGravity},
        DIRECTION = (0.0, 0.0, -1.0)
    )
)
"""
        context = {
            "AccelOfGravity": AccelOfGravity,
        }

        f.write(template.format(**context))

        f.write(
            """
# STEP: RUN ANALYSIS
res_Bld = MECA_STATIQUE(
    MODELE = model,
    CHAM_MATER = material,
    CARA_ELEM = element,
    EXCIT = (
        _F(
            CHARGE = liaisons
        ),
        _F(
            CHARGE = gravLoad
        )
    )
)
"""
        )

        #         f.write(
        # '''
        # # STEP: POST-PROCESSING
        # res_Bld = CALC_CHAMP(
        #     reuse = res_Bld,
        #     RESULTAT = res_Bld,
        #     # CONTRAINTE = ('SIEF_ELNO', 'SIGM_ELNO', 'EFGE_ELNO',),
        #     FORCE = ('REAC_NODA', 'FORC_NODA',)
        # )
        # '''
        #         )
        #
        #         template = \
        # '''
        # # STEP: MASS EXTRACTION FOR EACH ASSEMBLE
        # FaceMass = POST_ELEM(
        # 	TITRE = 'TotMass',
        #     MODELE = model,
        #     CARA_ELEM = element,
        #     CHAM_MATER = material,
        #     MASS_INER = _F(
        #         GROUP_MA = {massList},
        #     ),
        # )\n'''
        #
        #         context = {
        #             'massList': massList,
        #         }
        #
        #         f.write(template.format(**context))
        #
        #         f.write(
        # '''
        # IMPR_TABLE(
        #     UNITE = 10,
        # 	TABLE = FaceMass,
        #     SEPARATEUR = ',',
        #     NOM_PARA = ('LIEU', 'MASSE', 'CDG_X', 'CDG_Y', 'CDG_Z'),
        # 	# FORMAT_R = '1PE15.6',
        # )
        # '''
        #         )
        #
        #         template = \
        # '''
        # # STEP: REACTION EXTRACTION AT THE BASE
        # Reacs = POST_RELEVE_T(
        #     ACTION = _F(
        #         INTITULE = 'sumReac',
        #         GROUP_NO = {groupNames},
        #         RESULTAT = res_Bld,
        #         NOM_CHAM = 'REAC_NODA',
        #         RESULTANTE = ('DX','DY','DZ',),
        #         MOMENT = ('DRX','DRY','DRZ',),
        #         POINT = (0,0,0,),
        #         OPERATION = 'EXTRACTION'
        #     )
        # )
        # '''
        #
        #         context = {
        #             'groupNames': point0DGroupNames,
        #         }
        #
        #         f.write(template.format(**context))
        #
        #         f.write(
        # '''
        # IMPR_TABLE(
        #     UNITE = 10,
        #     TABLE = Reacs,
        #     SEPARATEUR = ',',
        #     # NOM_PARA = ('INTITULE', 'RESU', 'NOM_CHAM', 'INST', 'DX','DY','DZ'),
        #     FORMAT_R = '1PE12.3',
        # )
        # '''
        #         )
        #
        f.write(
            """
# STEP: DEFORMED SHAPE EXTRACTION
IMPR_RESU(
    FORMAT = 'MED',
	UNITE = 80,
	RESU = _F(
 		RESULTAT = res_Bld,
 		NOM_CHAM = ('DEPL',), # 'REAC_NODA', 'FORC_NODA',
 		NOM_CHAM_MED = ('Bld_DISP',), #  'Bld_REAC', 'Bld_FORC'
    )
)
"""
        )

        f.write(
            """
# STEP: CONCLUDE STUDY
FIN()
"""
        )

        f.close()


if __name__ == "__main__":
    fileNames = ["test"]
    files = fileNames

    for fileName in files:
        BASE_PATH = Path("/home/jesusbill/Dev-Projects/github.com/IfcOpenShell/analysis-models/models/")
        DATAFILENAME = BASE_PATH / fileName / f"{fileName}.json"
        ASTERFILENAME = BASE_PATH / fileName / f"{fileName}.comm"
        COMMANDFILE(DATAFILENAME, ASTERFILENAME)
