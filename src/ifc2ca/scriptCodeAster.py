import json
import codecs

def getGroupName(name):
    info = name.split('|')
    sortName = ''.join(c for c in info[0] if c.isupper())
    return str(sortName + '_' + info[1])

def createCommFile(FILENAME, FILENAMEASTER):

    AccelOfGravity = 9.806 # m/sec^2

    # Read data from input file
    with open(FILENAME) as dataFile:
        data = json.load(dataFile)

    elements = data['elements']
    connections = data['connections']

    edgeGroupNames = tuple([getGroupName(str(el['ifcName'])) for el in elements if el['geometryType'] == 'line'])
    faceGroupNames = tuple([getGroupName(str(el['ifcName'])) for el in elements if el['geometryType'] == 'surface'])

    unifiedConnection = False
    rigidLinkGroupNames = []
    for conn in connections:
        conn['relatedGroupNames'] = tuple([getGroupName(str(rel['relatingElement'])) + '_0D_to_' + getGroupName(str(conn['ifcName'])) for rel in conn['relatedElements']])
        if not conn['appliedCondition'] and len(conn['relatedGroupNames']) == 1:
            conn['appliedCondition'] = {
                'dx': True,
                'dy': True,
                'dz': True
            }
        if len(conn['relatedGroupNames']) > 1:
            unifiedConnection = True
        rigidLinkGroupNames.extend([getGroupName(str(rel['relatingElement'])) + '_1D_to_' + getGroupName(str(conn['ifcName'])) for rel in conn['relatedElements'] if rel['eccentricity']])
    rigidLinkGroupNames = tuple(rigidLinkGroupNames)

    # Define file to write command file for code_aster
    f = open(FILENAMEASTER, 'w')

    f.write('# Command file generated for ifcOpenShell/BlenderBim\n')
    f.write('# Aether Engineering - www.aethereng.com\n')
    f.write('\n')

    f.write('# Linear Static Analysis With Self-Weight\n')

    f.write(
'''
# STEP: INITIALIZE STUDY
DEBUT(
    PAR_LOT = 'NON'
)
'''
    )

    f.write(
'''
# STEP: READ MED FILE
mesh = LIRE_MAILLAGE(
    FORMAT = 'MED'
)
'''
    )

    f.write(
'''
# STEP: DEFINE MODEL
model = AFFE_MODELE(
    MAILLAGE = mesh,
    AFFE = (
        _F(
            TOUT = 'OUI',
            PHENOMENE = 'MECANIQUE',
            MODELISATION = '3D'
        ),'''
    )

    if faceGroupNames:
        template = \
        '''
        _F(
            GROUP_MA = {group_names},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'DKT'
        ),'''

        context = {
            'group_names': faceGroupNames
        }

        f.write(template.format(**context))

    if edgeGroupNames:
        template = \
        '''
        _F(
            GROUP_MA = {group_names},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        ),'''

        context = {
            'group_names': edgeGroupNames
        }

        f.write(template.format(**context))

    if rigidLinkGroupNames:
        template = \
        '''
        _F(
            GROUP_MA = {group_names},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        ),'''

        context = {
            'group_names': rigidLinkGroupNames
        }

        f.write(template.format(**context))

    f.write(
'''
    )
)\n
'''
    )


    f.write('# STEP: DEFINE MATERIALS')

    for i,el in enumerate(elements):
        template = \
