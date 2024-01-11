def get_class_properties(client, bsdd):
    bsdd.clear_class_psets()
    data = bsdd.get_active_class_data(client)
    pset_dict = bsdd.get_property_dict(data)
    if pset_dict is None:
        return
    bsdd.create_class_psets(pset_dict)


def load_bsdd(client, bsdd):
    bsdd.clear_domains()
    if bsdd.should_load_preview_domains:
        dictionaries = bsdd.get_dictionaries(client)
    else:
        dictionaries = bsdd.get_dictionaries(client, "Active")
    bsdd.create_dictionaries(dictionaries)


def search_class(keyword: str, client, bsdd):
    bsdd.clear_classes()
    if len(keyword) < 3:
        return
    related_entities = bsdd.get_related_ifc_entities(keyword)
    active_dictionary_uri = bsdd.get_active_dictionary_uri()
    classes: dict = bsdd.search_class(client, keyword, [active_dictionary_uri], related_entities)
    bsdd.create_classes(classes)


def set_active_bsdd_dictionary(name: str, uri: str, bsdd):
    bsdd.set_active_bsdd(name, uri)
