import ifcopenshell

options = {
    "IfcPostalAddress": ({}, {"Country": "The Netherlands"}, {"Country": "The Netherlands", "Town": "Eindhoven"}),
    "IfcTelecomAddress": (
        {},
        {"TelephoneNumbers": ["040-12345678"]},
        {"TelephoneNumbers": ["040-12345678"], "PagerNumber": "12345"},
    ),
}

for ent in ("IfcPostalAddress", "IfcTelecomAddress"):
    for purpose in (None, "USERDEFINED", "HOME"):
        for ud in (None, "SomethingUserdefined"):

            f = ifcopenshell.file(schema="IFC2X3")
            f.create_entity(ent, purpose, None, ud, **options[ent][1])

            valid = not (purpose == "USERDEFINED" and ud is None)

            f.write(f"{'pass' if valid else 'fail'}-{ent}-{purpose}-{ud}-ifc2x3.ifc")

    for kwargs in options[ent]:
        f = ifcopenshell.file(schema="IFC2X3")
        f.create_entity(ent, **kwargs)
        valid = len(kwargs) >= 1
        if not valid:
            kwargs = {"all-unset": 1}
        f.write(f"{'pass' if valid else 'fail'}-{ent}-{'-'.join(kwargs.keys())}-ifc2x3.ifc")
