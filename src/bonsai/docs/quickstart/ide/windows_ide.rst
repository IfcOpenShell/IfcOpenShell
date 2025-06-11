Windows
================

This quickstart will help you set up your MS Windows machine to explore the sourcecode of Bonsai 
or develop and debug your blender scripts in VSCode. This has the benefit of having a complete
development environment where you can explore the code, make changes, debug (break-points, watch 
variable and stack contents, etc. ) and see the results in blender

- Steps 1-6 will get you started with VSCode to develop and debug python scripts in Blender and explore the Bonsai sourcecode and documentation.

- Steps 7-14 will allow you to interact with GitHub to make changes to the Bonsai project.

- Step 15 will allow you to download someone else's pull request and test it in your local machine.

We will be using Windows 11 as our operating system and Visual Studio Code as our 
Integrated Development Environment (IDE) and we will create a dedicated user for Development.

.. note::
   In the following steps we will be installing a number of applications. There are several ways to install them and that has impact on whether Windows is able to find the relevant binaries. In general if you have issues in the steps below
   related to not being able to find binaries, please check that the installation path is in the PATH environment variable. You can hit "Windows" key and write "environment variables".
   
   .. image:: images/environment-variables.png
      :width: 500 px

   And then go to :menuselection:`System Properties --> Advanced -->Environment Variables`.
   
   Check that the installation path is in the PATH variable. If not, you can add it by clicking in the :menuselection:`Edit... --> New`.

   .. image:: images/windows-path.png
      :width: 500 px


1. **Create Development User**: Open Windows Settings (typically hitting "Windows" key
   and writing "settings" in the search field) and then go to :menuselection:`Accounts --> Other users`.
   Click on :menuselection:`Add account` and then add a new user. We will name it *falken10vdl*.
   

   .. image:: images/win-add-user.png
      :width: 500 px
      

2. **Install Blender for the created user**: We will install blender locally in the users home directory.
   We must check that we are following the `Systems requirements <https://docs.bonsaibim.org/guides/development/installation.html/>`__.

   We will download Blender 4.2 from the `Blender download page <https://www.blender.org/download/>`__.
   In particular, we take the `4.2 LTS <https://www.blender.org/download/lts/4-2/>`__ for Windows.
   
   We will download the Windows - Portable (.zip) version: 
   
   https://www.blender.org/download/release/Blender4.2/blender-4.2.8-windows-x64.zip

   Unzip the file in the user home directory. In our case it is *C:\\Users\\falke\\Documents\\blender-4.2.8-windows-x64* (the user *falken10vdl* has as home directory *C:\\Users\\falke*).

   CONGRATULATIONS! You have now Blender installed locally in your machine. You can launch it by double clicking in blender.exe which is situated in the previous folder.

   Now install the Bonsai Blender extension. Follow the `Unstable installation <https://docs.bonsaibim.org/guides/development/installation.html#unstable-installation>`__.

   CONGRATULATIONS! You have now the Bonsai Blender extension installed in your local Blender installation.


3. **Install VSCode**: Log in as the new created user (*falken10vdl* in this example) 
   and install `Visual Studio Code <https://code.visualstudio.com/docs/?dv=win64user>`__. 



4. **Adjust Python version in VSCode as in Blender**: This is a good practice step to 
   ensure that the Python version in VSCode matches the one in Blender.

   Check the Python version in Blender by going to :menuselection:`Scripting`. In the Python Console you can see the version number of the Python 
   interpreter

   .. image:: images/blender-python-version.png
      :width: 1000 px

   
   In our case it is version 3.11.7
   
   We will need to install the closest version in our Linux machine.
   
   We check in either in Microsoft store or `Python Downloads <https://www.python.org/downloads/windows/>`__.

   The closest version is 3.11 in Microsoft Store. So we installing by clicking in :menuselection:`Get`.

   After this, we have the 3.11 python version installed in our machine. It is reachable by typing
   `python3.11` in the terminal.

   .. code-block:: bash

         python3.11 -V
      
   .. image:: images/python-version.png
         :width: 500 px

   Finally create a sample python file and check the Python interpreter version in the bottom left corner. Select the
   Python interpreter that matches the one in Blender. In our case it is 3.11.

   :menuselection:`File --> New File... --> Python File`


   .. image:: images/VSCode-python-version-windows.png
         :width: 1000 px

   CONGRATULATIONS! You have now a Python version in VSCode similar to the one run by Blender.

