class Patcher:
    def __init__(self, src, file, logger):
        """Convert nesting relationships to aggregate relationships

        Some software like Revit won't load nested children elements because
        they (incorrectly) don't consider it to be part of the spatial tree.
        For example, 12D software will use nesting.

        This patch converts all nest relationships into aggregate
        relationships.

        See bug: https://github.com/Autodesk/revit-ifc/issues/706

        Example:

        .. code:: python

            ifcpatch.execute({"input": model, "recipe": "ConvertNestToAggregate", "arguments": []})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        for rel in self.file.by_type("IfcRelNests"):
            new = self.file.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                rel.OwnerHistory,
                rel.Name,
                rel.Description,
                rel.RelatingObject,
                rel.RelatedObjects,
            )
            self.file.remove(rel)
