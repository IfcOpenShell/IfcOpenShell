Selector syntax
===============

A common task in querying IFC models is to filter or search for elements which
match particular criteria. For example, you might want to find all plasterboard
walls with a 2 hour fire rating on level 3.

Alternatively, you might want to fetch some data about a single element. For
example, you might want to fetch the fire rating property of an element, or the
type description of an element, or the net volume of a list of elements.

Once you've retreived your data, you might want to format it in some way. You
might want to ensure that all names are always uppercase. Or you might want to
take length values defined in feet, and apply imperial formatting such that it
shows both feet and inches including fractions.

These three usecases of filtering, getting a value, and formatting that value
are common and used in many utilities, such as in Bonsai, IfcCSV, IfcDiff,
IfcClash, IfcPatch, and IfcFM.

IfcOpenShell provides a custom syntax to consistently and concisely describe
filters, value queries, and formatting rules.

Filtering elements
------------------

Filtering is typically used to select any IFC element or type.

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.util.selector

    model = ifcopenshell.open("model.ifc")
    # Get all concrete walls and slabs.
    ifcopenshell.util.selector.filter_elements(model, "IfcWall, IfcSlab, material=concrete")

.. csv-table::
   :header: "Example Query", "Description"

    "``IfcElement``", "All physical IfcElements including subclasses like walls, doors, windows, etc. Yep, that's it! Nothing else. Literally just ``IfcElement``."
    "``IfcWall, IfcSlab``", "All walls and slabs. Technically, this is either a wall or a slab, but it's easier to describe it as all walls and slabs"
    "``IfcWall, IfcSlab, material=concrete``", "All walls made out of concrete and slabs made out of concrete. The material checks any assigned IfcMaterial with a matching name or category attribute."

    "``325Q7Fhnf67OZC$$r43uzK``", "A single element. Yep, just the GlobalId, nothing else! Easy."

    "``325Q7Fhnf67OZC$$r43uzK, 2VlJ7nbF5AFfQQuRvSWexT``", "A bunch of arbitrary elements."

    "``IfcWall, ! 325Q7Fhnf67OZC$$r43uzK``", "All walls except that one element."

    "``IfcElement, ! IfcWall``", "All elements except for walls."

    "``IfcDoor, Name=D01``", "Any doors named D01, notice how attributes match the IFC Attribute naming exactly"

    "``IfcDoor, Name=/D[0-9]{2}/``", "Any doors with the naming scheme of D followed by two numbers:"

    "``IfcWall, Pset_WallCommon.FireRating=2HR``", "Any 2 hour fire rated wall"

    "``IfcWall, IfcColumn, IfcBeam, IfcFooting, /Pset_.*Common/.LoadBearing=TRUE``", "Any load bearing structure"

    "``IfcElement, /Pset_.*Common/.FireRating != NULL``", "Any element with a fire rating property"

    "``IfcWall, type=WT01, location=""Level 3""``", "Any walls of wall type WT01 on level 3 (we quote Level 3 since it has a space)"

    "``IfcElement, classification=/Pr_.*/``", "Any maintainable product according to Uniclass tables"

    "``IfcWall, IfcSlab, ! 325Q7Fhnf67OZC$$r43uzK, material=concrete, /Pset_.*Common/.FireRating=2HR``", "Notice how there are intuitive rules that class and instance filters are OR whereas other filters are AND So here is any wall or slab except that one element that has a material of concrete and has a 2 hour fire rating"

    "``IfcSlab, material=concrete + IfcDoor``", "Finally, you can union facet lists together. So here is all concrete slabs, as well as all doors (regardless of concrete)"

    "``IfcDoor, IfcWindow + IfcWall, IfcSlab, material=concrete + 325Q7Fhnf67OZC$$r43uzK``", "Here's another example of unioning facet groups. All doors and window, and all concrete walls and slabs, plus that one random element"

    "``IfcPump, location=""Level 3""``", "Locations bubble up the hierarchy. So if a pump is in a space and that space is on Level 3, then you can say ""all pumps on level 3"" which will include that pump in the space."

