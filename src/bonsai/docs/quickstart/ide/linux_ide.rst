Linux
================


This quickstart will help you set up your Linux machine to explore the sourcecode of Bonsai. 

You will be able to update or contribute to the official documentation and also 
explore the code behind Bonsai's functionalities to troubleshoot or propose new 
features.

We will be using AlmaLinux 9 as our operating system and Visual Studio Code as our 
Integrated Development Environment (IDE) and we will create a dedicated user for Development.



1. **Create Development User**: Open up a terminal (typically hitting "Windows" key
   and writting "terminal" in the search field)
   
   .. image:: images/launch-terminal.png
      :width: 200 px
      
   .. code-block:: bash

      sudo useradd falken10vdl
      sudo passwd falken10vdl
      sudo usermod -aG wheel falken10vdl

   .. image:: images/create-user.png
      :width: 500 px

   .. tip::

      If for some reason you need to delete the user, you can use the following command:

      .. code-block:: bash

         sudo userdel -r falken10vdl 

2. **Install Blender for the created user**: We will install blender locally in the users home directory.
   We must check that we are following the `Systems requirements <https://docs.bonsaibim.org/guides/development/installation.html/>`__.

   We will download Blender 4.2 from the `Blender download page <https://www.blender.org/download/>`__.
   In particular, we take the `4.2 LTS <https://www.blender.org/download/lts/4-2/>`__ for Linux.
   
   We will download the Linux 64 bit version: 
   
   https://www.blender.org/download/release/Blender4.2/blender-4.2.8-linux-x64.tar.xz

   .. code-block:: bash

      wget https://download.blender.org/release/Blender4.2/blender-4.2.8-linux-x64.tar.xz
      tar -xvf blender-4.2.8-linux-x64.tar.xz
      mv blender-4.2.8-linux-x64 /home/falken10vdl/.local/share/applications/blender-4.2.8-linux-x64

   .. warning::
   
      If the directory */home/falken10vdl/.local/bin/* does not exist, we will create it.

      .. code-block:: bash

         mkdir -p /home/falken10vdl/.local/bin/

   We will create a symbolic link to the blender executable in the bin directory and we will also modify the blender.desktop file to open in a terminal and to have a custom icon.
   
   .. code-block:: bash

      ln -s /home/falken10vdl/.local/share/applications/blender-4.2.8-linux-x64/blender /home/falken10vdl/.local/bin/blender
      sed -i 's/^Terminal=.*/Terminal=true/' /home/falken10vdl/.local/share/applications/blender-4.2.8-linux-x64/blender.desktop
      sed -i 's|^Icon=.*|Icon=/home/falken10vdl/.local/share/applications/blender-4.2.8-linux-x64/blender.svg|' /home/falken10vdl/.local/share/applications/blender-4.2.8-linux-x64/blender.desktop

   .. image:: images/blender-installation-1.png
      :width: 1000 px

   .. image:: images/blender-installation-2.png
      :width: 1000 px

   Congratulations! You have now Blender installed in your machine. You can launch it by typing `blender` in the terminal.

   Now install the Bonsai Blender extension. Follow the `Unstable installation <https://docs.bonsaibim.org/guides/development/installation.html#unstable-installation>`__.

3. **Install VSCode**: Log in as the new created user (*falken10vdl* in this example) 
   and install `Visual Studio Code <https://code.visualstudio.com/docs/setup/linux>`__. 

   .. code-block:: bash

      sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
      echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\nautorefresh=1\ntype=rpm-md\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/vscode.repo > /dev/null
      dnf check-update
      sudo dnf install code # or code-insiders

   .. image:: images/install-vscode.png
      :width: 1000 px

