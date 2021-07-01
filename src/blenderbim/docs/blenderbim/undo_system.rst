Undo system
===========

Supporting undo and redo is quite a complex problem because the Blender undo
system only keeps track of changes occuring in the Blender system. However,
changes actually occur in two other locations that Blender doesn't know about:
the IFC dataset, and the BlenderBIM Add-on system that synchronises Blender and
the IFC dataset.

Let's see how undo works in a basic Blender add-on without IFC or the BlenderBIM
Add-on getting involved.

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

This scenario where there is pure IfcOpenShell never occurs with the BlenderBIM
Add-on, so let's put both of them together.

.. code-block:: python
    :emphasize-lines: 5,7,8,10,13

    class Foobar(bpy.types.Operator):
        bl_idname = "foobar"
        bl_label = "Foobar"
        bl_options = {"REGISTER", "UNDO"}
        transaction_key: bpy.props.StringProperty()

        def execute(self, context):
            return IfcStore.execute_ifc_operator(self, context)

        def _execute(self, context):
            ifcopenshell.api.run("foo.bar", IfcStore.get_file())
            context.scene.name = "Foobar"
            bpy.ops.foobaz(transaction_key=self.transaction_key)
            return {"FINISHED"}

When your operator manipulates (creates, removes, or edits) IFC data directly or
indirectly (i.e. through calling another operator), your operator must have a
``transaction_key`` property assigned. The purpose of this transaction key is so
that if the operator is ever called from another operator, it can identify that
changes in the IFC data belong to a parent transaction. In this example, it is
also calling another operator ``bpy.ops.foobaz``, which manipulates IFC as well,
so we have to pass along the transaction key so ``bpy.ops.foobaz`` gets treated
as a sub-transaction.

In this example, we call ``return IfcStore.execute_ifc_operator(self, context)``
in the ``execute`` function. This is a special wrapper which begins an IFC
transaction, runs your operator's ``_execute`` function, then ends the IFC
transaction. This wrapper ensures that any IFC data manipulations within your
actual ``_execute`` function gets captured in a single transaction. In addition
to tracking all changes in the IFC data, it also tracks changes in the
``id_map`` and ``guid_map``.

If, however, your operator manipulates data that is not tracked by Blender, is
not tracked in the IFC data, and is not tracked in the element map, then you
will have to write your own rollback (undo) and commit (redo) code for your
operator. Here is an example.

.. code-block:: python

    class Foobar(bpy.types.Operator):
        bl_idname = "foobar"
        bl_label = "Foobar"
        bl_options = {"REGISTER", "UNDO"}
        transaction_key: bpy.props.StringProperty()

        def execute(self, context):
            old_value = Foo.bar
            result = self._execute(context)
            new_value = Foo.bar
            self.transaction_data = {"old_value": old_value, "new_value": new_value}
            IfcStore.add_transaction(self)
            return result

        def _execute(self, context):
            Foo.bar = "baz"
            return {"FINISHED"}

        def rollback(self, data):
            Foo.baz = data["old_value"]

        def commit(self, data):
            Foo.baz = data["new_value"]

Note that there is a distinction between ``execute`` and ``_execute``. This
recommended convention allows you to quickly discern undo state tracking code
from regular operation code.