The filter elements syntax works by specifying one or more groups of filters
separated by a ``+`` character. Each filter group will return a set of filtered
elements, and these are unioned together.

.. code-block::

    filter_group[ + filter_group]*

A filter group consists of one or more filters separated by a ``,`` character.
The filters are chained and apply from left to right.

.. code-block::

    filter[, filter]*

There are nine types of filters to choose from. Some of these filters will add
new elements to your filter group, and some will filter previously added
elements in your filter group based on their criteria.

.. csv-table::
   :header: "Filter", "Type", "Usage", "Example"

    "Class", "Add", "``[!] {{ifc_class_name}}``", "``IfcWall`` adds all IfcWall elements and their subclasses. ``! IfcWall`` subtracts all non-IfcWall elements from the filter group."
    "GlobalId", "Add", "``[!] {{global_id}}``", "``325Q7Fhnf67OZC$$r43uzK`` adds the single element with that GlobalId attribute. ``! 325Q7Fhnf67OZC$$r43uzK`` subtracts that single element."
    "Attribute", "Filter", "``{{name}}{{=}}{{value}}``", "``Name=Foo`` specifies the criteria that elements must have a ``Name`` attribute with a value of ``Foo``. Attribute names must be spelled exactly the same as in IFC, which means that they must start with an uppercase character."
    "Property", "Filter", "``{{pset}}.{{prop}}{{=}}{{value}}``", "``Pset_WallCommon.FireRating=2HR`` specifies the criteria that elements must have a ``Pset_WallCommon`` property set, with a ``FireRating`` property within it with a value of ``2HR``. The property set name and the property name are separated by a ``.``."
    "Type", "Filter", "``type{{=}}{{value}}``", "``type=Foo`` specifies the criteria that elements must have a type which has a ``Name`` attribute with a value of ``Foo``."
    "Material", "Filter", "``material{{=}}{{value}}``", "``material=Foo`` specifies the criteria that elements must have a IfcMaterial assigned directly or indirectly (such as within a layer set). That IfcMaterial must have either a ``Name`` or ``Category`` attribute with a value of ``Foo``."
    "Classification", "Filter", "``classification{{=}}{{value}}``", "``classification=Foo`` specifies the criteria that elements must have an IfcClassificationReference with an ``Identification`` attribute with a value of ``Foo``."
    "Location", "Filter", "``location{{=}}{{value}}``", "``location=Foo`` specifies the criteria that elements must be contained directly or indirectly in a spatial element with a ``Name`` attribute with a value of ``Foo``."
    "Parent", "Filter", "``parent{{=}}{{value}}``", "``parent=Foo`` specifies the criteria that elements must be a direct or indirect child in the spatial hierarchy to an element with a ``Name`` attribute with a value of ``Foo``."
    "Query", "Filter", "``query:{{keys}}{{=}}{{value}}``", "``query:types.count=0`` specifies the criteria that elements must have zero type occurrences. The query keys corresponds to the syntax used in the `Getting element values`_ section"

When you specify a filter with a ``{{=}}`` check, you can choose from one of
the following comparison checks:

.. csv-table::
   :header: "Comparison", "Description"

    "``=``", "Must equal the value. The data type of the value is automatically converted to match."
    "``!=``", "Must not equal the value."
    "``>``", "Must be greater than the value."
    "``>=``", "Must be greater than or equal to the value."
    "``<``", "Must be less than the value."
    "``<=``", "Must be less than or equal to the value."
    "``*=``", "Must contain the value."
    "``!*=``", "Must not contain the value."

When you specify a ``{{pset}}``, ``{{prop}}``, or ``{{value}}``, there are
three ways you can do so:

