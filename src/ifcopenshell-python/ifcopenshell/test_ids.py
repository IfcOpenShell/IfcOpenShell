import unittest
from ids import ids, specification, entity, classification, property, material


class TestIds(unittest.TestCase):

    """ Parsing IDS.xml """

    def test_parse(self):
        ids_file = ids.parse(sys.argv[1])
        self.assertEqual( type(ids_file).__name__, "ids" )

    """ IDS authoring """

    """ IFC validation with IDS """

    """ IDS validation results """


if __name__ == '__main__':
    import sys
    unittest.main()