# IfcOpenShell C++ API documentation

This directory contains the Sphinx, Doxygen, Breathe, and Exhale configuration
for the IfcOpenShell C++ API reference. During a Sphinx build, Exhale runs
Doxygen, Breathe consumes the generated XML, and Exhale creates the API pages.

## Prerequisites

- Python 3.10 or newer
- [Doxygen](https://www.doxygen.nl/)
- [Graphviz](https://graphviz.org/)

Install the Python dependencies from this directory:

```shell
python -m pip install -r requirements.txt
```

Both `doxygen` and `dot` must be available on `PATH`. For the standard Windows
install locations, this can be done for the current PowerShell session with:

```powershell
$env:Path = "C:\Program Files\doxygen\bin;C:\Program Files\Graphviz\bin;$env:Path"
```

## Generating the documentation

From this directory, run:

```shell
python -m sphinx -M html . output -W --keep-going
```

To include the current Git commit in Doxygen's project metadata, set
`PROJECT_NUMBER` before building. For example, in PowerShell:

```powershell
$env:PROJECT_NUMBER = git rev-parse --short HEAD
python -m sphinx -M html . output -W --keep-going
```

Or in a POSIX shell:

```shell
PROJECT_NUMBER=$(git rev-parse --short HEAD) python -m sphinx -M html . output -W --keep-going
```

Alternatively, configure the main CMake project with
`-DBUILD_DOCUMENTATION=ON` and build the `cpp_api_docs` target.

The generated documentation is written to `output/html/index.html`. The
generated Doxygen XML and Exhale sources are kept under `output/` as build
artifacts.

The generated headers under `src/ifcparse/schemas` are intentionally excluded
from this documentation build.