5. **Connect VSCode to Blender by means of VSCode's extension: "Blender Development"**: This steps
   is crucial to be able to develop and debug scripts in VSCode and interactively see the results in Blender.
      
   Launch VSCode and go to the Extensions tab, search for Blender Development and install it.

   .. image:: images/VSCode-blender-extension.png
         :width: 1000 px
   
   This will also install some Python related extensions.

6. **Test that you can develop python scripts in VSCode for Belnder**: Create a sample blender python file under adirectory
   for example *C:\\Users\\falke\\Documents\\bonsaiDevel\\scripts*. You can use whatever blender python script you want. 
   We will use this one from the blender documentation:
   
   `Example Panel <https://docs.blender.org/api/current/info_quickstart.html#example-panel>`__
  
   .. code-block:: python

      import bpy

      class HelloWorldPanel(bpy.types.Panel):
         """Creates a Panel in the Object properties window"""
         bl_label = "Hello World Panel"
         bl_idname = "OBJECT_PT_hello"
         bl_space_type = 'PROPERTIES'
         bl_region_type = 'WINDOW'
         bl_context = "object"

         def draw(self, context):
            layout = self.layout

            obj = context.object

            row = layout.row()
            row.label(text="Hello world!", icon='WORLD_DATA')

            row = layout.row()
            row.label(text="Active object is: " + obj.name)
            row = layout.row()
            row.prop(obj, "name")

            row = layout.row()
            row.operator("mesh.primitive_cube_add")


      def register():
         bpy.utils.register_class(HelloWorldPanel)


      def unregister():
         bpy.utils.unregister_class(HelloWorldPanel)


      if __name__ == "__main__":
         print("Hello World: run from Blender Text Editor")
      else:
         print("Hello World: run from VSCode")
         print(f"NOTE. __name__ is : {__name__}")

      register()


   .. tip::

      Although blender has builtin the python modules for bpy, it is a good practice to install the "fake-bpy-module" in your local python environment. 
      This will allow VSCode to provide autocompletion and other features. You can install it by running the following command in the VSCode terminal:

      .. code-block::
            
            python3.11 -m pip install fake-bpy-module-latest


      .. image:: images/install-bpy-fake-windows.png
         :width: 1000 px
   

   We have changed the last part of the script since running from VSCode has some subtle differences compared to running from the Blender Text Editor. In particular the special variable `__name__` is different.

   - Press CTRL-SHIFT-P and type "Blender: Open Scripts Folder". Select the previous folder where the script file is located
   - Press CTRL-SHIFT-P and type "Blender: Start". Blender will start.
   - Press CTRL-SHIFT-P and type "Blender: Run Script". The script will run and the output will be seen in Blender!
   
   As you can see below. We have set a break-point in line 37 (see point 13 below for another example of setting a break-point). We can inspect in the left side the local variables, global variables, add watches, 
   check the stack, etc. For example we can see that __name__ has a value of "<run_path>" Instead of "__main__".

   .. image:: images/script-blender-vscode.png
      :width: 1000 px

   
   Once we continue execution we can check in the VSCode Terminal the output and in Blender the panel created by the script.

   .. image:: images/script-blender-vscode-2.png
         :width: 1000 px


   CONGRATULATIONS! You have now a development environment ready to speedup your python scripting in Blender.


