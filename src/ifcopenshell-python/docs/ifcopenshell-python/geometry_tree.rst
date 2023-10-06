Geometry tree
=============

IfcOpenShell includes a utility to build a unbalanced binary tree of geometry
and their bounding boxes. After a tree is built, you can efficiently select
geometry by specifying a point, radius, or bounding box.

.. image:: images/geometry-tree.png

The most efficient way to build tree is by using the iterator, as shown in the
example below:

.. code-block:: python

    import multiprocessing
    import ifcopenshell
    import ifcopenshell.geom

    tree = ifcopenshell.geom.tree()
    settings = ifcopenshell.geom.settings()
    iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
    if iterator.initialize():
        while True:
            tree.add_element(iterator.get_native())
            if not iterator.next():
                break

Once built, there are three methods you can use to select elements in the tree:
``select_box``, ``select``, and ``select_ray``.

``select_box`` lets you query for elements that contain a point or another
element. However, it only checks the bounding box of elements instead of their
exact geometry. This is the fastest approach and is recommended if you don't
need precise geometry selection.

``select`` lets you query for elements that contain a point, a sphere, or
another element.  ``select`` is similar to select box, but additionally
considers the actual geometry of the object. This is slower but more precise.

``select_ray`` lets you query for elements that intersect with a ray.

Selecting elements using bounding boxes
---------------------------------------

You may select all elements that have a bounding box containing the point with
XYZ coordinates of ``(0., 0., 0.)``.

.. code-block:: python

    # This will return a list of elements.
    # E.g.: [#66=IfcFurniture('3I53aQSFrFhRRaMHWNp8pD', ...), #96=IfcFurniture('0t5avJ3o956wj73wyBw0nO', ...)]
    elements = tree.select_box((0., 0., 0.))

.. note::

    All coordinates and length arguments must be specified in meters.

You may select all elements based on another element's bounding box. It will
return:

1. The queried element itself (i.e. a wall in this example)
2. Any elements fully contained by the wall
3. Any elements fully containing the wall
4. Any elements intersecting the wall

.. code-block:: python

    wall = ifc_file.by_type("IfcWall")[0]
    elements = tree.select_box(wall)

You may also select elements that are completely within another element's
bounding box. It will return:

1. The queried element itself (i.e. a wall in this example)
2. Any elements fully contained by the wall

.. code-block:: python

    elements = tree.select_box(wall, completely_within=True)

    # Alternatively, you may also specify an extension to dilate the bounding
    # box of the wall.
    elements = tree.select_box(wall, completely_within=True, extend=5.)

Selecting elements using precise geometry
-----------------------------------------

You may select all elements that have geometry containing the point with XYZ
coordinates of ``(0., 0., 0.)``.

.. code-block:: python

    elements = tree.select((0., 0., 0.))

.. note::

    All coordinates and length arguments must be specified in meters.

You may also select all elements that have geometry intsecting with a sphere,
represented by a centerpoint and a radius. This will return:

1. Any elements fully contained by the sphere
2. Any elements intersecting the sphere

.. code-block:: python

    # This extension is also in meters.
    elements = tree.select((0., 0., 0.), extend=5.)

You may select all elements based on another element's geometry. It will
return:

1. The queried element itself (i.e. a wall in this example)
2. Any elements fully contained by the wall
3. Any elements fully containing the wall
4. Any elements intersecting the wall

.. code-block:: python

    wall = ifc_file.by_type("IfcWall")[0]
    elements = tree.select(wall)

You may also select elements that are completely within another element's
geometry. It will return:

1. The queried element itself (i.e. a wall in this example)
2. Any elements fully contained by the wall

.. code-block:: python

    elements = tree.select_box(wall, completely_within=True)

    # Alternatively, you may also specify an extension to dilate the geometry
    # of the wall.
    elements = tree.select_box(wall, completely_within=True, extend=5.)

Selecting elements using a ray
------------------------------

You may select all elements that intersect with a ray. A ray is not infinite,
but instead must have a length. The default length is 1000 meters.

This returns a list of ray intersection results, which contain information
about the element it intersects with along with the point of intersection. This
may mean that the same element is returned multiple times if it intersects
multiple times.

.. code-block:: python

    origin = (0., 0., 0.)
    direction = (1., 0., 0.)
    results = tree.select_ray(origin, direction, length=5.)

    for result in results:
        print(ifc_file.by_id(r.instance.id())) # The element the ray intersects with
        print(list(r.position)) # The XYZ intersection point
        print(r.distance) # The distance between the ray origin and the intersection
        print(list(r.normal)) # The normal of the face being intersected
        print(r.dot_product) # The dot product of the face being intersected with the ray
