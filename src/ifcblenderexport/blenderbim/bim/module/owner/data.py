from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    people = {}
    organisations = {}
    addresses = {}
    roles = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.people = {}
        cls.organisations = {}
        cls.addresses = {}
        cls.roles = {}

    @classmethod
    def load(cls):
        file = IfcStore.get_file()
        if not file:
            return
        cls.people = {}
        cls.organisations = {}
        cls.addresses = {}
        cls.roles = {}
        for person in file.by_type("IfcPerson"):
            data = person.get_info()
            data["is_engaged"] = bool(person.EngagedIn)
            cls.people[person.id()] = data

            roles = []
            if data["Roles"]:
                for role in data["Roles"]:
                    roles.append(role.id())
            data["Roles"] = roles

            addresses = []
            if data["Addresses"]:
                for address in data["Addresses"]:
                    addresses.append(address.id())
            data["Addresses"] = addresses

        for organisation in file.by_type("IfcOrganization"):
            data = organisation.get_info()
            data["is_engaged"] = (
                bool(organisation.IsRelatedBy) or bool(organisation.Relates) or bool(organisation.Engages)
            )
            cls.organisations[organisation.id()] = data

            roles = []
            if data["Roles"]:
                for role in data["Roles"]:
                    roles.append(role.id())
            data["Roles"] = roles

            addresses = []
            if data["Addresses"]:
                for address in data["Addresses"]:
                    addresses.append(address.id())
            data["Addresses"] = addresses

        for address in file.by_type("IfcAddress"):
            cls.addresses[address.id()] = address.get_info()

        for role in file.by_type("IfcActorRole"):
            cls.roles[role.id()] = role.get_info()
        cls.is_loaded = True
