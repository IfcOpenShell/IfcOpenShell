import importlib
import ifcopenshell.api


def run(usecase_path, ifc_file=None, **settings):
    importlib.import_module(f"ifcopenshell.api.{usecase_path}")
    module, usecase = usecase_path.split(".")
    usecase_class = getattr(getattr(getattr(ifcopenshell.api, module), usecase), "Usecase")
    if ifc_file:
        return usecase_class(ifc_file, **settings).execute()
    return usecase_class(**settings).execute()
