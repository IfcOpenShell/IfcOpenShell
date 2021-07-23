# Note: it is the intent for you to override these with your own functions


def get_person(ifc):
    people = ifc.by_type("IfcPerson") or [None]
    return people [0]


def get_organisation(ifc):
    organisations = ifc.by_type("IfcOrganization") or [None]
    return organisations[0]


def get_application(ifc):
    applications = ifc.by_type("IfcApplication") or [None]
    return applications[0]
