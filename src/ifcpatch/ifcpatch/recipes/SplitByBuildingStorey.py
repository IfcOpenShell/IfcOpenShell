class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        import ifcopenshell
        from shutil import copyfile
        storeys = self.file.by_type('IfcBuildingStorey')
        for i, storey in enumerate(storeys):
            dest = '{}-{}.ifc'.format(i, storey.Name)
            copyfile(self.src, dest)
            old_ifc = ifcopenshell.open(dest)
            new_ifc = ifcopenshell.file(schema=self.file.schema)
            if self.file.schema == 'IFC2X3':
                elements = old_ifc.by_type('IfcProject') + old_ifc.by_type('IfcProduct')
            else:
                elements = old_ifc.by_type('IfcContext') + old_ifc.by_type('IfcProduct')
            inverse_elements = []
            for element in elements:
                if element.is_a('IfcElement') \
                        and not self.is_in_storey(element, storey):
                    element.Representation = None
                    continue
                if element.is_a('IfcElement'):
                    styled_rep_items = [i for i in old_ifc.traverse(element) if i.is_a('IfcRepresentationItem') and i.StyledByItem]
                    [new_ifc.add(i.StyledByItem[0]) for i in styled_rep_items]
                new_ifc.add(element)
                inverse_elements.extend(old_ifc.get_inverse(element))
            for inverse_element in inverse_elements:
                new_ifc.add(inverse_element)
            for element in new_ifc.by_type('IfcElement'):
                if not self.is_in_storey(element, storey):
                    new_ifc.remove(element)
            new_ifc.write(dest)

    def is_in_storey(self, element, storey):
        return element.ContainedInStructure \
            and element.ContainedInStructure[0].RelatingStructure.is_a('IfcBuildingStorey') \
            and element.ContainedInStructure[0].RelatingStructure.GlobalId == storey.GlobalId
