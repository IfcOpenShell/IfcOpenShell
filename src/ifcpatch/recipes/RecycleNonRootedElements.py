class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        import ifcopenshell.util.element
        hashes = {}
        for element in self.file:
            if element.is_a('IfcRoot'):
                continue
            h = hash(tuple(element))
            if h in hashes:
                for inverse in f.get_inverse(element):
                    ifcopenshell.util.element.replace_attribute(inverse, element, hashes[h])
                self.file.remove(element)
            else:
                hashes[h] = element
