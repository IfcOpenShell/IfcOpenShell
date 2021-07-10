class Data:
    styles = {}

    @classmethod
    def purge(cls):
        cls.styles = {}

    @classmethod
    def load(cls, file, style_id):
        if not file:
            return
        data = file.by_id(style_id).get_info()
        data["Styles"] = [s.id() for s in data["Styles"]]
        cls.styles[style_id] = data
