# bsdd

A library to interact with the buildingSMART Data Dictionary (bSDD) API.
This packages is totally independent from other packages in IfcOpenShell and requires only a python installation to run.

## Installation

```bash
pip install git+https://git@github.com/ifcopenshell/ifcopenshell.git@v0.7.0#subdirectory=src/bsdd

# check your installation
python
>>> from bsdd import Client
>>> client = Client()
>>> [l["uri"] for l in client.get_dictionary()["dictionaries"] if "4.3" in l["uri"]][0]
'https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3'
```

## Develop

```bash
# create a fork in your domain
git clone git@github.com:<your-name>/IfcOpenShell.git
cd src/bsdd

# if you use vs code / pycharm, you can launch it from this folder
code .

# if you use conda/mamba. follow instructions below:
# otherwise setup a dev env in your preferred way.
mamba create -n bsdd-dev python pytest requests
mamba activate bsdd-dev

# run tests
pytest
```
