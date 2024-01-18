# STEP: RUN ANALYSIS
{{ res_Bld }} = MECA_STATIQUE(
    MODELE = model,
    CHAM_MATER = material,
    CARA_ELEM = element,
    LIST_INST = {{ analysis_time }},
    EXCIT = (
        _F(
            CHARGE = connection
        ),
        _F(
            CHARGE = {{ load }}
        )
    ),
    SOLVEUR=_F(
        NPREC=12,
        RESI_RELA=1e-1,
        STOP_SINGULIER='NON',
    )
)

{{ res_Bld }} = CALC_CHAMP(
    reuse = {{ res_Bld }},
    RESULTAT = {{ res_Bld }},
    CONTRAINTE=('EFGE_NOEU', ),
)
{{ "\n" }}
