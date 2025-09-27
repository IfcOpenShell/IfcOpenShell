async def test_pset():
    import ifcopenshell.api.pset
    import ifcopenshell.api.material
    errors = []
    try:
        model = ifcopenshell.file()

        steel_material = ifcopenshell.api.material.add_material(model, name="S355 Steel")
        steel_pset = ifcopenshell.api.pset.add_pset(model,
            product=steel_material,
            name="Pset_MaterialSteel")

        ifcopenshell.api.pset.edit_pset(model,
            pset=steel_pset,
            properties={
                "YieldStress": 355*(10**6),  # Pa (355 MPa)
            })
    except Exception as e:
        errors.append(f"API Error: {e}")
        return errors

async def test_doc():
    import ifcopenshell.util.doc
    errors = []
    try:
        ifcopenshell.util.doc.get_entity_doc("IFC4", "IfcWall", recursive=True)
    except Exception as e:
        errors.append(f"Doc API Error: {e}")
    return errors