X. **BONUS: Editing Bonsai Documentation**: Please refer to `Writing documentation <https://docs.bonsaibim.org/guides/development/writing_docs.html/>`__ for details on how to edit and contribute documentation.
   Here we just summarize the steps to integrate that workflow in VSCode and using Inkscape.

   - Download and install Inkscape from `Inkscape download page <https://inkscape.org/release>`__. In our case we will use `Inkscape 1.4 Windows 64 bit msi installer <https://inkscape.org/release/inkscape-1.4/windows/64-bit/msi/dl/>`__.  

   - The file below has the style annotation for the Bonsai documentation.

   .. container:: blockbutton

      `Download style annotation file <https://docs.bonsaibim.org/quickstart/ide/bonsai_style_annotation.svg>`__

   It contains some shapes and styles that you can use to create your own diagrams.

   .. image:: images/inkscape-annotation-template.png
         :width: 1000 px

   - Open some screenshot file you want to add annotations in Inkscape and also open this template. You can then copy paste from the template to the screenshot file.

   .. warning::
      When copying the shapes for your convenience just make sure that you do not have selected the option "When scaling objects, scale the stroke width by the same proportion" 
      to keep the style width right as per Bonsai documentation style guidelines
   
      .. image:: images/inkscape-scaling-outline.png
         :width: 1000 px

   - Once done you can export your edited screenshot as PNG to be used in the docummentation. :menuselection:`File --> Export...` and click in the Export button on bottom right corner.
   - As described in `Writing documentation <https://docs.bonsaibim.org/guides/development/writing_docs.html/>`__ you need to have sphinx installed in your system. One of the easiest ways is to use `Chocolately <https://chocolatey.org/install>`__. 
      Install Chocolately and then you can simply run the following command in the terminal:

      .. code-block::

         choco install sphinx

      and then install the theme and theme dependencies:

      .. code-block::

         python3.11 -m pip install furo
         python3.11 -m pip install sphinx-autoapi
         python3.11 -m pip install sphinx-copybutton

      All these can be accomplished within a terminal of VSCode.

      .. image:: images/doc-pip-furo.png
            :width: 1000 px


   - To speedup your workflow you can add the following VSCode files in the .vscode folder of your cloned repository. In our case it is *C:\\Users\\falke\\Documents\\bonsaiDevel\\IfcOpenShell\\.vscode*
   - Make sure to edit them with the right paths in your system.

      - `launch.json <https://docs.bonsaibim.org/quickstart/ide/windows/launch.json>`__

         .. image:: images/launch-windows-jason.png
               :width: 1000 px

      - `tasks.json <https://docs.bonsaibim.org/quickstart/ide/windows/tasks.json>`__
      
         .. image:: images/tasks-windows-jason.png
               :width: 1000 px

   - Now you can use the debug tool in VSCode to regenerate the html documentation by cliking the "Play" button *BonsaiDocsServer (IfcOpenShell)* in the top left corner of the debug tool.

      .. image:: images/bonsai-doc-server.png
            :width: 1000 px

   - Once the server is started you can open a browser and go to the following URL:
      http://localhost:8000/ and you will see the documentation.

   - In order to rebuild the documentation you need to stop the server and run the command again. You can do this by clicking in the "Abort" button in the bottom right corner of the debug tool.

      .. image:: images/doc-server-running.png
            :width: 1000 px

   CONGRATULATIONS! And happy documenting!
            


Now let's find out how to interact with GitHub in order to make changes to the Bonsai project.


7. **Install GitHub related VSCode extensions**: To facilitate the use of git commands and pulling
   and pushing files from a local repository towards github, please install as well the following VSCode
   extensions:

   - GitHub Pull Requests
   - GitHub Repositories
   - Remote Repositories
   
   Optionaly you can also install Copilot extensions
   
   - GitHub Copilot
   - GitHub Copilot Chat

   .. image:: images/VSCode-extensions.png
         :width: 500 px


