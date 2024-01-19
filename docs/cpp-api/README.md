# IfcOpenShell C++ API documentation

This folder contains the setup to build the IfcOpenShell C++ API documentation from the source code.

## Generating the documentation

> Prerequisites:
> 
> Make sure to have [Doxygen](https://www.doxygen.nl) and [Graphviz](https://graphviz.org) installed into your `$PATH` variable.
> 
> The documentation also use the [doxygen-awesome](https://jothepro.github.io/doxygen-awesome-css) theme as a git submodule.

Build with the command (from within the `/docs/cpp-api` folder):

```shell
$ doxygen
```

To include the current git commit hash into the build documentation, use the following command:

```shell
$ PROJECT_NUMBER=$(git rev-parse --short HEAD) doxygen
```

This will extract the current commit hash in short version and sets the propper ENV variable used by doxygen.

The generation of the documentation might take a while depending on your systems hardware, as it is configured to generate the Class graphs using .

The resulting documentation is located unter `/cpp-api/output/html` and can be directly accessed with your browser:

```shell
$ open ./output/html/index.html
```
