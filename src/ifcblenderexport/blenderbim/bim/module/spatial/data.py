from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        product = file.by_id(product_id)
        if product.ContainedInStructure:
            structure = product.ContainedInStructure[0].RelatingStructure
            cls.products[product_id] = {"type": structure.is_a(), "Name": structure.Name, "id": int(structure.id())}
        else:
            cls.products[product_id] = {"type": None, "Name": None, "id": None}