4. **Adjust Python version in VSCode as in Blender**: This is a good practice step to 
   ensure that the Python version in VSCode matches the one in Blender.

   Check the Python version in Blender by going to :menuselection:`Scripting`. In the Python Console you can see the version number of the Python 
   interpreter

   .. image:: images/blender-python-version.png
      :width: 1000 px

   
   In our case it is version 3.11.7
   
   We will need to install the closest version in our Linux machine.
   
   We check in `Python Downloads <https://www.python.org/downloads/>`__.

   .. image:: images/python-downloads.png
      :width: 1000 px

   The closest version is 3.11.11. So we download the Gzipped source tarball and install it.

   We use the "altinstall" option to avoid overwriting the default Python version which could cause 
   conflicts with the default installed version of the linux operating system.

   .. code-block:: bash

      wget https://www.python.org/ftp/python/3.11.11/Python-3.11.11.tgz
      tar -xvf Python-3.11.11.tgz
      cd Python-3.11.11
      sudo dnf install gcc openssl-devel bzip2-devel libffi-devel
      ./configure --enable-optimizations
      nproc
      make -j 4 #adjust the value to the one provided by nproc
      sudo make altinstall


   .. image:: images/install-python-1.png
      :width: 1000 px

   .. image:: images/install-python-2.png
      :width: 1000 px

   .. image:: images/install-python-3.png
      :width: 1000 px

   .. image:: images/install-python-4.png
      :width: 1000 px

   .. image:: images/install-python-5.png
      :width: 1000 px

   After this, we have the 3.11 python version installed in our machine. It is reachable by typing
   `python3.11` in the terminal.

   .. code-block:: bash

         python3.11 -V
      
   .. image:: images/install-python-6.png
         :width: 1000 px

   Launch VSCode and go to the Extensions tab, search for Blender Development and install it.

   .. image:: images/VSCode-blender-extension.png
         :width: 1000 px
   
   This will also install some Python related extensions.

   Finally create a sample python file and check the Python interpreter version in the bottom left corner.

   :menuselection:`File --> New File... --> Python File`


   .. image:: images/VSCode-python-version.png
         :width: 1000 px

   Congratulations! You have now a Python version in VSCode similar to the one run by Blender.

5. **Install GitHub related VSCode extensions**: To facilitate the use of git commands and pulling
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


6. **Fork IfcOpenShell project from GitHub**: For this step you will need an account on GitHub. 
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

7. **Cloning bonsai to our development environment**: Launch VSCode
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

8. **Link the Bonsai addon to the local cloned repository**: We will now edit the following 
   script that establishes links from the unstable-installation to the cloned repository so we 
   can easily see the changes done in the cloned repository taken effect when we load blender 
   locally.

   .. container:: blockbutton

      `Download dev_environment.sh <https://docs.bonsaibim.org/quickstart/ide/dev_environment.sh>`__

   Edit the file to match the paths in your system. In our case we will edit the following lines:

   - REPO_PATH="$HOME/bonsaiDevel/IfcOpenShell"
   - BLENDER_PATH="$HOME/.config/blender/4.2"
   - PACKAGE_PATH="${BLENDER_PATH}/extensions/.local/lib/python3.11/site-packages"
   - BONSAI_PATH="${BLENDER_PATH}/extensions/raw_githubusercontent_com/bonsai"

   We execute the script in the terminal. Confirm the data and the script will create the necessary links.

   .. code-block:: bash

      ./dev_environment.sh
 
   .. image:: images/dev-environment-sh.png
      :width: 1000 px

   .. image:: images/dev-environment-sh-executed.png
      :width: 1000 px

   .. warning::
   
      If you receive an error like this:

      .. code-block:: bash

         cp: cannot stat '/home/falken10vdl/.config/blender/4.2/extensions/.local/lib/python3.11/site-packages/ifcopenshell/*_wrapper*': No such file or directory

      It means that you have not installed the Bonsai Blender extension. Please refer to tha 
      last part of point 2. above and follow the `Unstable installation <https://docs.bonsaibim.org/guides/development/installation.html#unstable-installation>`__.