8. **Fork IfcOpenShell project from GitHub**: For this step you will need an account on GitHub. 
   Once you have a registered account you can find it under https://github.com/YOURGITHUBUSERID
   In the example for *falken10vdl* the link is https://github.com/falken10vdl

   .. image:: images/GitHubUser.png
      :width: 1000 px

   Go to the `IfcOpenShell GitHub page <https://github.com/IfcOpenShell/IfcOpenShell/>`__. And 
   click on the Fork button. Please make sure that you are logged with your GitHub account as shown in the 
   top right corner of the page.

   .. image:: images/fork-bonsai.png
      :width: 1000 px

   Once the fork is generated you will be redirected to your own fork of the IfcOpenShell project.

   .. image:: images/forked-bonsai.png
      :width: 1000 px

   Now we will clone the forked repository to our local machine. 

9. **Clone bonsai to our development environment**: Launch VSCode
   Select the Source Control tool. Then  :menuselection:`Clone repository` and then select "Clone from GitHub".
   
   .. image:: images/cloning-from-github.png
      :width: 1000 px

   A series of steps will be required to authenticate with GitHub. You will need to provide your GitHub credentials.
   Once VSCode has authenticated yourself in GitHub, you will be able to select the repository you want to clone. 
   In this case we will clone the IfcOpenShell repository.

   .. image:: images/selecting-forked-repo.png
      :width: 1000 px

   VSCode will ask you to select a folder where the repository will be cloned. and it will start the cloning process.

   Once finished, you will see the repository in the Explorer tool.

   .. image:: images/cloned-repo.png
      :width: 1000 px

10. **Link the Bonsai addon to the local cloned repository**: We will now edit the following 
    script that establishes links from the unstable-installation to the cloned repository so we 
    can easily see the changes done in the cloned repository taken effect when we load blender 
    locally.

    .. container:: blockbutton

       `Download dev_environment.bat <https://docs.bonsaibim.org/quickstart/ide/windows/dev_environment.bat>`__

    Edit the file to match the paths in your system. In our case we will edit the following lines:

    - SET REPO_PATH=%HOMEDRIVE%\\Users\\%USERNAME%\\Documents\\bonsaiDevel\\IfcOpenShell
    - SET BLENDER_PATH=%HOMEDRIVE%\\Users\\%USERNAME%\\AppData\\Roaming\\Blender Foundation\\Blender\\4.2
    - SET PACKAGE_PATH=%BLENDER_PATH%\\extensions\\.local\\lib\\python3.11\\site-packages
    - SET BONSAI_PATH=%BLENDER_PATH%\\extensions\\raw_githubusercontent_com\\bonsai

    You need to run it as an administrator.

    .. image:: images/run-as-administrator.png
       :width: 1000 px
    
    Confirm the data and the script will create the necessary links.

    .. image:: images/running-dev_environment-bat.png
       :width: 1000 px


    .. warning::
   
       If you receive errors like this:

       .. code-block:: bash

          The system cannot find the path specified.

       It means that you have not installed the Bonsai Blender extension. Please refer to tha 
       last part of point 2. above and follow the `Unstable installation <https://docs.bonsaibim.org/guides/development/installation.html#unstable-installation>`__.


