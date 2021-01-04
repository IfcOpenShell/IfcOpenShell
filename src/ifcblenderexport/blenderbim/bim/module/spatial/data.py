from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        product = file.by_id(product_id)
        element = product.ContainedInStructure[0].RelatingStructure if product.ContainedInStructure else None
        cls.products[product_id] = {
            "type": element.is_a() if element else None,
            "Name": element.Name if element else None,
            "id": int(element.id()) if element else None
        }
