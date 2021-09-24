# Note: it is the intent for you to override these with your own functions
users = {}


def get_person(ifc):
    people = ifc.by_type("IfcPerson") or [None]
    return people[0]


def get_organisation(ifc):
    organisations = ifc.by_type("IfcOrganization") or [None]
    return organisations[0]


def get_application(ifc):
    applications = ifc.by_type("IfcApplication") or [None]
    return applications[0]


def get_user(ifc):
    person = get_person(ifc)
    organisation = get_organisation(ifc)
    if not person or not organisation:
        return
    key = f"{person.id()}-{organisation.id()}"
    user = users.get(key)
    if not user:
        for element in ifc.by_type("IfcPersonAndOrganization"):
            if element.ThePerson == person and element.TheOrganization == organisation:
                users[key] = element
                user = element
        if not user:
            return ifc.create_entity("IfcPersonAndOrganization", ThePerson=person, TheOrganization=organisation)
    return user
