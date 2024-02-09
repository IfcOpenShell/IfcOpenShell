# STEP: DEFINE TIME
{{ analysis_time }} = DEFI_LIST_REEL(
    DEBUT = {{ start }},
    INTERVALLE = _F(
        JUSQU_A = {{ end }},
        NOMBRE = {{ steps }}
    )
)

# STEP: DEFINE LOADS
{{ load }} = AFFE_CHAR_MECA_F(
    MODELE = model,
    FORCE_NODALE = (
        {%- for el in vertexLoadElements %}
        _F(
            GROUP_NO = {{ tuple([getGroupName(el.ref_id)]) }},
            {%- for key, load in el.loads[load_key].items() %}
            {{ key }} = DEFI_FONCTION(NOM_PARA='INST', ABSCISSE={{ time }}, ORDONNEE={{ tuple(load) }}),
            {%- endfor %}
        ),
        {%- endfor %}
    ),
    FORCE_POUTRE = (
        {%- for el in edgeLoadElements %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(el.ref_id)]) }},
            {%- for key, load in el.loads[load_key].items() %}
            {{ key }} = DEFI_FONCTION(NOM_PARA='INST', ABSCISSE={{ time }}, ORDONNEE={{ tuple(load) }}),
            {%- endfor %}
        ),
        {%- endfor %}
    ),
    FORCE_COQUE = (
        {%- for el in faceLoadElements %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(el.ref_id)]) }},
            {%- for key, load in el.loads[load_key].items() %}
            {{ key }} = DEFI_FONCTION(NOM_PARA='INST', ABSCISSE={{ time }}, ORDONNEE={{ tuple(load) }}),
            {%- endfor %}
        ),
        {%- endfor %}
    ),
)
{{ "\n" }}
