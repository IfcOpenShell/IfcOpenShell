rem Hack while we do not have bcf-client on our conda ifcopenshell channel yet
rem pip install bcf-client
cd test && python tests.py
cd ../src/ifcopenshell-python && mv ifcopenshell ifcopenshell-local && make test