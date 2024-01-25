IfcExcel
======

IfcExcel lets you view and edit IFC data using spreadsheets or tabular datasets, and review metadata easily.

Library installation
-------------------

To install the library, you need some python library dependencies :

```bash
pip install ifcopenshell -U
pip install openpyxl -U
pip install pandas -U
pip install lark -U
```

Export Excel
-------------------

Import library

```python
import ifcopenshell
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
```

Open IFC file

```python
file_path = r"model.ifc"
ifc_file = ifcopenshell.open(file_path)
```

Get all Classes

```python
# get all classes
classes = ifc_file.by_type("IfcProduct")
# print all class name
class_names = [class_name.is_a() for class_name in classes]
class_names = list(set(class_names))
class_names.sort()
```

Export to Excel

```python
file_name = "result.xlsx"
with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
    for class_name in class_names:
        objects = ifc_file.by_type(class_name)
        result_df = pd.DataFrame()
        for object in objects:
            class_data = {}
            # get dict of properties and values
            psets  = ifcopenshell.util.element.get_psets(object)
            for name, value in psets.items():
                if isinstance(value, dict):
                    for key, val in value.items():
                        class_data[key] = val
                else:
                    pass
            class_df =  pd.DataFrame(class_data, index=[0])
            result_df = pd.concat([result_df, class_df], ignore_index=True)
        if(result_df.empty):
            continue
        result_df.to_excel(writer, sheet_name=class_name, index=False)
        # set auto fit column width
        worksheet = writer.sheets[class_name]
        for idx, col in enumerate(worksheet.columns):
            worksheet.column_dimensions[col[0].column_letter].width = 20

```

Read Excel
-------------------

Read excel 
```python
file_name = "result.xlsx"
df = pd.read_excel(file_name, sheet_name=None)
print(list(df.keys()))
```

This documentation provides clear and organized instructions for using the IfcExcel library to export and read IFC data in Excel. Adjustments can be made based on your specific documentation requirements.

To custom more detail, please refer to the repo [Ifc-to-excel](https://github.com/chuongmep/Ifc-to-excel)