.. csv-table::
   :header: "Value Type", "Example", "Description"

    "Quoted string", "``""foo \""bar\"" baz""``", "The value must be in double quotes. The value may contain spaces, symbols, and other characters. If you need to use a double quote, you can escape it with a backslash. This is the safest, most general way to specify a value."
    "Unquoted string", "``foobarbaz``", "For convenience, if you have a simple value which contains no spaces or special characters, you are free to specify it as an unquoted string."
    "Regex string", "``/foo.*baz/``", "You may specify a Python-compatible regex pattern delimited by forward slashes. You can learn more about regular expressions from `Beginners Regex tutorial <https://regexone.com/>`_ and `Online Regex testing website <https://regex101.com/>`_."

Getting element values
----------------------

Given a single element, this syntax provides a simple way to extract a value
without needing to write complex code for it.

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.util.selector

    # Get the Name attribute of the wall's type.
    ifcopenshell.util.selector.get_element_value(wall, "type.Name")

.. csv-table::
   :header: "Example Query", "Description"

    "``class``", "Get the IFC class of the element."
    "``Name``", "Get the ``Name`` attribute."
    "``Pset_WallCommon.Status``", "Get the value of the ``Status`` property in the ``Pset_WallCommon`` property set."
    "``/Pset_.*Common/.Status``", "Get the value of the ``Status`` property in the any common property set."
    "``type.Name``", "Get the ``Name`` attribute of the element's relating type."
    "``types.count``", "Count the number of occurrences of a type."
    "``storey.Name``", "Get the ``Name`` attribute of the storey that the element is contained in."
    "``materials.count``", "Count the number of materials assigned to an element."
    "``material.Name``", "Get the name of the assigned material."
    "``material.item.0.Name``", "Get the name of the first item in a material set (e.g. the first material layer)"

The element value syntax works by specifying one or more query keys separated
by a ``.`` character. Each query key returns data based of the results of the
previous key.

.. code-block::

    key[.key]*

Valid keys are:

.. csv-table::
   :header: "Key", "Description"

    "``id``", "Gets the IFC ID (equivalent to ``.id()``)"
    "``class``", "Gets the IFC class (equivalent to ``.is_a()``)"
    "``predefined_type``", "Gets the predefined type of the element, taking into account inheritance."
    "``{{attribute}}``", "Gets the value of the attribute you specify. Attributes always start with an uppercase letter."
    "``{{pset}}``", "This gets the property set with the same name specified in ``{{pset}}``. Note that this can be ambiguous with ``{{attribute}}``. If there is an ambiguity, ``{{attribute}}`` takes priority."
    "``{{prop}}``", "If the previous key returns a property set, ``{{prop}}``  gets the value of a property with the same name specified in ``{{prop}}``. For this reason, often you specify both keys together, like this: ``{{pset}}.{{prop}}``."
    "``type``", "Gets the relating type of an element occurrence."
    "``types`` or ``occurrences``", "Gets the related objects of an element type."
    "``container``", "Gets the immediate spatial element that an element is contained in."
    "``space``", "Gets the first IfcSpace spatial element that an element is contained in."
    "``storey``", "Gets the first IfcBuildingStorey spatial element that an element is contained in."
    "``building``", "Gets the first IfcBuilding spatial element that an element is contained in."
    "``site``", "Gets the first IfcSite spatial element that an element is contained in."
    "``parent``", "Gets the parent element in the spatial hierarchy."
    "``classification``", "Gets the element's classification reference(s)"
    "``group``", "Gets the element's group(s)"
    "``system``", "Gets the element's system(s). This is a subset of group(s)."
    "``material`` or ``mat``", "Gets the assigned material, which may be a material set."
    "``item`` or ``i``", "If the previous key returns a material set, gets the relevant material set items"
    "``materials`` or ``mats``", "Gets a list of IfcMaterials assigned directly or indirectly (such as via a material set) to the element"
    "``profiles``", "Gets a list of IfcProfileDefs assigned (such as via a material profile) or used (such as in an extrusion) in the element"
    "``x``", "Gets the X coordinate of the element's placement"
    "``y``", "Gets the Y coordinate of the element's placement"
    "``z``", "Gets the Z coordinate of the element's placement"
    "``easting``", "Gets the map easting of the element's placement"
    "``northing``", "Gets the map northing of the element's placement"
    "``elevation``", "Gets the map elevation of the element's placement"
    "``count``", "If the previous key returns multiple things, count that list. Otherwise, return 1."
    "``{{number}}``", "If the previous key returns multiple things, fetch the ``{{number}}`` index (e.g. 0, 1, 2, 3, etc) item in that list."

