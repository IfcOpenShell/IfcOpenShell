import os
import pytest
import weakref
import itertools
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.template


@pytest.mark.parametrize(
    "args",
    itertools.product((0, 1), (0, 1), (0, 1), (0, 1, 2)),
)
def test_file_gc(args):
    do_run_api, do_delete_ref, file_first, api = args

    f = ifcopenshell.file()
    if api == 0:
        inst = f.createIfcPerson()
    elif api in (1, 2):
        inst = f.createIfcSite()

    r = weakref.ref(f)

    if do_run_api:
        if api == 0:
            ifcopenshell.api.run(
                "attribute.edit_attributes",
                f,
                product=inst,
                attributes={"FamilyName": "Bimson"},
            )
        elif api == 1:
            ifcopenshell.api.run(
                "pset.add_pset", f, product=inst, name="ePSet_MapConversion"
            )
        elif api == 2:
            pset = f.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", f
                    ),
                    "Name": "ePSet_MapConversion",
                }
            )
            f.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", f
                    ),
                    "RelatedObjects": [inst],
                    "RelatingPropertyDefinition": pset,
                }
            )
            del pset

    if file_first:
        del f
    else:
        del inst

    # File should still exist, because we either have a direct ref
    # or the instance from the file still available
    assert r()

    if not file_first:
        del f
    else:
        del inst

    # With both deleted we should have no longer access to the file.
    assert r() is None


def test_bug_2517():
    fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
    model = ifcopenshell.open(f'{fixtures}/bug_2517_test2.ifc')
    library = ifcopenshell.open(f"{fixtures}/bug_2517_lib.ifc")
    result = model.add(library.by_type("IfcClassification")[0])
    model.create_entity(
        "IfcRelAssociatesClassification",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[model.by_type("IfcProject")[0]],
        RelatingClassification=result,
    )


def test_bug_2486_a():
    run = ifcopenshell.api.run

    file = run("project.create_file")

    mymaterial = run("material.add_material", file)
    pset = run("pset.add_pset", file, product=mymaterial)
    run(
        "pset.edit_pset",
        file,
        pset=pset,
        properties={"foo": "bar"},
    )

    another_file = run("project.create_file")

    run(
        "project.append_asset",
        another_file,
        library=file,
        element=mymaterial,
    )


def test_bug_2486_b():
    file = ifcopenshell.template.create()
    file.wrapped_data.header.file_name.name = "myfile.ifc"


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
