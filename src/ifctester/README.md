# ifctester

With **IfcTester**, you can author and read **Information Delivery Specification** - **IDS** - files and validate your IFC models against IDS to see if your model is compliant. After the audit, you can generate reports in console, as a web page, JSON or BCF file. It works from the command line, as a web app, or as a library.

## How to use it

### Command line use


```bash
# run console reporter
python -m ifctester example.ids example.ifc
python -m ifctester example.ids example.ifc -r Html -o report.html
```

Available flags:

- ``-r`` / ``--reporter``: The reporting method to view audit results. Availabe reporters: Console, Txt, Json, Html, Ods, Bcf
- ``--no-color``: Disable colour output (supported by Console reporting).
- ``--excel-safe``: Make sure exported ODS is safely exported for Excel.
- ``-o`` / ``--output``: Output file (supported for all types of reporting except Console).

### Code example

```python
import ifcopenshell
from ifctester import ids, reporter


# create new IDS
my_ids = ids.Ids(title="My IDS")

# add specification to it
my_spec = ids.Specification(name="My first specification")
my_spec.applicability.append(ids.Entity(name="IFCWALL"))
property = ids.Property(
    baseName="IsExternal",
    value="TRUE", 
    propertySet="Pset_WallCommon", 
    dataType="IfcBoolean",
    uri="https://identifier.buildingsmart.org/uri/.../prop/LoadBearing", 
    instructions="Walls need to be load bearing.",
    cardinality="required")
my_spec.requirements.append(property)
my_ids.specifications.append(my_spec)

# Save such IDS to file
result = my_ids.to_xml("SampleIDS.xml")

# open  IFC file:
my_ifc = ifcopenshell.open("MyIfcModel.ifc")

# validate IFC model against IDS requirements:
my_ids.validate(my_ifc)

# show results:
reporter.Console(my_ids).report()
```


### ifctester web app

Can be started by `cd webapp && python app.py`.
