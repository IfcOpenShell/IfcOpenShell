Debugging Bonsai
================

This is a mini-guide to setting up an IDE and configuring it to debug Bonsai more
easily. It is currently specific to this writers own system (Ubuntu) but this
can be expanded by others.

1. **Install VSCodium**: This will be system specific. I used the available
   snap package.

   .. code-block:: bash

     sudo snap install --classic codium

   I chose VSCodium to avoid Microsoft telemetry and data harvesting, but
   VSCode is going to be similar, and even a bit easier (i.e. steps 3 & 4).

2. **Activate Python language support**: Start VSCodium, open the Extensions, find the Python
   language support and activate it.

3. **Install Blender Addon**: It seems VSCodium is not allowed to directly access
   the Marketplace, and this addon (and the next) is not available in
   VSCodium's equivalent. (Or I'm an idiot... entirely possible). This means a
   few more steps are needed.

   Download the Blender addon's ``.vsix`` file from marketplace (Under "Resources")
   using your browser from `this <https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development>`_
   page.

   Install it with "**...**" -> "**Install from VSIX...**"

4. **Install ms-vscode.cpptools**: When trying to use the Blender addon I got
   an error about a missing dependancy. I read somewhere that this addon was
   not needed, but I can't currently find the reference. At least for me, it
   needs to be added the same way as step 3, or the Blender addon fails to
   start.

   Download the Cpp Tools addon's ``.vsix`` file from marketplace (Under "Resources")
   using your browser from `this <https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools>`_
   page. You will need to select the correct download for your system OS and
   architecture.

   Install it with "**...**" -> "**Install from VSIX...**"

5. **Set the Blender config directory**: In **Settings** -> **Extensions** -> **Blender** -> "**Environment Variables**"
   edit the json file to set the ``BLENDER_USER_RESOURCE`` to the config folder
   you installed Bonsai to. For me:

   .. code-block:: json

        {
            "blender.environmentVariables": {
                "BLENDER_USER_RESOURCES": "/home/steve/.config/blender/4.2bonsai"
            }
        }

   .. note::
    You `must` change that path to the correct value for your system.

6. **Unset the Just My Code flag**:  In **Settings** -> **Extensions** -> **Blender** -> "**Just My Code**"
   by unchecking the box.

   Again, this was advice found searching around in a github issue. If not
   done, the breakpoints do not work for me.

7. **Open the folder in VSCodium**: This is the same folder set in step 5.

   ``/home/steve/.config/blender/4.2bonsai``

   This was a key point for me. Do `not` go deeper in the folder structure -
   that just doesn't work. (Thanks @theoryshaw)

8. **Start Blender**: In VSCodium press ``Ctrl+Shift+P``, and search/select
   **Blender: Start**.

9. **Set the Blender binary path**: The first time you try to start Blender the
   addon will ask for the path of the binary. Navigate to your Blender binary
   and select it. For me:

   ``/home/steve/Software/blender-git/build_linux/bin/blender``

   .. warning::
    Do `not` try to use a binary installed using snap - it will `not` work.
    Either install a debian package of Blender, or build it from source, and
    use that.

   All being well, Blender should start and show the usual Bonsai UI.

10. **Ensure Blender is behaving**: Exercise the interface a bit to be sure
    Bonsai is working normally. Add a demo project, add some walls, etc.

    One issue I ran in to was opening the wrong folder in step 7. Due to the
    way VSCodium works, I was getting two Bonsai plugins conflicting, and
    failing in interesting ways. One symptom of this was the modal user
    interface when adding walls was completely missing. Oh, and the debugger
    completely failed to work.

    If you are happy, quit Blender, and try setting some breakpoints in
    VSCodium then run Blender again, and try to trigger them. I set one on
    the ``bim.add_sheet`` operator at:
    ``extensions/.local/lib/python3.11/site-packages/bonsai/bim/module/drawing/operator.py:1456``

    .. note::
        I made the mistake of setting the breakpoint on the ``_execute``
        methods ``def`` line, which did not work. This probably helped confuse
        me when trying to get the addon to work.

If you get to this point, congratulations! You will now be 1000% more effective
when troubleshooting issues, and able to make many more contributions, fixes
and patches.