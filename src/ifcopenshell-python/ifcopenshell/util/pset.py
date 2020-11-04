import ifcopenshell

property_set_template_files = []
psets = {}
qtos = {}
applicable_psets = {}
applicable_qtos = {}


def load_property_set_template(path):
    property_set_template_files.append(ifcopenshell.open(path))
    for prop in property_set_template_files[-1].by_type("IfcPropertySetTemplate"):
        if prop.Name[0:4] == "Qto_":
            qtos[prop.Name] = {"HasPropertyTemplates": {p.Name: p for p in prop.HasPropertyTemplates}}
            entity = prop.ApplicableEntity if prop.ApplicableEntity else "IfcRoot"
            applicable_qtos.setdefault(entity, []).append(prop.Name)
        else:
            psets[prop.Name] = {"HasPropertyTemplates": {p.Name: p for p in prop.HasPropertyTemplates}}
            entity = prop.ApplicableEntity if prop.ApplicableEntity else "IfcRoot"
            applicable_psets.setdefault(entity, []).append(prop.Name)


def get_applicable_psetqtos(schema_version, ifc_class, is_pset=False, is_qto=False):
    def is_a(entity, ifc_class):
        if entity.name() == ifc_class:
            return True
        return is_a(entity.supertype(), ifc_class) if entity.supertype() else False

    results = []
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_version)
    entity = schema.declaration_by_name(ifc_class)
    if is_pset:
        search_items = applicable_psets.items()
    elif is_qto:
        search_items = applicable_qtos.items()
    for ifc_class, pset_names in search_items:
        if is_a(entity, ifc_class):
            results.extend(pset_names)
    return results
