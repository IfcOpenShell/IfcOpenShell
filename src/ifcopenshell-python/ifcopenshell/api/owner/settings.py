# Note: it is the intent for you to override these with your own functions


def get_person(ifc):
    return ifc.by_type("IfcPerson")[0]


def get_organisation(ifc):
    return ifc.by_type("IfcOrganization")[0]


def get_application(ifc):
    return ifc.by_type("IfcApplication")[0]
