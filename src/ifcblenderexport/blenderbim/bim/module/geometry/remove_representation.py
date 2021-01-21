class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        styles = []
        for subelement in self.file.traverse(self.settings["representation"]):
            if subelement.is_a("IfcRepresentationItem") and subelement.StyledByItem:
                styles.append(subelement)
        for style in styles:
            self.remove_deep(style)
        self.remove_deep(self.settings["representation"])

    def remove_deep(self, element):
        subgraph = list(self.file.traverse(element))
        subgraph_set = set(subgraph)
        for ref in subgraph[::-1]:
            if ref.id() and len(set(self.file.get_inverse(ref)) - subgraph_set) == 0:
                self.file.remove(ref)
