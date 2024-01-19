# STEP: DEFINE MODEL
model = AFFE_MODELE(
    MAILLAGE = mesh,
    AFFE = (
        _F(
            TOUT = 'OUI',
            PHENOMENE = 'MECANIQUE',
            MODELISATION = '3D'
        ),
        {%- if faceGroupNames %}
        _F(
            GROUP_MA = {{ faceGroupNames }},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'DKT'
        ),
        {%- endif %}
        {%- if edgeGroupNames %}
        _F(
            GROUP_MA = {{ edgeGroupNames }},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        ),
        {%- endif %}
        {%- if point0DGroupNames %}
        _F(
            GROUP_MA = {{ point0DGroupNamesPlus }},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'DIS_TR'
        ),
        {%- endif %}
        {%- if point1DGroupNames %}
        _F(
            GROUP_MA = {{ point1DGroupNames }},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'DIS_TR'
        ),
        {%- endif %}
        {%- if rigidLinkGroupNames %}
        _F(
            GROUP_MA = {{ rigidLinkGroupNames }},
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        ),
        {%- endif %}
    )
)
{{ "\n" }}
