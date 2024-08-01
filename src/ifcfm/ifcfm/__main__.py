import ifcfm
import argparse
import ifcopenshell

parser = argparse.ArgumentParser(description="Extracts FM data from IFC to spreadsheets")
parser.add_argument(
    "-p",
    "--preset",
    type=str,
    default="basic",
    help="The FM standard to extract. Built-in preset standards include cobie24, cobie3, aohbsem, and basic.",
)
parser.add_argument("-i", "--ifc", type=str, required=True, help="The IFC file")
parser.add_argument(
    "-s",
    "--spreadsheet",
    type=str,
    default="output.ods",
    help="The spreadsheet file, or directory if the format is csv. Defaults to output.ods",
)
parser.add_argument(
    "-f", "--format", type=str, default="ods", help="The format, chosen from csv, ods, or xlsx. Defaults to ods."
)
parser.add_argument("-d", "--delimiter", type=str, default=",", help="The delimiter in CSV. Defaults to a comma.")
parser.add_argument("-n", "--null", type=str, default="N/A", help="How to represent null values. Defaults to N/A.")
parser.add_argument(
    "-e", "--empty", type=str, default="-", help="How to represent empty strings. Defaults to a hyphen."
)
parser.add_argument("--bool_true", type=str, default="YES", help="How to represent true values. Defaults to YES.")
parser.add_argument("--bool_false", type=str, default="NO", help="How to represent false values. Defaults to NO.")
args = parser.parse_args()

ifc_file = ifcopenshell.open(args.ifc)
parser = ifcfm.Parser(preset=args.preset)
parser.parse(ifc_file)
writer = ifcfm.Writer(parser)
writer.write(null=args.null, empty=args.empty, bool_true=args.bool_true, bool_false=args.bool_false)
if args.format == "csv":
    writer.write_csv(args.spreadsheet, delimiter=args.delimiter)
elif args.format == "ods":
    writer.write_ods(args.spreadsheet)
elif args.format == "xlsx":
    writer.write_xlsx(args.spreadsheet)
