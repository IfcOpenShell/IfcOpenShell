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

Simple example:
```python
import ifc5d.csv2ifc

csv2ifc = ifc5d.csv2ifc.Csv2Ifc(csv_filepath, ifc_file)
csv2ifc.execute()
```

See example files as a CSV file format reference:
- `sample_cost_schedule_house_FR.csv` / `.ods`
- `schedule.csv`, `rates.csv` (schedule of rates example)

Some notes on the format:
- Empty lines are ignored.
- Importing ods/xlsx is not currently supported, only csv.
- 'Property', 'Query' columns are required only for non-schedule of rates cost schedules.
- 'Index' was preferred for import hierarchy source over 'Hierarchy' as it's easier to edit from the table view.
- In non-SoR if cost values are not provided in any way and cost item has subitems, then `SUM()` will added automatically as it's cost value.  
Mixing `SUM()` cost items and items with their own value is not supported.

## Columns Description

**General Columns**
- 'Index' - is a hierarchy depth that's used for building hierarchy during csv import. Starts from 1.  
E.g. root items of the same level have index '1', their children have '2', etc.
- 'Name' - IfcCostItem.Name.  
Some older exports may have 'Description' field instead of 'Name', it is safe to just rename it.
- 'Identification' - IfcCostItem.Identification.
- 'Unit' - IfcCostValue unit, should be provided as a unit symbol.  
E.g. 'm2', 'm3', 'kg', etc.
- 'Value' - overall cost value to assign to IfcCostItem.
- All other columns that are not mentioned in this list or the one below will be interpeted as cost value categories.  
Note that if 'Value' is provided, it takes priority over subcategories.

Non-schedule of rates columns:
- 'Quantity' - total cost item quantity.
- 'Property' - quantity name that should be added to IfcCostItem from 'Query' elements.  
If 'Query' is provided, 'Property' can be left empty or set to "COUNT" to count queried elements.
- 'Query' - selector query for elements to assign to IfcCostItem.  
If query is provided, it takes priority over 'Quantity' (using both is not supported).

**Exported informational columns (not used for import)**
- 'Hierarchy' is just an informational column that doesn't affect the import.  
E.g. '1', '1.1', '1.1.1', etc.
- 'Id' - IfcCostItem.id
- 'RateSubtotal' - all IfcCostItem specific costs, not including subitem costs.
- 'TotalPrice' - IfcCostItem total cost, including subitem sum calculations.




## Usage IFC to CSV, ODS, XSLS

Simple example:
```python
import ifc5d.ifc5Dspreadsheet

# csv.
writer = ifc5d.ifc5Dspreadsheet.Ifc5DCsvWriter(ifc_file, csv_dir)
writer.write()

# ods.
writer = ifc5d.ifc5Dspreadsheet.Ifc5DOdsWriter(ifc_file, ods_dir)
writer.write()

# xlsx.
writer = ifc5d.ifc5Dspreadsheet.Ifc5DXlsxWriter(ifc_file, xlsx_dir)
writer.write()
```

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