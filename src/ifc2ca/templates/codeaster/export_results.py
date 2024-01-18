# STEP: RESULT EXTRACTION
IMPR_RESU(
    FORMAT="MED",
    UNITE={{unit_number}},
    RESU=_F(
        RESULTAT={{res_Bld}},
        NOM_CHAM=("DEPL", "EFGE_NOEU"),
        NOM_CHAM_MED=("MODEL_DISP", "ELEMENT_FORCE"),
    ),
)
{{"\n"}}
