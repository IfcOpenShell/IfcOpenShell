bSDD
====

The **buildingSMART Data Dictionary** (bSDD) is an online RESTful centralised
API provided by buildingSMART that allows you to search for standardised
classifications and properties.

For example, if you want to assign a Uniclass classification system (popular in
the UK) or an Omniclass classification system (popular in the US) to elements
in your model, instead of downloading the classification system from their
website, you can directly search the bSDD. This ensures that you are always up
to date, and that codes are entered correctly (without spelling mistakes,
correct formatting, etc).

The bSDD search results may also be filtered based on IFC class. This will make
it quick to shortlist relevant classification codes and properties to a
particular object.

The bSDD also stores information on whether or not classification systems
require additional standard properties to be filled out, and whether they
should be filled out in a particular way. For example, all countries need to
fill out a "Fire Rating" property for walls, but they have different ways to
fill it out. Local governments (or companies) may submit their standard to the
bSDD so that all bSDD-compatible BIM applications can look up the property and
fill it out in a standardised way (such as picking for a list of preset
possible values defined by the local government).

More reading:

1. `Swagger API docs <https://bs-dd-api-prototype.azurewebsites.net/swagger/index.html>`_
2. `bSDD Github Repository <https://github.com/buildingSMART/bSDD>`_

PyPI
----

.. code-block::

    pip install bsdd

Examples
--------

Learning how to use the bSDD is best done by reading the official Swagger API docs.

.. code-block:: python
    from bsdd import Client,apply_ifc_classification_properties
    from pprint import pprint

    client = Client()

    # Get a list of "dictionary domains". For example, Uniclass (by the NBS organisation) might be one domain.
    pprint(client.get_dictionary())

    # For example, search the Netherland's Nlsfb2005 classification standard for all codes that apply to an IfcWall.
    pprint(client.search_in_dictionary("https://identifier.buildingsmart.org/uri/nlsfb/nlsfb2005/2.2", related_ifc_entity="IfcWall"))

    # And, search the classification for external walls(buitenwanden) that apply to an IfcWall.
    pprint(client.search_class(search_text='buitenwanden',dictionary_uris="https://identifier.buildingsmart.org/uri/nlsfb/nlsfb2005/2.2", related_ifc_entities=["IfcWall"]))

    # Alternatively, search up a particular classification code.
    data = client.get_class("https://identifier.buildingsmart.org/uri/nlsfb/nlsfb2005/2.2/class/21.21")
    pprint(data)

    # You may also apply default properties (if the classification system on
    # the bSDD defines them) to your IFC element. For example, if a
    # classification code is for a load bearing wall, it can automatically set
    # the "LoadBearing" property to True for you.
    apply_ifc_classification_properties(ifc_file, element, data["classProperties"])
