# ifc2ca
Files and scripts for the use of [`Code_Aster`](https://code-aster.org) in IFC-driven FEM analyses

## File Organisation

## Scripts:

- [`ifc2ca.py`](ifc2ca.py): a python script to extract and create a `json` file from an `ifc` file
- [`scriptSalome.py`](scriptSalome.py): a python script to run in the [`Salome-Meca`](https://www.code-aster.org/spip.php?article303) environment. Creates the geometry and the mesh of the structure
- [`scriptCodeAster.py`](scriptCodeAster.py): a python script to create the input file (`.comm`) for Code_Aster
- [`scriptSalomeBonded.py`](scriptSalomeBonded.py): a python script to run in the [`Salome-Meca`](https://www.code-aster.org/spip.php?article303) environment. Creates the geometry and the mesh of the structure by bonding together all structural elements (no connections are considered)
- [`scriptCodeAsterBonded.py`](scriptCodeAsterBonded.py): a python script to create the input file (`.comm`) for Code_Aster for the "bonded" case

## Analysis Models

A number of analysis models with all the relative input/output and script files are provided in [this repository](https://github.com/IfcOpenShell/analysis-models) within the IfcOpenShell Organization

---

## Current Status

Read [Change Log](changelog.md)