'''
{matNameID} = DEFI_MATERIAU(
    ELAS = _F(
        E = {youngModulus},
        NU = {poissonRatio},
        RHO = {massDensity}
    )
)
'''
        if 'poissonRatio' in el['material']['mechProps']:
            poissonRatio = el['material']['mechProps']['poissonRatio']
        else:
            if 'shearModulus' in el['material']['mechProps']:
                poissonRatio = (el['material']['mechProps']['youngModulus'] / 2.0 / el['material']['mechProps']['shearModulus']) - 1
            else:
                poissonRation = 0

        context = {
            'matNameID': 'matF'+ '_%s' % i,
            'youngModulus': float(el['material']['mechProps']['youngModulus']),
            'poissonRatio': float(poissonRatio),
            'massDensity': float(el['material']['commonProps']['massDensity'])
        }

        f.write(template.format(**context))


    f.write(
'''
material = AFFE_MATERIAU(
    MAILLAGE = mesh,
    AFFE = ('''
    )

    for i,el in enumerate(elements):
        template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            MATER = {matNameID},
        ),'''

        context = {
            'group_name': getGroupName(str(el['ifcName'])),
            'matNameID': 'matF'+ '_%s' % i
        }

        f.write(template.format(**context))

    if rigidLinkGroupNames:
        template = \
        '''
        _F(
            GROUP_MA = {group_names},
            MATER = {matNameID},
        ),'''

        context = {
            'group_names': rigidLinkGroupNames,
            'matNameID': 'matF_0'
        }

        f.write(template.format(**context))

    f.write(
'''
    )
)
'''
    )


    f.write(
'''
# STEP: DEFINE ELEMENTS
element = AFFE_CARA_ELEM(
    MODELE = model,
    POUTRE = ('''
    )

    for el in [el for el in elements if el['geometryType'] == 'line']:
        if el['profile']['profileShape'] == 'rectangular':
            template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = {profileDimensions}
        ),'''

            context = {
                'group_name': getGroupName(str(el['ifcName'])),
                'profileDimensions': (el['profile']['xDim'], el['profile']['yDim'])
            }

            f.write(template.format(**context))

        elif el['profile']['profileShape'] == 'iSymmetrical':
            template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            SECTION = 'GENERALE',
            CARA = ('A', 'IY', 'IZ', 'JX'),
            VALE = {profileProperties}
        ),'''

            context = {
                'group_name': getGroupName(str(el['ifcName'])),
                'profileProperties': (
                    el['profile']['mechProps']['crossSectionArea'],
                    el['profile']['mechProps']['momentOfInertiaY'],
                    el['profile']['mechProps']['momentOfInertiaZ'],
                    el['profile']['mechProps']['torsionalConstantX']
                )
            }

            f.write(template.format(**context))

    if rigidLinkGroupNames:
        template = \
        '''
        _F(
            GROUP_MA = {group_names},
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = {profileDimensions}
        ),'''

        context = {
            'group_names': rigidLinkGroupNames,
            'profileDimensions': (1, 1)
        }

        f.write(template.format(**context))

    f.write(
'''
    ),
    COQUE = ('''
    )

    for el in [el for el in elements if el['geometryType'] == 'surface']:

        template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            EPAIS = {thickness},
            VECTEUR = {orientationVector}
        ),'''

        context = {
            'group_name': getGroupName(str(el['ifcName'])),
            'thickness': el['thickness'],
            'orientationVector': (
                el['geometry'][1][0] - el['geometry'][0][0],
                el['geometry'][1][1] - el['geometry'][0][1],
                el['geometry'][1][2] - el['geometry'][0][2]
            )
        }

        f.write(template.format(**context))

    f.write(
'''
    ),'''
    )

    #     f.write(
    # '''
    #     ORIENTATION = ('''
    #     )
    #
    #     for el in [el for el in elements if el['geometryType'] == 'line']:
    #
    #         template = \
    #         '''
    #         _F(
    #             GROUP_MA = '{group_name}',
    #             CARA = ('ANGL_VRIL',),
    #             VALE = {rotation}
    #         ),'''
    #
    #         context = {
    #             'group_name': getGroupName(str(el['ifcName'])),
    #             'rotation': 0 # (el['rotation'],)
    #         }
    #
    #         f.write(template.format(**context))
    #
    #     f.write(
    # '''
    #     ),'''
    #     )

    f.write(
'''
)\n
'''
    )


    f.write('# STEP: DEFINE GROUND BOUNDARY CONDITIONS')

    f.write(
'''
grdSupps = AFFE_CHAR_MECA(
    MODELE = model,
    DDL_IMPO = ('''
    )

    for conn in [conn for conn in connections if conn['appliedCondition']]:
        f.write(
        '''
        _F(
            GROUP_NO = '%s',''' % conn['relatedGroupNames'][0]
        )
        for dof in conn['appliedCondition']:
            if conn['appliedCondition'][dof]:
                f.write(
        '''
            %s = 0,''' % (str(dof).upper())
                )
        f.write(
        '''
        ),'''
        )

    f.write(
        '''
    ),'''
    )

    if unifiedConnection:
        f.write(
    '''
    LIAISON_UNIF = ('''
        )

        for conn in [conn for conn in connections if len(conn['relatedGroupNames']) > 1]:
            template = \
        '''
        _F(
            GROUP_NO = {group_names},
            DDL = ('DX', 'DY', 'DZ', 'DRX', 'DRY', 'DRZ')
        ),'''

            context = {
                'group_names': conn['relatedGroupNames']
            }

            f.write(template.format(**context))

        f.write(
    '''
    ),'''
        )

    if rigidLinkGroupNames:
        f.write(
    '''
    LIAISON_SOLIDE = ('''
        )

        for groupName in rigidLinkGroupNames:
            template = \
        '''
        _F(
            GROUP_MA = '{group_name}'
        ),'''

            context = {
                'group_name': groupName
            }

            f.write(template.format(**context))

        f.write(
    '''
    ),'''
        )

    f.write(
    '''
)'''
    )

    template = \
'''
# STEP: DEFINE LOAD
exPESA = AFFE_CHAR_MECA(
    MODELE = model,
    PESANTEUR = _F(
        GRAVITE = {AccelOfGravity},
        DIRECTION = (0.,0.,-1.)
    )
)
'''
    context = {
        'AccelOfGravity': AccelOfGravity,
    }

    f.write(template.format(**context))


    f.write(
'''
# STEP: RUN ANALYSIS
res_Bld = MECA_STATIQUE(
    MODELE = model,
    CHAM_MATER = material,
    CARA_ELEM = element,
    EXCIT = (
        _F(
            CHARGE = grdSupps
        ),
        _F(
            CHARGE = exPESA
        )
    )
)
'''
    )


#     f.write(
# '''
# # STEP: POST-PROCESSING
# res_Bld = CALC_CHAMP(
#     reuse = res_Bld,
#     RESULTAT = res_Bld,
#     CONTRAINTE = ('SIEF_ELNO', 'SIGM_ELNO', 'EFGE_ELNO',),
#     FORCE = ('REAC_NODA', 'FORC_NODA',),
# )
# '''
#     )
#
#     template = \
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
#     context = {
#         'massList': massList,
#     }
#
#     f.write(template.format(**context))
#
#     f.write(
# '''
# IMPR_TABLE(
#     UNITE = 10,
# 	TABLE = FaceMass,
#     SEPARATEUR = ',',
#     NOM_PARA = ('LIEU', 'MASSE', 'CDG_X', 'CDG_Y', 'CDG_Z'),
# 	# FORMAT_R = '1PE15.6',
# )
# '''
#     )
#
#     f.write(
# '''
# # STEP: REACTION EXTRACTION AT THE BASE
# Reacs = POST_RELEVE_T(
#     ACTION = _F(
#         INTITULE = 'sumReac',
#         GROUP_NO = 'grdSupps',
#         RESULTAT = res_Bld,
#         NOM_CHAM = 'REAC_NODA',
#         RESULTANTE = ('DX','DY','DZ',),
#         # MOMENT = ('DRX','DRY','DRZ',),
#         # POINT = (0,0,0,),
#         OPERATION = 'EXTRACTION',
#     ),
# )
# '''
#     )
#
#     f.write(
# '''
# IMPR_TABLE(
#     UNITE = 10,
#     TABLE = Reacs,
#     SEPARATEUR = ',',
#     NOM_PARA = ('INTITULE', 'RESU', 'NOM_CHAM', 'INST', 'DX','DY','DZ'),
#     # FORMAT_R = '1PE12.3',
# )
# '''
#     )
#
    f.write(
'''
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
'''
    )

    f.write(
'''
# STEP: CONCLUDE STUDY
FIN()
'''
    )

    f.close()

if __name__ == '__main__':
    fileNames = ['cantilever_01', 'beam_01', 'portal_01', 'building_01', 'building-frame_01'];
    files = [fileNames[3]]

    for fileName in files:
        FILENAME = 'examples/' + fileName + '/' + fileName + '.json'
        FILENAMEASTER = 'examples/' + fileName + '/CA_input_00.comm'
        createCommFile(FILENAME, FILENAMEASTER)
