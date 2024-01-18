# STEP: DEFINE MATERIALS
{%- for i, (_, material) in enumerate(materials.items()) %}
{{ "mat" + "_%s" % i }} = DEFI_MATERIAU(
    ELAS = _F(
        E = {{ material.properties.YoungModulus }},
        NU = {{ material.properties.PoissonRatio }},
        RHO = {{ material.properties.MassDensity }}
    )
)
{% endfor %}
material = AFFE_MATERIAU(
    MAILLAGE = mesh,
    AFFE = (
        {%- for i, (_, material) in enumerate(materials.items()) %}
        _F(
            GROUP_MA = {{ material.groupNames }},
            MATER = {{ "mat" + "_%s" % i }},
        ),
        {%- endfor %}
        {%- if rigidLinkGroupNames %}
        _F(
            GROUP_MA = {{ rigidLinkGroupNames }},
            MATER = {{ "mat_0" }},
        ),
        {%- endif %}
    )
)
{{ "\n" }}
