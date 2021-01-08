from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    people = {}

    @classmethod
    def load(cls):
        file = IfcStore.get_file()
        if not file:
            return
        cls.people = {}
        for person in file.by_type("IfcPerson"):
            data = person.get_info()

            roles = {}
            if data["Roles"]:
                for role in data["Roles"]:
                    roles[role.id()] = role.get_info()
            data["Roles"] = roles

            addresses = []
            if data["Addresses"]:
                for address in data["Addresses"]:
                    addresses.append(address.get_info())
            data["Addresses"] = addresses

            data["is_engaged"] = bool(person.EngagedIn)

            cls.people[person.id()] = data
        cls.is_loaded = True
