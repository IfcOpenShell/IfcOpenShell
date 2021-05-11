import argparse
from cjio import cityjson
from cityjson2ifc import Cityjson2ifc

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Example:
    # python ifccityjson.py -i example/3DBAG_example.json -o example/output.ifc -n identificatie
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-i", "--input", type=str, help="input CityJSON file", required=True)
    parser.add_argument("-o", "--output", type=str, help="output IFC file. Standard is output.ifc")
    parser.add_argument("-n", "--name", type=str, help="Attribute containing the name")
    args = parser.parse_args()

    city_model = cityjson.load(args.input)
    data = {}
    if args.name:
        data["name_attribute"] = args.name
    if args.output:
        data["file_destination"] = args.output

    converter = Cityjson2ifc()
    converter.configuration(**data)
    converter.convert(city_model)
