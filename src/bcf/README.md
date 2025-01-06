# bcf

A simple Python implementation of the BCF standard. Manipulation of BCF-XML is
available via `bcfxml.py` and manipulation of BCF-API is available via
`bcfapi.py`.

Python files in 'model' folder are automatically generated from .xsd files (located in 'xsd' folder).
To regenerate them you can use `make models`.
The only exception is 'v2/model/extensions.py', see it's note for the details.
