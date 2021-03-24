class Data:
    products = {}
    openings = {}
    fillings = {}

    @classmethod
    def purge(cls):
        cls.products = {}
        cls.openings = {}
        cls.fillings = {}

    @classmethod
    def load(cls, file, product_id):
        if not file:
            return
        cls.products[product_id] = set()
        if product_id in cls.fillings:
            del cls.fillings[product_id]
        product = file.by_id(product_id)
        for rel in file.by_type("IfcRelVoidsElement"):
            building_element = rel.RelatingBuildingElement
            if building_element != product:
                continue
            opening = rel.RelatedOpeningElement
            opening_id = int(opening.id())
            cls.products[product_id].add(opening_id)
            cls.openings[opening_id] = {"Name": opening.Name, "HasFillings": set()}
        for rel in file.by_type("IfcRelFillsElement"):
            opening = rel.RelatingOpeningElement
            opening_id = int(opening.id())
            filling = rel.RelatedBuildingElement
            filling_id = int(filling.id())

            if filling_id == product_id and opening_id not in cls.openings:
                cls.openings[opening_id] = {"Name": opening.Name, "HasFillings": set()}

            if opening_id not in cls.openings:
                continue

            cls.fillings[filling_id] = {"Name": filling.Name, "FillsVoid": opening_id}
            cls.openings[opening_id]["HasFillings"].add(filling_id)
        return  # See bug #1224
        #if not hasattr(product, "HasOpenings") or not product.HasOpenings:
        #    return
        #for rel_voids_element in product.HasOpenings:
        #    opening = rel_voids_element.RelatedOpeningElement
        #    opening_id = int(opening.id())
        #    fillings = []
        #    if opening.HasFillings:
        #        for rel_fills_element in opening.HasFillings:
        #            filling = rel_fills_element.RelatedBuildingElement
        #            filling_id = int(filling.id())
        #            fillings.append(filling_id)
        #            cls.fillings[filling_id] = {
        #                "Name": filling.Name,
        #            }
        #    cls.openings[opening_id] = {
        #        "Name": opening.Name,
        #        "HasFillings": fillings,
        #    }
        #    cls.products[product_id].append(opening_id)
