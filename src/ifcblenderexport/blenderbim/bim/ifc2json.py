import ifcopenshell

class IFC2JSON:
    def __init__(self, file):
        self.file = file
        self.id_objects = {}
        self.jsonObjects = []

    def convert(self):
        # schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(self.file.schema)
        entityIter = iter(self.file)
        for entity in entityIter:
            self.entityToDict(entity)
        for key in self.id_objects:
            self.jsonObjects.append(self.id_objects[key])

        return {
            'data': self.jsonObjects
        }

    def entityToDict(self, entity):
        ref = {
            'Type': entity.is_a()
        }
        attr_dict = entity.__dict__

        # check for globalid
        if 'GlobalId' in attr_dict:
            ref['ref'] = attr_dict['GlobalId']
            if not attr_dict['GlobalId'] in self.id_objects:
                d = {
                    'Type': entity.is_a()
                }

                for i in range(0,len(entity)):
                    attr = entity.attribute_name(i)
                    if attr in attr_dict:
                        if not attr == 'OwnerHistory':
                            jsonValue = self.getEntityValue(attr_dict[attr])
                            if jsonValue:
                                d[attr] = jsonValue
                            if attr_dict[attr] == None:
                                continue
                            elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                                d[attr] = self.entityToDict(attr_dict[attr])
                            elif isinstance(attr_dict[attr], tuple):
                                subEnts = []
                                for subEntity in attr_dict[attr]:
                                    if isinstance(subEntity, ifcopenshell.entity_instance):
                                        subEntJson = self.entityToDict(subEntity)
                                        if subEntJson:
                                            subEnts.append(subEntJson)
                                    else:
                                        subEnts.append(subEntity)
                                if len(subEnts) > 0:
                                    d[attr] = subEnts
                            else:
                                d[attr] = attr_dict[attr]
                self.id_objects[attr_dict['GlobalId']] = d
            return ref
        else:
            d = {
                'Type': entity.is_a()
            }

            for i in range(0,len(entity)):
                attr = entity.attribute_name(i)
                if attr in attr_dict:
                    if not attr == 'OwnerHistory':
                        jsonValue = self.getEntityValue(attr_dict[attr])
                        if jsonValue:
                            d[attr] = jsonValue
                        if attr_dict[attr] == None:
                            continue
                        elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                            d[attr] = self.entityToDict(attr_dict[attr])
                        elif isinstance(attr_dict[attr], tuple):
                            subEnts = []
                            for subEntity in attr_dict[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    # subEnts.append(None)
                                    subEntJson = self.entityToDict(subEntity)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attr] = subEnts
                        else:
                            d[attr] = attr_dict[attr]
            return d

    def getEntityValue(self, value):
        if value == None:
            jsonValue = None
        elif isinstance(value, ifcopenshell.entity_instance):
            jsonValue = self.entityToDict(value)
        elif isinstance(value, tuple):
            jsonValue = None
            subEnts = []
            for subEntity in value:
                subEnts.append(self.getEntityValue(subEntity))
            jsonValue = subEnts
        else:
            jsonValue = value
        return jsonValue
