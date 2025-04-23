Debugging Bonsai
================

This is a mini-guide to setting up an IDE and configuring it to debug Bonsai
more easily. It is currently specific to this writers own system (Ubuntu) but
this can be expanded by others.

.. warning::
   Attaching debugger to Blender may significantly decrease performance due to
   the debugger overhead.

VSCode Extension
--------------

1. **Install VSCode/VSCodium**: This will be system specific. I used the
   available snap package.

   .. code-block:: bash

      sudo snap install --classic codium

   I chose VSCodium to avoid Microsoft telemetry and data harvesting, but
   VSCode is going to be similar, and even a bit easier (i.e. step 3).

2. **Activate Python language support**: Start VSCode/VSCodium, open the
   Extensions tab, find the Python language support and activate it.

3. **Install Blender Addon**: This step depends on which IDE you chose.

   a. VSCode

      Open up the Extensions tab on the left, and search for the *Blender
      Development* extension. Select it, and click Install.

      I haven't actually tested this, but this should install the 
      *ms-vscode.cpptools* dependancy for you. If not, you may need to search
      for, and install, this extension too.

   b. VSCodium

      It seems VSCodium is not allowed to direct access the Marketplace, and
      due to licensing it is not possible to install the *Blender Development*
      extension because of the *ms-vscode.cpptools* dependancy.

      VSCodium's equivalent Marketplace does not (and could not due to
      licensing) provide a functioning *Blender Development* extension. (Or I'm
      an idiot... entirely possible).

      I've created an alternative *Blender Development* extension with the
      *ms-vscode.cpptools* dependancy removed.

      .. note::
         This alternative should also work in VSCode, but you may as well save
         yourself the hassle, and just use the original one.

      Download the *Blender Development* ``.vsix`` file from my GitHub fork
      using your browser from `this <https://github.com/sboddy/blender_vscode>`_
      repository. The ``.vsix`` is available on the Releases page.

      In VSCodium's Extensions sidebar install it with "**...**" ->
      "**Install from VSIX...**"

      If you are squeamish about downloading my ``.vsix``, you can review the
      single commit, clone the repo and create your own.

4. **Set the Blender config directory**: In **Settings** -> **Extensions** ->
   **Blender** -> "**Environment Variables**"
   edit the json file to set the ``BLENDER_USER_RESOURCE`` to the config folder
   you installed Bonsai to. *For me*:

   .. code-block:: json

      {
         "blender.environmentVariables": {
            "BLENDER_USER_RESOURCES": "/home/steve/.config/blender/4.2bonsai"
         }
      }

   .. warning::
      You `must` change that path to the correct value for your system.

5. **Unset the Just My Code flag**:  In **Settings** -> **Extensions** ->
   **Blender** -> "**Just My Code**" by unchecking the box.

   Again, this was advice found searching around in a github issue. If not
   done, the breakpoints do not work for me.

6. **Open the folder in VSCode/VSCodium**: This is the same folder set in step
   5. Again, *for me*:

   ``/home/steve/.config/blender/4.2bonsai``

   This was a key point for me. Do `not` go deeper in the folder structure -
   that just doesn't work. (Thanks @theoryshaw) This feels a little like
   using a sledgehammer to crack a nut, and there might be a better, "proper"
   way of setting this up. If there is I'd love to hear it.

7. **Start Blender**: In VSCode/VSCodium press ``Ctrl+Shift+P``, and
   search/select **Blender: Start**.

8. **Set the Blender binary path**: The first time you try to start Blender the
   addon will ask for the path of the binary. Navigate to your Blender binary
   and select it. *For me*:

   ``/home/steve/Software/blender-git/build_linux/bin/blender``

   .. warning::
      Do `not` try to use a binary installed using snap - it will `not` work.
      Either install a debian package of Blender, or build it from source, and
      use that.

   All being well, Blender should start and show the usual Bonsai UI.

9. **Ensure Blender is behaving**: Exercise the interface a bit to be sure
   Bonsai is working normally. Add a demo project, add some walls, etc.

   One issue I ran in to was opening the wrong folder in step 7. Due to the
   way VSCode/VSCodium works, I was getting two Bonsai plugins conflicting,
   and failing in interesting ways. One symptom of this was the modal user
   interface when adding walls was completely missing. Oh, and the debugger
   completely failed to work.

   If you are happy, quit Blender, and try setting some breakpoints in
   VSCode/VSCodium then run Blender again, and try to trigger them. I set one
   on the ``bim.add_sheet`` operator at:
   ``extensions/.local/lib/python3.11/site-packages/bonsai/bim/module/drawing/operator.py:1456``

   .. note::
      I made the mistake of setting the breakpoint on the ``_execute``
      methods ``def`` line, which did not work. This probably helped confuse
      me when trying to get the addon to work.

If you get to this point, congratulations! You will now be 1000% more effective
when troubleshooting issues, and able to make many more contributions, fixes
and patches.

Blender Addon + VS Code Debugger
------------------------------

Setting up debugging with Blender Addon is a bit simpler as it doesn't require Blender to be started in a special way
and debugger can be always attached later when it's needed.

1. Install Hextant Python Debugger Blender addon from `official repository <https://github.com/hextantstudios/hextant_python_debugger#installation>`_.

2. Open IfcOpenShell repository in VS Code and setup configuration for attaching debugger `per the instructions <https://github.com/hextantstudios/hextant_python_debugger#debug-a-blender-add-on-from-visual-studio-code>`_.

3. Start Debug Server in Blender (Blender -> System -> Start Debug Server)

4. VS Code -> Run and Debug -> "Python Debugger: Remote Attach" in dropdown -> Start Debugging

5. Now debugger is attached to Blender. You can set breakpoints in VS Code and use Debug Console.
