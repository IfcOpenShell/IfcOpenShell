def load_bsdd(props, client, bsdd):
    props.domains.clear()
    if props.load_preview_domains:
        dictionaries = bsdd.get_dictionaries(client)
    else:
        dictionaries = bsdd.get_dictionaries(client, "Active")
    if not props.load_preview_domains:
        dictionaries = filter(lambda d: d["status"] == "Active", dictionaries)
    for dictionary in sorted(dictionaries, key=lambda d: d["name"]):
        new = props.domains.add()
        bsdd.fill_dictionary_prop(new, dictionary)


def set_active_bsdd_dictionary(context, name, uri):
    props = context.scene.BIMBSDDProperties
    props.active_domain = name
    props.active_uri = uri


def search_class(context, client, bsdd, ifc):
    props = context.scene.BIMBSDDProperties
    props.classifications.clear()
    if len(props.keyword) < 3:
        return
    related_entities = bsdd.get_related_ifc_entities(props.keyword, props.should_filter_ifc_class,
                                                     context.active_object, ifc)
    response: dict = client.search_class(props.keyword, dictionary_uris=[props.active_uri],
                                         related_ifc_entities=related_entities)
    classes = response.get("classes", [])
    for _class in sorted(classes, key=lambda c: c["referenceCode"]):
        bsdd.fill_class_prop(props.classifications.add(), _class)


def get_class_properties(context, client, bsdd):
    bprops = context.scene.BIMBSDDProperties
    data = bsdd.get_active_class_data(bprops, client)
    pset_dict = bsdd.get_property_dict(data)
    if pset_dict is None:
        return
    bsdd.create_classification_psets(bprops, pset_dict)