11. **Adjust the VSCode Blender extension**: We will now make some adjustments to the VSCode Blender extension to ease the reload of the addon.
    Select the Extensions tool. Then  :menuselection:`Blender Development` and then select :menuselection:`Settings`.

    .. image:: images/VSCode-blender-extension-settings.png
       :width: 1000 px

    Click twice in "Add Item" within the *Blender: Additonal Arguments* section and add the following two items (adapt *Testing.ifc* to the name of the IFC file you want to 
    test during Bonsai development):

    - --python-expr
    - import bpy; import os; os.chdir("C:\\\\Users\\\\falke\\\\Documents\\\\blender-4.2.8-windows-x64"); bpy.ops.bim.load_project(filepath="C:\\\\Users\\\\falke\\\\Documents\\\\bonsaiDevel\\\\Testing.ifc", should_start_fresh_session=True, use_detailed_tooltip=True)

    .. image:: images/VSCode-blender-additional-arguments-windows.png
       :width: 1000 px

    .. Note::
   
      You can use double backslash (\\\\) and double quotes (") in the path for correct interpretation by VSCode or you can use single forward slash
      (/) and single quotes (') as well. In this case the path will be: 'C:/Users/falke/Documents/bonsaiDevel/Testing.ifc'

      .. image:: images/VSCode-blender-additional-arguments-2-windows.png
         :width: 1000 px


    Make sure that Blender > Addon: Just My code is not selected (This allows to set the breakpoints anywhere in the source code).

    .. image:: images/just-my-code-false.png
       :width: 1000 px


    .. warning::
   
       This way to use the VSCode Blender extension is not the standard one. Refer to the `VSCode Blender extension documentation <https://github.com/JacquesLucke/blender_vscode>`__ for the standard way to use it.
       The reason behind is that this allows us to start VSCode in the top of the cloned repository so
       all the Git related funtionality in VSCode works properly and we have a complete view from VSCode 
       :menuselection:`Explorer` tool of the whole repository. 
      
       Bonsai is a big project with a lot of dependencies
       so reloading it is not an easy task (see discussion in https://community.osarch.org/discussion/1650/vscode-and-jacquesluckes-blender-vscode/p1). We have taken the pragmatic approach to start blender with a specific file (*Testing.ifc*) 
       and then we can reload the addon from the Blender UI which also uploads automatically the changes in the addon and the testing file
       
       To summarize:

       - We need *Blender > Addon: Just My code* to get the breakpoint functionality even if the addon is not "registered/loaded" to the extension (due to the root folder we use)
       - We need *Blender: Additonal Arguments* to automatically load the Testing.ifc file when we start Blender from VSCode (We do not use *Blender:Reload Addons* since it does not work in our case)

       Instead of restarting Blender from VSCode, we use the Blender UI that, as explainedin the next step, it provides a simple way to get the addon and the Testing file reloaded.

12. **Launch blender from VSCode**: We are now ready to launch Blender from VSCode. 
    Open VSCode. Open the cloned repository if not already open.
    Press CTRL-SHIFT-P and type "Blender: Start".

    .. image:: images/VSCode-blender-start.png
       :width: 1000 px
  
    Blender will start loading the Testing.ifc file. You can now start exploring the code and make changes to the addon!

    .. image:: images/VSCode-and-blender.png
       :width: 1000 px

    In order to be able to restart blender (and reload the addons + reload the Testing file) we need to 
    enable "Developer Extras" and also a good practice is to enable "Python Tooltips" in :menuselection:`Edit --> Preferences --> Interface`.

    .. image:: images/enable-developer-extras.png
       :width: 500 px

    Once these are enabled, you can press F3 and write "restart" to restart Blender.

    .. image:: images/restart-blender.png
       :width: 1000 px


    .. warning::
       The Windows conpty Dll will force the terminal to be detached once Blender is restarted and you will lose the console output. 
       In order to avoid that, you can enable the following settings in VSCode:

       Go to :menuselection:`File --> Preferences --> Settings` and search for "terminal.integrated.windows". Enable both *terminal.integrated.windowsEnableConpty* 
       and *terminal.integrated.windowsUseConptyDll*.

       .. image:: images/terminal-integrated-windows.png
          :width: 1000 px

       - *terminal.integrated.windowsEnableConpty* makes it possible to restart blender from Bonsai restart_blender command.

       - *terminal.integrated.windowsUseConptyDll* makes it possible to maintain the console attached so the output of the reloaded blender instance is still visible in the terminal.
      
    .. note::

       Once you enable "Developer Extras" you will see that you can right click in the UI and select "Source Code" to see the code behind the UI. For example in the image below you can
       right click in the "Generate SVG" and select "Edit Source".

         .. image:: images/edit_source.png
            :width: 1000 px
      
       Then in the "Scripting" tab you can click and select a new editor windows that has been created (in this case it is called "uy.py").

       .. image:: images/scripting_ui_code.png
          :width: 500 px
   
       If you select it, you will see the relevant code with a vertical blue line marking the exact point in the source code where the UI element is defined.
      
       .. image:: images/marked_code.png
          :width: 1000 px

       From there it is quite usefull to search in VSCode to find the relevant file within the Bonsai source code. For that you can go to :menuselection:`Edit --> Find in Files`.

       .. image:: images/vscode_search_in_files.png
          :width: 350 px

       Then you can click in the results to get the file opened in the editor.
      
       .. image:: images/vscode_search_results.png
          :width: 1000 px


    .. tip::

       Once you enable "developer Extras" you will be able to select in :menuselection:`Edit --> Preferences --> Experimental --> Debugging` a number of options related to code development.

       .. image:: images/blender_experimental_debugging.png
          :width: 500 px
       
       In the case case of Bonsai. You have the TAB :menuselection:`Quality & Coordination --> Debug --> Experimental --> Debugging` that also provides a number of tools to ease the development process.

       .. image:: images/bonsai_debug.png
          :width: 500 px
       
       Finally, there are a number of usefull Blender addons that can also help you in the development process. For example "Icon Viewer" or "Math vis".

       .. image:: images/blender_development_addons.png
          :width: 500 px


13. **Add a break-point**: Let's add a break-point in the code to see how it works.
    Press CTRL-SHIFT-P and type "Blender: Start". Blender will start.
    Open the cloned folder and go to  *src > bonsai > bonsai > bim > module > light > prop.py* and go to line 75.  
    Add a line for a print statement and click on the left side of the line number to add a break-point.

    .. code-block:: python

      74   def update_shadow_mode(self, context):
      75      print("Shadow mode", self.shadow_mode)
      76      if self.shadow_mode == "SHADING":


    Set a break-point in line 75.

    .. image:: images/break-point.png
       :width: 1000 px

    In Blender. Go To SOLAR ANALYSIS Tool in Bonsai and Click in "No Shadow", "Shaded" or "Rendered"

    .. image:: images/trigger-breakpoint.png
       :width: 1000 px


    This will trigger the break-point. See how the execution is stopped at the break-point.

    .. image:: images/break-point-stop.png
       :width: 1000 px


    Click in the debugging tools the option for "step over" (F10).

    .. image:: images/step-over.png
       :width: 1000 px

    You can see the print statement executed and the output in the VSCode internal terminal.

    .. image:: images/print-to-console.png
       :width: 1000 px


    From here you can watch the local variables, global variables, add watches, check the stack, etc.
    Resume execution or move step by step to see how the code is executed.

    CONGRATULATIONS! You have now a development environment ready to explore the Bonsai code and contribute to the project.

14. **Make changes and do a Pull Request to the project**: In the previous steps we got a complete IDE to explore and make changes to the Bonsai sourcecode.
    In this step we will provide a simple workflow of using Git commands within VSCode to make changes and do a Pull Request to the project.
    Bonsai changes very fast so our cloned repository will be outdated very soon. We propose to do the following:

    a. Check in our GitHub page if our project fork (https://github.com/falken10vdl/IfcOpenShell) is outdated compared to the IfcOpenShell main branch (https://github.com/IfcOpenShell/IfcOpenShell).
    b. Sync our fork with the upstream branch (if needed).
    c. Pull the changes in our porject fork to our local repository (/home/falken10vdl/bonsaiDevel).
    d. Create a new branch in our local repository (example: *DOC_QS_IDE*)
    e. Publish the branch to our project fork in GitHub. 
    f. Make changes in the code.
    g. Commit the changes.
    h. Push the changes to our project fork.
    i. Create a Pull Request to the upstream main branch of the IfcOpenShell project.

    Let's see below the steps with an example of changing the documentation of the Quickstart guide for the IDE in Windows.

    a. Check in our GitHub page if our project fork is outdated. Click *Update branch*

       .. image:: images/check-fork.png
          :width: 1000 px
 
    b. After clicking *Update branch* our fork is up to date with the upstream main branch.

       .. image:: images/sync-fork.png
          :width: 1000 px

    c. Pull the changes in our project fork to our local repository
    
       .. image:: images/pull-changes.png
          :width: 1000 px
   
    d. Create a new branch in our local repository by clicking in the current branch name in the bottom left corner of the VSCode window. Give a name to the branch and press Enter.

       .. image:: images/create-branch.png
          :width: 1000 px

       The new branch is created and we can see it in the bottom left corner of the VSCode window.

       .. image:: images/new-branch-local.png
          :width: 1000 px

    e. Publish the branch to our project fork in GitHub by clicking in the publish button (*little cloud with up arrow*) in the bottom 
       left corner of the VSCode window. Select as origin the project fork.

       .. image:: images/new-branch-publish-to-private-github.png
          :width: 1000 px

       Check that the branch is now in our project fork in GitHub.

       .. image:: images/new-branch-in-private-github.png
          :width: 1000 px

    f. Make changes in the code. In this case we will change documentation by adding a Quickstart for the IDE in Windows. :)

       .. image:: images/make-changes-windows.png
          :width: 1000 px

    g. Commit the changes.
       
       First provide your user name and email to Git (this is required only once).

       .. image:: images/git-user-email-windows.png
          :width: 1000 px

       Then commit the changes by clicking in the check mark in the Source Control tool.

       .. image:: images/commit-changes-windows.png
          :width: 1000 px

       Accept the staging of the changes prior to commit.

       .. image:: images/staging-prior-commit.png
          :width: 350 px

    h. Push the changes to our new branch in the github project fork.
    
       .. image:: images/push-to-private-fork-new-branch.png
          :width: 1000 px

       Check that the changes are in the project fork in GitHub. You can see that the directory *ide* has been added, for example.

       .. image:: images/private-fork-new-branch-updated-windows.png
          :width: 1000 px


    i. Create a Pull Request to the upstream main branch of the IfcOpenShell project.
       Go to your GitHub page and you will see that the new branch has 1 commit ahead of the upstream main branch. Click in the *Compare & pull request* button.

       .. image:: images/compare-and-pull-request.png
          :width: 1000 px

       Verify that the changes are correct, add a description and click in the *Create pull request* button.

       .. image:: images/pull-request-windows.png
          :width: 1000 px

       .. note::

          If you need to update the Pull Request with new changes, you can do it by making the changes in the local repository and then commit and push them to the same branch. 
          The Pull Request will be updated automatically. You can also add comments to the Pull Request to explain the changes made.

       .. warning::

          Sometimes the process of changing the initial code for the Pull Request takes enough time that already the upstream main branch has changed significately. This means that a direct merge to the upstream branch
          is not possible without conflicts. In this case you will need to rebase the Pull Request branch with the upstream main branch.This takes all your commits from the current PR branch and reapplies them one by one on top of the latest commits 
          in the target branch (which should be the upstream main branch). This is a bit more complex process and you can refer to the `Using Git source control in VS Code <https://code.visualstudio.com/docs/sourcecontrol/overview>`__ for more information.

          .. image:: images/rebase_branch.png
             :width: 1000 px


    CONGRATULATIONS! You have now made a change in the Bonsai project and created a Pull Request to the main branch of the project. Happy coding and documenting!

15. **Test someone else's Pull Request**: Ofen times you want to provide feedback to someone else's Pull Request. 
    A simple way to do this is by using the GitHub Pull Request extension in VSCode. Please refer to `GitHub Pull Requests in Visual Studio Code <https://code.visualstudio.com/blogs/2018/09/10/introducing-github-pullrequests>`__  for more information.

    .. image:: images/checkout_pull_request_vscode.png
       :width: 1000 px

    This will fetch the branch of the Pull Request and you will be able to test it as if you had created your own branch.

    .. image:: images/pull_request_see.png
       :width: 1000 px
    
    You can also use the GitHub Pull Request extension to review the Pull Request and provide comments. And of course the rest of the VSCode functionality to test, debug, improve, etc. the code.

    CONGRATULATIONS! and happy testing!