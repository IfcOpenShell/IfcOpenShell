import importlib

modules = {
    "project": None,
    "search": None,
    "bcf": None,
    "root": None,
    "unit": None,
    "model": None,
    "georeference": None,
    "context": None,
    "drawing": None,
    "misc": None,
    "attribute": None,
    "type": None,
    "spatial": None,
    "void": None,
    "aggregate": None,
    "geometry": None,
    "cobie": None,
    "resource": None,
    "cost": None,
    "sequence": None,
    "group": None,
    "system": None,
    "structural": None,
    "boundary": None,
    "profile": None,
    "material": None,
    "style": None,
    "layer": None,
    "owner": None,
    "pset": None,
    "qto": None,
    "classification": None,
    "constraint": None,
    "document": None,
    "pset_template": None,
    "clash": None,
    "lca": None,
    "csv": None,
    "bimtester": None,
    "diff": None,
    "patch": None,
    "covetool": None,
    "augin": None,
    "debug": None,
}

for name in modules.keys():
    modules[name] = importlib.import_module(f"blenderbim.bim.module.{name}")
    
def get_modules():
    return modules