Undo system
===========

Supporting undo and redo is quite a complex problem because the Blender undo
system only keeps track of changes occurring in the Blender system. However,
changes actually occur in two other locations that Blender doesn't know about:
the IFC dataset, and the Bonsai system that synchronises Blender and the IFC
dataset.

Let's see how undo works in a basic Blender add-on without IFC or Bonsai
getting involved.

.. code-block:: python
    :emphasize-lines: 4

    class Foobar(bpy.types.Operator):
        bl_idname = "foobar"
        bl_label = "Foobar"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            context.scene.name = "Foobar"
            return {"FINISHED"}

This operation changes Blender data. The important line is ``bl_options =
{"REGISTER", "UNDO"}``, which tells Blender to keep track of it as a single
transaction in its undo history. When you press undo or redo, Blender figures
out all the changes automatically and you don't need to do anything.

If you have an operator that only manipulates (creates, removes, or edits)
Blender data, this solution is sufficient.

Now let's look at pure IfcOpenShell.

.. code-block:: python
    :emphasize-lines: 3,5

    import ifcopenshell
    model = ifcopenshell.open("foo.ifc")
    model.begin_transaction()
    model.create_entity("IfcWall")
    model.end_transaction()
    model.undo()
    model.redo()

Pure IfcOpenShell let's you start and stop recording transactions whenever you
want. Since IfcOpenShell has no interface, you manually run code like
``model.undo()`` and ``model.redo()`` to undo and redo.

This scenario where there is pure IfcOpenShell never occurs with Bonsai.
Instead, stuff happens in Blender operators.

.. code-block:: python
    :emphasize-lines: 6,7

    class Foobar(bpy.types.Operator):
        bl_idname = "foobar"
        bl_label = "Foobar"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            return IfcStore.execute_ifc_operator(self, context)

        def _execute(self, context):
            ifcopenshell.api.run("foo.bar", IfcStore.get_file())
            return {"FINISHED"}

When your operator manipulates (creates, removes, or edits) IFC data directly or
indirectly (i.e. through calling another operator), your operator must be
wrapped in an ``IfcStore.execute_ifc_operator`` call. This wrapper will:

1. Begin a Bonsai transaction
2. Begin an IfcOpenShell transaction
3. Run your operator's ``_execute``.
4. End the IfcOpenShell transaction
5. End the Bonsai transaction

The IfcOpenShell transaction keeps track of IFC data changes, and the Bonsai
transaction keeps track of all other custom data changes, like changes in the
``id_map`` and ``guid_map``. For the vast majority of operations, this wrapper
provides everything that you need.

If, however, your operator manipulates data that is not tracked by Blender, is
not tracked in the IFC data, and is not tracked in the element map, then you
will have to write your own rollback (undo) and commit (redo) code for your
operator. Here is an example.

.. code-block:: python

    class Foobar(bpy.types.Operator):
        bl_idname = "foobar"
        bl_label = "Foobar"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            IfcStore.begin_transaction(operator)
            old_value = Foo.bar
            result = self._execute(context)
            new_value = Foo.bar
            self.transaction_data = {"old_value": old_value, "new_value": new_value}
            IfcStore.add_transaction_operation(self)
            IfcStore.end_transaction(operator)
            return result

        def _execute(self, context):
            Foo.bar = "baz"
            return {"FINISHED"}

        def rollback(self, data):
            Foo.baz = data["old_value"]

        def commit(self, data):
            Foo.baz = data["new_value"]

Note that there is still a distinction between ``execute`` and ``_execute``.
This recommended convention allows you to quickly discern undo state tracking
code from regular operation code.
