Writing docs
============

A great way to contribute without writing code is to help writing
documentation. Please reach out before contributing as the software is still in
an alpha state and portions may not be worth documenting as it changes too
frequently.

Writing technical documentation
-------------------------------

All documentation is written in ReStructured Text and is available in the
`BlenderBIM Add-on docs directory
<https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.7.0/src/blenderbim/docs>`_.
You can press the edit button on the top right on any documentation page to
quickly edit their content.

You can link to `external websites
<https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html>`_.
You can also link to sections on the same page, like `Writing technical
documentation`_. You can link to other pages, like :doc:`Hello
World<hello_world>` or sections within other pages, like
:ref:`devs/installation:unstable installation`. We have ``autosectionlabel``
enabled so it is not necessary to manually create labels.

The following colours and annotation styles should be used for annotating
images. All stroke widths are 3px with a corner radius of 3px.  Horizontal
underlines are 5px with a corner radius of 2px. The dark green is ``39b54a`` and
the light green is ``d9e021``.

.. image:: images/documentation-style.png

Special keywords such as **Technical Terminology** that the user should be
aware of should be bolded, titlecased, and used consistently. You *may*
use italics to emphasize words or phrases. Inline code must be ``quoted`` and
longer code snippets may use code blocks.

.. code-block:: console

    $ cd /path/to/blenderbim
    $ ls

Be sure to specify the language to enable syntax highlighting.

.. code-block:: python

   print("Hello, world!")

A button may be used to point users to a critical sample file or
download.

.. container:: blockbutton

    `Visit critical link <https://blenderbim.org>`__

You can use bulleted lists:

- Like.
- This.

Or ordered lists:

1. Like.
2. This.

.. note::

   Instead of writing "Note that XYZ ..." you should use notes sparingly to
   highlight "gotchas".

.. tip::

   Tips may be used to add a useful but optional suggestion.

.. warning::

   Warnings may be used to highlight common mistakes.

.. seealso::

    See also blocks should be used to reference `further reading
    <https://blenderbim.org>`__ links.

Tables can be very annoying to format. You can use a CSV table instead.

.. csv-table::
   :header: "Foo", "Bar", "Baz"

    "ABC", "01", "02"
    "DEF", "03", "04"

Building documentation
----------------------

If you want to build the documentation locally, the documentation system uses
`Sphinx <https://www.sphinx-doc.org/en/master/>`_. First, install the theme and
theme dependencies:

.. code-block:: console

    $ pip install furo
    $ pip install sphinx-autoapi
    $ pip install sphinx-copybutton

Now you can generate the documentation:

.. code-block:: console

    $ cd /path/to/ifcopenshell/src/blenderbim/docs/
    $ make html
    $ cd _build/html
    $ python -m http.server

You will now have a local webserver running hosting the documentation.
