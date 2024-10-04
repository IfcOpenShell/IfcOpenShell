Writing documentation
=====================

A great way to contribute without writing code is to help writing
documentation. Please reach out before contributing as the software is still in
an alpha state and portions may not be worth documenting as it changes too
frequently.

Philosophy
----------

The documentation is split into three sections:

1. **Quickstart**: a crash course where a user should be able to go from
   nothing to doing the most basic, common tasks. It is not comprehensive, but
   a highly focused tutorial style "taster" of what's available. It should be
   kept very short, aiming to acquaint new users within an hour.
2. **Guides**: a guidebook style, topic-driven series of articles discussing
   things of interest, or tutorials that cover common workflows. This should
   contain lots of images.
3. **Reference**: a comprehensive index of the entire interface and all
   available features.

Documentation should not be a guide to IFC. Users should not have to know what
IFC is.

Official documentation should be polished and maintained. Less documentation of
a higher quality that is kept updated with every release is preferred to more
documentation with stubs, incomplete or inaccurate information.

Syntax
------

All documentation is written in ReStructured Text and is available in the
`Bonsai docs directory
<https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/bonsai/docs>`_.
You can press the edit button on the top right on any documentation page to
quickly edit their content.

Links
^^^^^

You can link to

.. code-block:: restructuredtext

  `external websites
  <https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html>`_

(note the space between the url and the link text).  You can also link to
sections on the same page, like

.. code-block:: restructuredtext

  :ref:`contribute/writing_docs:Writing technical documentation`
  
or with

.. code-block:: restructuredtext

  :ref:`custom text<contribute/writing_docs:writing technical documentation>`.
  
Traditional references like 
  
.. code-block:: restructuredtext
 
  `Writing technical documentation`_

work too but are discouraged. You can link to other pages, like this:

.. code-block:: restructuredtext

  :doc:`Hello World<hello_world>`

or sections within other pages, like this:

.. code-block:: restructuredtext

  :ref:`devs/installation:unstable installation`

We have ``autosectionlabel`` enabled so it is not necessary to manually create labels. The depth of sections
with automatic labels is set to 2, so the third level of titles
will not get automatic labels to avoid duplication.

You can still create labels manually. This way you would ensure links still works when documentation is refactored.

.. code-block:: restructuredtext

    .. _My label:

    My Section
    ==========

    :ref:`Link to My Section <My label>`

This link will work across the documentation. Make sure the label is globally unique.

Images
^^^^^^

The following colours and annotation styles should be used for annotating
images. All stroke widths are 3px with a corner radius of 3px.  Horizontal
underlines are 5px with a corner radius of 2px. The dark green is ``39b54a`` and
the light green is ``d9e021``.

.. image:: images/documentation-style.png

Special keywords such as **Technical Terminology** that the user should be
aware of should be bolded, titlecased, and used consistently. You *may*
use italics to emphasize words or phrases. Inline code must be ``quoted`` and
longer code snippets may use code blocks.

.. code-block:: bash

    cd /path/to/bonsai
    ls

Be sure to specify the language to enable syntax highlighting.

.. code-block:: python

   print("Hello, world!")

A button may be used to point users to a critical sample file or
download.

.. container:: blockbutton

    `Visit critical link <https://bonsaibim.org>`__

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
    <https://bonsaibim.org>`__ links.

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

.. code-block:: bash

    pip install furo
    pip install sphinx-autoapi
    pip install sphinx-copybutton

Now you can generate the documentation:

.. code-block:: bash

    cd /path/to/ifcopenshell/src/bonsai/docs/
    make html
    cd _build/html
    python -m http.server

.. warning::

.. warning::

   Depending on your machine and environment, you might need to use ``.\make`` instead of ``make``.

You will now have a local webserver running hosting the documentation. Your terminal 
will return something like seen underneath, replace [::] with localhost. 

.. code:: console
      
      Serving HTTP on :: port 8000 (http://[::]:8000/) ...
      
Streamlining your workflow
^^^^^^
Now that you have added or changed some content in the documentation, you may want to see it on the webserver.
Initially you can:

- Kill the terminal, eg. the server.
- Run the make and build sequence as above again.

.. tip::

   If you make small incremental changes, you can avoid the cd navigation in many IDE's 
   by right clicking on the docs folder and open a fresh terminal from there.

This will work, but it is not very efficient. You can streamline your workflow by setting
up a run and debug configuration in your IDE. Below is an example for VScode placed in your 
.vscode folder in the root.

*task.json*

.. code:: json
      
    {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Build and Serve Docs",
                "type": "shell",
                "command": "powershell",
                "args": [
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    "cd D:/ifcopenshell/src/bonsai/docs/; .\\make html; cd _build/html; python -m http.server"
                ],
                "group": {
                    "kind": "build",
                    "isDefault": true
                },
                "problemMatcher": []
            }
        ]
    }

*launch.json*

.. code:: json
      
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "BonsaiDocsServer",
                "type": "python",
                "request": "launch",
                "program": "D:/ifcopenshell/src/bonsai/docs/_build/html",
                "args": ["-m", "http.server"],
                "preLaunchTask": "Build and Serve Docs",
                "console": "integratedTerminal"
            }
        ]
    }

Now you can run the debugger, it will build the documentation and start the server.
Simply stop debugging to stop the server and rerun the debugger to see your changes.

 



