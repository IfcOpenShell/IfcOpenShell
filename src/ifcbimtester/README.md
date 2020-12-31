# BIMTester
### Packages to be installed
+ behave
+ pystache
+ ifcopenshell


### Start bimtester Gui from a shell
```
python3 ./bimtester.py -g
```

### Create a binary out of the Python package
+ The commands needs to be updated
+ Unix:
`$ pyinstaller --onefile --clean --icon=icon.ico --add-data "features:features" bimtester.py`
+ Windows:
 `$ pyinstaller --onefile --clean --icon=icon.ico --add-data "features;features" bimtester.py`


### Translation files
+ the binary mo translation files are not part of the repo
+ they might be needed to be recreated
+ use the following commands on Linux
```
cd YourIfcopenshellRepository/src/ifcbimtester/bimtester/locale
pybabel compile -d .

```