9. **Adjustments to the VSCode Blender extensionst**: We will now make some adjustments to the VSCode Blender extension to ease the reload of the addon.
   Select the Extensions tool. Then  :menuselection:`Blender Development` and then select :menuselection:`Settings`.

   .. image:: images/VSCode-blender-extension-settings.png
      :width: 1000 px

   Click twice in "Add Item" within the *Blender: Additonal Arguments* section and add the following two items (adapt *Testing.ifc* to the name of the IFC file you want to test during Bonsai development):

   - --python-expr
   - import bpy; bpy.ops.bim.load_project(filepath="/home/falken10vdl/bonsaiDevel/Testing.ifc", should_start_fresh_session=True, use_detailed_tooltip=True)

   .. image:: images/VSCode-blender-additional-arguments.png
      :width: 1000 px

   Make sure that Blender > Addon: Just My code is not selected (This allows to set the breakpoints anywhere in the source code).

   .. image:: images/just-my-code-false.png
      :width: 1000 px


   .. warning::
   
      This way to use the VSCode Blender extension is not the standard one. Refer to the `VSCode Blender extension documentation <https://github.com/JacquesLucke/blender_vscode>`__ for the standard way to use it.
      The reasond behind is that this allows us to start VSCode in the top of the cloned repository so
      all the Git related funtionality in VSCode works properly and we have a complete view from VSCode 
      :menuselection:`Explorer` tool of the whole repository. 
      
      Bonsai is a big project with a lot of dependencies
      so reloading it it is not an easy task (see discussion in https://community.osarch.org/discussion/1650/vscode-and-jacquesluckes-blender-vscode/p1). We have taken the pragmatic approach to start blender with a specific file (*Testing.ifc*) 
      and then we can reload the addon from the Blender UI which also upload automatically the changes in the addon and the testing file
      To summarize:

      - We need *Blender > Addon: Just My code* to get the breakpoint functionality even if the addon is not "registered/loaded" to the extension (due to the root folder we use)
      - We need *Blender: Additonal Arguments* to automatically load the Testing.ifc file when we start Blender from VSCode (We do not use *Blender:Reload Addons* since it does not work in our case)

      Instead of restarting Blender from VSCode, we use the Blender UI that, as explainedin the next step, it provides a simple way to get the addon and the Testing file reloaded.

10. **Launch blender from VSCode**: We are now ready to launch Blender from VSCode. 
    Open VSCode. Open the cloned repository if not already open.
    Press CTRL-SHIFT-P and type "Blender: Start".

    .. image:: images/VSCode-blender-start.png
       :width: 1000 px
  
    Blender will start loading the Testing.ifc file. You can now start exploring the code and make changes to the addon!

    .. image:: images/VSCode-and-blender.png
       :width: 1000 px

    In order to be able to restart blender (and reload the addons + reload teh Testing file) we need to 
    enable "Developer Extras" and also a good practice is to enable "Python Tooltips" in :menuselection:`Edit --> Preferences --> Interface`.

    .. image:: images/enable-developer-extras.png
       :width: 1000 px

    Once these are enabled, you can press F3 and write restart to restart Blender.

    .. image:: images/restart-blender.png
       :width: 1000 px

11. **Adding a break-point**: Let's add a break-point in the code to see how it works.
    Press CTRL_SHIFT_P and type "Blender: Start". Blender will start.
    Open the cloned folder and go to  *src > bonsai > bonsai > bim > module > ligth > prop.py* and go to line 75.  
    Add a line for a print statemente and click on the left side of the line number to add a break-point.

    .. code-block:: python

      74   def update_shadow_mode(self, context):
      75      print("Shadow mode", self.shadow_mode)
      76      if self.shadow_mode == "SHADING":


    Set a break-point in line 75.

    .. image:: images/break-point.png
       :width: 1000 px

    In Blender. Go To SOLAR ANALYSYS Tool in Bonsai and Click in "No Shadow", "Shaded" or "Rendered"

    .. image:: images/trigger-breakpoint.png
       :width: 1000 px


    This will trigger the break-point. See how the execution is stopped at the break-point.

    .. image:: images/break-point-stop.png
       :width: 1000 px


    From here you can watch the local variables, global variables, add watches, check the stack, etc.
    Resume execution or move step by step to see how the code is executed.

    CONGRATULATIONS! You have now a development environment ready to explore the Bonsai code and contribute to the project.

12. **Making changes and doing Pull Request to the project**: In the previous steps we got a complete IDE to explore and make changes to the Bonsai sourcecode.
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

    Letis see below the steps with an example of changing the documentation of the Quickstart guide for the IDE in Linux.

    a. Check in our GitHub page if our project fork is outdated. Click *Update branch*

       .. image:: images/check-fork.png
          :width: 1000 px
 
    b. After clicking *Update brnach* our fork is up to date with the upstream main branch.

       .. image:: images/sync-fork.png
          :width: 1000 px

    c. Pull the changes in our porject fork to our local repository
    
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

    f. Make changes in the code. In this case we will change documentation by adding a Quickstart for the IDE in Linux. :)

       .. image:: images/make-changes.png
          :width: 1000 px

    g. Commit the changes.
    
       .. image:: images/commit-changes.png
          :width: 1000 px

    h. Push the changes to our project fork.
    
       .. image:: images/push-changes.png
          :width: 1000 px

    i. Create a Pull Request to the upstream main branch of the IfcOpenShell project.
    
       .. image:: images/create-pull-request.png
          :width: 1000 px


