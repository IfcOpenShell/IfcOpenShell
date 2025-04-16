# ifc5d

## Description

Ifc5D is a collection of utilities of manipulating cost-related data to and from
formats, reports, and optimisation engines.

Currently supported:

 - CSV to IFC
 - IFC to XLSX
 - IFC to CSV
 - IFC to ODS


Planned (would you like to contribute? Please reach out!):


 - IFC to PDF
 - ODS to CSV
 - XLSX to CSV
 - IFC to Graph

## Usage CSV to IFC

See example files as a CSV file format reference:
- `sample_cost_schedule_house_FR.csv` / `.ods`
- `schedule.csv`, `rates.csv` (schedule of rates example)

Some notes on the format:
- Empty lines are ignored.
- Importing ods/xlsx is not currently supported, only csv.

## Usage IFC to CSV, ODS, XSLS

#TODO

### CLI app for converting IFC files to CSV, ODS or XLSX format.

Usage:
    python ifc5Dspreadsheet.py input_file output_file [-l log_file] [-f format_type]

Arguments:
    input_file (str): The path to the input IFC file to process.
    output_file (str): The output directory for CSV or filename for other formats.

Options:
    -l, --log log_file (str): The path to the file where errors should be logged. Default is process.log.
    -f, --format format_type (str): The output format to export in (csv/ods/xlsx). Default is csv.

Examples:
    python ifc5Dspreadsheet.py "C:\Users\Dev-Machine\Desktop\test_cost.ifc" rev_01_schedule -l error.log -f ODS
    python ifc5Dspreadsheet.py "C:\Users\Username\Desktop\test_cost.ifc" "C:\Users\Username\Desktop" -l error.log -f CSV

### Scripting:

Example for ODS exports:

```
import ifcopenshell
from ifc5d.ifc5Dspreadsheet import Ifc5DOdsWriter

file = "path_to_file/file.ifc"

path = "directory/cost_schedule"
writer = Ifc5DOdsWriter(file=file, output=path)
writer.write()

```