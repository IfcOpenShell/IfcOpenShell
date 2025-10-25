@ECHO OFF

:: python bootstrap.py express.bnf > express_parser.py

IF EXIST IFC2X3_TC1.exp (
    python express_parser.py IFC2X3_TC1.exp header implementation schema_class definitions
    
    IF EXIST Ifc2x3-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc2x3.cpp txt/header_ifc2x3.txt Ifc2x3.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc2x3.h txt/header_ifc2x3.txt Ifc2x3.h
        python cat.py -o ..\..\..\ifcparse\Ifc2x3-schema.cpp txt/header_ifc2x3.txt Ifc2x3-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc2x3-definitions.h txt/header_ifc2x3.txt Ifc2x3-definitions.h
    ) ELSE (
        :: v0.5.0
        python cat.py -o ..\..\..\ifcparse\Ifc2x3.cpp txt/header_ifc2x3.txt txt/ifndef_ifc4.txt Ifc2x3.cpp txt/endif.txt
        python cat.py -o ..\..\..\ifcparse\Ifc2x3.h txt/header_ifc2x3.txt Ifc2x3.h
        python cat.py -o ..\..\..\ifcparse\Ifc2x3enum.h txt/header_ifc2x3.txt Ifc2x3enum.h
        python cat.py -o ..\..\..\ifcparse\Ifc2x3-latebound.cpp txt/header_ifc2x3.txt txt/ifndef_ifc4.txt Ifc2x3-latebound.cpp txt/endif.txt
        python cat.py -o ..\..\..\ifcparse\Ifc2x3-latebound.h txt/header_ifc2x3.txt Ifc2x3-latebound.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4_ADD2TC1.exp (
    python express_parser.py IFC4_ADD2TC1.exp header implementation schema_class definitions

    IF EXIST Ifc4-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4.cpp txt/header_ifc4.txt Ifc4.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4.h txt/header_ifc4.txt Ifc4.h
        python cat.py -o ..\..\..\ifcparse\Ifc4-schema.cpp txt/header_ifc4.txt Ifc4-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4-definitions.h txt/header_ifc4.txt Ifc4-definitions.h
    ) ELSE (
        :: v0.5.0
        python cat.py -o ..\..\..\ifcparse\Ifc4.cpp txt/header_ifc4.txt txt/ifdef_ifc4.txt Ifc4.cpp txt/endif.txt
        python cat.py -o ..\..\..\ifcparse\Ifc4.h txt/header_ifc4.txt Ifc4.h
        python cat.py -o ..\..\..\ifcparse\Ifc4enum.h txt/header_ifc4.txt Ifc4enum.h
        python cat.py -o ..\..\..\ifcparse\Ifc4-latebound.cpp txt/header_ifc4.txt txt/ifdef_ifc4.txt Ifc4-latebound.cpp txt/endif.txt
        python cat.py -o ..\..\..\ifcparse\Ifc4-latebound.h txt/header_ifc4.txt Ifc4-latebound.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4x1.exp (
    python express_parser.py IFC4x1.exp header implementation schema_class definitions

    IF EXIST Ifc4x1-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x1.cpp txt/header_ifc4x1.txt Ifc4x1.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x1.h txt/header_ifc4x1.txt Ifc4x1.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x1-schema.cpp txt/header_ifc4x1.txt Ifc4x1-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x1-definitions.h txt/header_ifc4x1.txt Ifc4x1-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4x2.exp (
    python express_parser.py IFC4x2.exp header implementation schema_class definitions

    IF EXIST Ifc4x2-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x2.cpp txt/header_ifc4x2.txt Ifc4x2.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x2.h txt/header_ifc4x2.txt Ifc4x2.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x2-schema.cpp txt/header_ifc4x2.txt Ifc4x2-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x2-definitions.h txt/header_ifc4x2.txt Ifc4x2-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4x3_RC1.exp (
    python express_parser.py IFC4x3_RC1.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_rc1-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc1.cpp txt/header_ifc4x3_rc1.txt Ifc4x3_rc1.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc1.h txt/header_ifc4x3_rc1.txt Ifc4x3_rc1.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc1-schema.cpp txt/header_ifc4x3_rc1.txt Ifc4x3_rc1-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc1-definitions.h txt/header_ifc4x3_rc1.txt Ifc4x3_rc1-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4x3_RC2.exp (
    python express_parser.py IFC4x3_RC2.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_rc2-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc2.cpp txt/header_ifc4x3_rc2.txt Ifc4x3_rc2.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc2.h txt/header_ifc4x3_rc2.txt Ifc4x3_rc2.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc2-schema.cpp txt/header_ifc4x3_rc2.txt Ifc4x3_rc2-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc2-definitions.h txt/header_ifc4x3_rc2.txt Ifc4x3_rc2-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4x3_RC3.exp (
    python express_parser.py IFC4x3_RC3.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_rc3-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc3.cpp txt/header_ifc4x3_rc2.txt Ifc4x3_rc3.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc3.h txt/header_ifc4x3_rc2.txt Ifc4x3_rc3.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc3-schema.cpp txt/header_ifc4x3_rc2.txt Ifc4x3_rc3-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc3-definitions.h txt/header_ifc4x3_rc2.txt Ifc4x3_rc3-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4x3_RC4.exp (
    python express_parser.py IFC4x3_RC4.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_rc4-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc4.cpp txt/header_ifc4x3_rc2.txt Ifc4x3_rc4.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc4.h txt/header_ifc4x3_rc2.txt Ifc4x3_rc4.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc4-schema.cpp txt/header_ifc4x3_rc2.txt Ifc4x3_rc4-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_rc4-definitions.h txt/header_ifc4x3_rc2.txt Ifc4x3_rc4-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4X3.exp (
    python express_parser.py IFC4X3.exp header implementation schema_class definitions

    IF EXIST Ifc4x3-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3.cpp txt/header_ifc4x3_rc2.txt Ifc4x3.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3.h txt/header_ifc4x3_rc2.txt Ifc4x3.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3-schema.cpp txt/header_ifc4x3_rc2.txt Ifc4x3-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3-definitions.h txt/header_ifc4x3_rc2.txt Ifc4x3-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4X3_TC1.exp (
    python express_parser.py IFC4X3_TC1.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_tc1-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_tc1.cpp txt/header_ifc4x3_tc1.txt Ifc4x3_tc1.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_tc1.h txt/header_ifc4x3_tc1.txt Ifc4x3_tc1.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_tc1-schema.cpp txt/header_ifc4x3_tc1.txt Ifc4x3_tc1-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_tc1-definitions.h txt/header_ifc4x3_tc1.txt Ifc4x3_tc1-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4X3_ADD1.exp (
    python express_parser.py IFC4X3_ADD1.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_add1-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add1.cpp txt/header_ifc4x3_add1.txt Ifc4x3_add1.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add1.h txt/header_ifc4x3_add1.txt Ifc4x3_add1.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add1-schema.cpp txt/header_ifc4x3_add1.txt Ifc4x3_add1-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add1-definitions.h txt/header_ifc4x3_add1.txt Ifc4x3_add1-definitions.h
    )
    
    del *.cpp *.h
)

IF EXIST IFC4X3_ADD2.exp (
    python express_parser.py IFC4X3_ADD2.exp header implementation schema_class definitions

    IF EXIST Ifc4x3_add2-schema.cpp (
        :: v0.6.0
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add2.cpp txt/header_ifc4x3_add2.txt Ifc4x3_add2.cpp
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add2.h txt/header_ifc4x3_add2.txt Ifc4x3_add2.h
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add2-schema.cpp txt/header_ifc4x3_add2.txt Ifc4x3_add2-schema.cpp 
        python cat.py -o ..\..\..\ifcparse\Ifc4x3_add2-definitions.h txt/header_ifc4x3_add2.txt Ifc4x3_add2-definitions.h
    )
    
    del *.cpp *.h
)
