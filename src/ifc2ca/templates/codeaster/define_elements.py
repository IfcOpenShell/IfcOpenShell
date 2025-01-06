# STEP: DEFINE ELEMENTS
element = AFFE_CARA_ELEM(
    MODELE = model,
    POUTRE = (
        {%- for _, profile in profiles.items() %}
        {%- if profile.properties %}
        _F(
            GROUP_MA = {{ profile.groupNames }},
            SECTION = 'GENERALE',
            CARA = ('A', 'IY', 'IZ', 'JX'),
            VALE = ({{ profile.properties.CrossSectionArea }}, {{ profile.properties.MomentOfInertiaY }}, {{ profile.properties.MomentOfInertiaZ }}, {{ profile.properties.TorsionalConstantX }})
        ),
        {%- elif profile.type == "IfcRectangleProfileDef" and profile.ProfileType == "AREA" %}
        _F(
            GROUP_MA = {{ profile.groupNames }},
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = ({{ profile.XDim }}, {{ profile.YDim }})
        ),
        {%- elif profile.type == "IfcRectangleHollowProfileDef" and profile.ProfileType == "AREA" %}
        _F(
            GROUP_MA = {{ profile.groupNames }},
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ', 'EPY', 'EPZ'),
            VALE = ({{ profile.XDim }}, {{ profile.YDim }}, {{ profile.WallThickness }}, {{ profile.WallThickness }})
        ),
        {%- else %}
        _F(
            GROUP_MA = {{ profile.groupNames }},
            SECTION = 'GENERALE',
            CARA = ('A', 'IY', 'IZ', 'JX'),
            VALE = ({{ profile.properties.CrossSectionArea }}, {{ profile.properties.MomentOfInertiaY }}, {{ profile.properties.MomentOfInertiaZ }}, {{ profile.properties.TorsionalConstantX }})
        ),
        {%- endif %}
        {%- endfor %}
        {%- if rigidLinkGroupNames %}
        _F(
            GROUP_MA = {{ rigidLinkGroupNames }},
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = (1.0, 1.0)
        ),
        {%- endif %}
    ),
    COQUE = (
        {%- for el in shellElements %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(el.ref_id)]) }},
            EPAIS = {{ el.Thickness }},
            VECTEUR = {{ tuple(el.orientation[0]) }}
        ),
        {%- endfor %}
    ),
    DISCRET = (
        {%- for conn in vertexConnections %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(conn.ref_id) + "_0D"]) }},
            CARA = 'K_TR_D_N',
            VALE = {{ conn.stiffnesses }},
            REPERE = 'LOCAL'
        ),
        {%- if includeZeroLength1DSprings %}
        {%- for rel in conn.related_elements %}
        _F(
            GROUP_MA = {{ tuple([rel.springGroupName]) }},
            CARA = 'K_TR_D_L',
            VALE = {{ rel.stiffnesses }},
            REPERE = 'LOCAL'
        ),
        {%- endfor %}
        {%- endif %}
        {%- endfor %}
        {%- for conn in edgeConnections %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(conn.ref_id) + "_0D"]) }},
            CARA = 'K_TR_D_N',
            VALE = {{ conn.stiffnesses }},
            REPERE = 'LOCAL'
        ),
        {%- endfor %}
    ),
    ORIENTATION = (
        {%- for el in beamElements %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(el.ref_id)]) }},
            CARA = 'VECT_Y',
            VALE = {{ tuple(el.orientation[1]) }}
        ),
        {%- endfor %}
        {%- for conn in vertexConnections %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(conn.ref_id) + "_0D"]) }},
            CARA = 'VECT_X_Y',
            VALE = {{ tuple(conn.orientation[0] + conn.orientation[1]) }}
        ),
        {%- if includeZeroLength1DSprings %}
        {%- for rel in conn.related_elements %}
        _F(
            GROUP_MA = {{ tuple([rel.springGroupName]) }},
            CARA = 'VECT_X_Y',
            VALE = {{ tuple(rel.orientation[0] + rel.orientation[1]) }},
        ),
        {%- endfor %}
        {%- endif %}
        {%- endfor %}
        {%- for conn in edgeConnections %}
        _F(
            GROUP_MA = {{ tuple([getGroupName(conn.ref_id) + "_0D"]) }},
            CARA = 'VECT_X_Y',
            VALE = {{ tuple(conn.orientation[0] + conn.orientation[1]) }}
        ),
        {%- endfor %}
    ),
)
{{ "\n" }}
