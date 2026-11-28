# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell


@pytest.mark.parametrize(
    "encoded,expected",
    [
        ("AA\\X2\\D83DDE00\\X0\\BB", "AA\U0001f600BB"),
        ("AA\\X4\\0001F600\\X0\\BB", "AA\U0001f600BB"),
        ("AA\\X2\\00E9\\X0\\BB", "AAéBB"),
        ("\\X2\\00E9D83DDE0000E9\\X0\\", "é\U0001f600é"),
        ("\\X2\\D83DDE00D83DDE01\\X0\\", "\U0001f600\U0001f601"),
        ("Bld \\X2\\5EFA7BC9\\X0\\ ok", "Bld 建築 ok"),
    ],
)
def test_x2_utf16_surrogate_pairs(encoded, expected):
    data = (
        "ISO-10303-21;HEADER;FILE_DESCRIPTION((''),'2;1');FILE_NAME('','',(''),(''),'','','');"
        "FILE_SCHEMA(('IFC4'));ENDSEC;DATA;"
        "#1=IFCPROJECT('0YvctVUKr0kugbFTf53O9L',$,'" + encoded + "',$,$,$,$,$,$);"
        "ENDSEC;END-ISO-10303-21;"
    )
    f = ifcopenshell.file.from_string(data)
    assert f.by_id(1).Name == expected
