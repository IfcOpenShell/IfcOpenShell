# STEP: DEFINE SUPPORTS AND CONSTRAINTS
connection = AFFE_CHAR_MECA(
    MODELE = model,
    {%- if vertexConnections %}
    LIAISON_DDL = (
        {%- for conn in vertexConnections %}
            {%- if conn.appliedCondition %}
                {%- for i in range(len(conn.liaisons.coeffs)) %}
        _F(
            GROUP_NO = {{ conn.liaisons.groupNames }},
            DDL = {{ conn.liaisons.dofs[i] }},
            COEF_MULT = {{ conn.liaisons.coeffs[i] }},
            COEF_IMPO = 0.0
        ),
                {%- endfor %}
            {%- endif %}
            {%- for rel in conn.related_elements %}
                {%- for i in range(len(rel.liaisons.coeffs)) %}
        _F(
            GROUP_NO = {{ rel.liaisons.groupNames }},
            DDL = {{ rel.liaisons.dofs[i] }},
            COEF_MULT = {{ rel.liaisons.coeffs[i] }},
            COEF_IMPO = 0.0
        ),
                {%- endfor %}
            {%- endfor %}
        {%- endfor %}
    ),
    {%- endif %}
    {%- if edgeConnections %}
    LIAISON_GROUP = (
        {%- for conn in edgeConnections %}
            {%- if conn.appliedCondition %}
                {%- for i in range(len(conn.liaisons.coeffs)) %}
        _F(
            GROUP_NO_1 = {{ tuple([conn.liaisons.groupNames[0]]) }},
            GROUP_NO_2 = {{ tuple([conn.liaisons.groupNames[0]]) }},
            DDL_1 = {{ conn.liaisons.dofs[i] }},
            DDL_2 = {{ conn.liaisons.dofs[i] }},
            COEF_MULT_1 = {{ conn.liaisons.coeffs[i] }},
            COEF_MULT_2 = (0.0, 0.0, 0.0),
            COEF_IMPO = 0.0
        ),
                {%- endfor %}
            {%- endif %}
            {%- for rel in conn.related_elements %}
                {%- for i in range(len(rel.liaisons.coeffs)) %}
        _F(
            GROUP_NO_1 = {{ tuple([rel.liaisons.groupNames[0]]) }},
            GROUP_NO_2 = {{ tuple([rel.liaisons.groupNames[3]]) }},
            DDL_1 = {{ tuple(rel.liaisons.dofs[i][:3]) }},
            DDL_2 = {{ tuple(rel.liaisons.dofs[i][:3]) }},
            COEF_MULT_1 = {{ tuple(rel.liaisons.coeffs[i][:3]) }},
            COEF_MULT_2 = {{ tuple(rel.liaisons.coeffs[i][3:]) }},
            COEF_IMPO = 0.0
        ),
                {%- endfor %}
            {%- endfor %}
        {%- endfor %}
    ),
    {%- endif %}
    {%- if unifiedConnections %}
    LIAISON_UNIF = (
        {%- for conn in unifiedConnections %}
        _F(
            GROUP_NO = {{ conn.unifiedGroupNames }},
            DDL = ('DX', 'DY', 'DZ', 'DRX', 'DRY', 'DRZ')
        ),
        {%- endfor %}
    ),
    {%- endif %}
    {%- if rigidLinkGroupNames %}
    LIAISON_SOLIDE = (
        {%- for groupName in rigidLinkGroupNames %}
        _F(GROUP_MA = {{ tuple([groupName]) }}),
        {%- endfor %}
    ),
    {%- endif %}
)
{{ "\n" }}