When you specify a ``{{pset}}`` or ``{{prop}}``, there are three ways you can
do so:

.. csv-table::
   :header: "Value Type", "Example", "Description"

    "Quoted string", "``""foo \""bar\"" baz""``", "The value must be in double quotes. The value may contain spaces, symbols, and other characters. If you need to use a double quote, you can escape it with a backslash. This is the safest, most general way to specify a value."
    "Unquoted string", "``foobarbaz``", "For convenience, if you have a simple value which contains no spaces or special characters, you are free to specify it as an unquoted string."
    "Regex string", "``/foo.*baz/``", "You may specify a Python-compatible regex pattern delimited by forward slashes. You can learn more about regular expressions from `Beginners Regex tutorial <https://regexone.com/>`_ and `Online Regex testing website <https://regex101.com/>`_."

Formatting
----------

Given a value, this syntax allows a simple way to specify a set of formatting
rules. This is useful for configuring outputs of how data should be presented.

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.util.selector

    # Get the Name attribute of the wall's type.
    value = ifcopenshell.util.selector.get_element_value(wall, "type.Name")
    # Always display names in uppercase.
    ifcopenshell.util.selector.format(f'upper("{value}")')

Formatting queries are written similar to how you'd write functions or formulas
in spreadsheets. For example ``upper("foo")`` will produce ``FOO``. You may
nest formulas, for example ``concat(title("foo"), lower("Bar"))`` will produce
``Foobar``. Strings must be double quoted.

.. csv-table::
   :header: "Function", "Example", "Result", "Description"

    "``upper({{value}})``", "``upper(""Foo"")``", "``FOO``", "Uppercases a string."
    "``lower({{value}})``", "``lower(""Foo"")``", "``foo``", "Lowercases a string."
    "``title({{value}})``", "``title(""foo"")``", "``Foo``", "Titlecases a string."
    "``concat({{value}}[, {{value2}}]*)``", "``concat(""foo"", ""bar"")``", "``foobar``", "Concatenates two or more strings."
    "``round({{value}}, {{precision}})``", "``round(3.123, 0.1)``", "``3.1``", "Rounds ``{{value}}`` to the nearest ``{{precision}}``."
    "``number({{value}}[, {{decimal_separator}}[, {{thousands_separator}}]])``", "``number(1234.56, "","", ""."")``", "``1.234,56``", "Formats {{value}} with an optional custom {{decimal_separator}} and {{thousands_separator}}. The default separators are ``.`` and ``,``."
    "``metric_length({{value}}, {{precision}}, {{decimals}})``", "``metric_length(3.123, 0.1, 2)``", "``3.10``", "Rounds ``{{value}}`` to the nearest ``{{precision}}`` then displays using a certain amount of decimal places."
    "``imperial_length({{value}}, {{precision}}, {{input_unit}}, {{output_unit}})``", "``imperial_length(3.22, 4, ""foot"")``", "``3' - 3 3/4""``", "``The {{value}}`` may be specified either as ``foot`` or ``inch`` depending on ``{{input_unit}}``. The ``{{value}}`` is then rounded to the nearest ``1/{{precision}}`` inch then formatted using fractional feet and inches if ``{{output_unit}}`` is set to ``foot`` or just inches if ``{{output_unit}}`` is set to ``inch``."
