Tracking revisions with Git
===========================

BlenderBIM supports tracking the development of your IFC files with a Git
repository.

BlenderBIM is an IFC file editor, you can create or load an IFC project,
change, add or remove BIM objects and save to disk. A Git repository is a
special folder on your computer where text files, such as IFC files, can be
efficiently stored and past versions recalled.

Git is also a tool to share files with other people, transmitting only file
changes, and allowing multiple people to keep local copies of the same
repository up-to-date.

.. Note::

    If you don't already have Git installed on your system, you will need to
    `Download from the Git website <https://git-scm.com/downloads>`__.
    You may have to restart Blender after installation.

Adding your IFC file to a repository
------------------------------------

First, save your file to disk. If the folder is already a repository you can
*Add* the file in the *IFC Git panel* to tell Git you want to track it,
otherwise BlenderBIM will offer to convert the folder into a repository.

.. Warning::

    You probably don't want to turn your entire HOME or User folder into a Git
    repository. Create one folder per project, this folder can contain multiple
    IFC files, optionally in subfolders, plus any resources needed to support
    them.

After adding an IFC file, this action will appear as the most recent item at
the top of the revision list.

'Committing' changes
--------------------

As you work on your IFC project, save the file regularly as usual. When you
get to a point where it would be useful to later retrieve this state, you need
to *commit* this to the Git repository. BlenderBIM gives you three options:

- Showing uncommitted changes will temporarily highlight the differences
between the saved file and the last committed revision. Green objects are new
and blue objects exist in the previous revision but have since been modified.

- Discarding uncommitted changes will throw away all your saved changes and
revert the model to the previous revision.

- Committing changes will save this state of the model in the repository, along
with a short commit message, the date, and your author details.

.. Tip::

    All revisions need to have some sort of commit message. Typically this
    should be kept to 50 characters or less, but there is no practical limit,
    consider that this message may appear in various places, including on
    drawings, web pages, email subject lines etc.. It is also best to describe the
    status of the revision rather than the changes, ie. "Kitchen now has a
    door" is better than "Add a kitchen door" - but this is a matter of taste.

Visualising differences
-----------------------

As you add commits, the revision list will build up. Usually you are working at
the HEAD of a branch, ie. at the top of the list, but you can select items in
the list to view commit metadata. You can also temporarily colourise the current
model showing differences between this and any other saved revision - colours
are the same as above: green objects are new to the current model, blue
objects have changed in some way, and (if you have an older revision loaded)
red objects have been deleted.

Retrieving Revisions
--------------------

Colourising the model will show you *which* things are different, but it won't
show you *how* they are different. As long as you have no uncommitted changes,
you can switch to the selected revision, this will load in BlenderBIM as a
full model that can be viewed and even edited.

.. Warning::

    Switching to a different revision actually changes the file on disk before
    loading it in BlenderBIM. Don't worry, the original hasn't been lost,
    simply select the revision at the top of the list, switch back to
    that and you can continue as before.

Branching
---------

Git supports a branched workflow. Say that you want to explore some design
options, but don't want to mess-up the primary design, you can fork off any
revision into a new branch and work on this without breaking anything in any
other branches.

.. Note::

    The primary branch in a Git repository is usually called *main*, though
    this is a convention, and older versions of Git call it *master*. Branch
    names should be short, but can contain unicode characters, emojis etc...
    Branch names can't contain spaces, and have some other minor limitations -
    BlenderBIM will not allow you to create invalid branch names.

To create a branch simply switch to any earlier revision, ie. not the current
HEAD at the top of the revision list, and start editing the project.  When you
save and commit, BlenderBIM will insist that you either discard your changes
or it will force you to create a new branch.

Each branch can now be navigated separately in the revision list, to switch
between branches, and to any previous revision in any branch, select the
revision you are interested-in and switch as before.

.. Tip::

    Conceptually a local branch is equivalent to a remote fork in somebody
    else's copy of your repository, and indeed with an external Git tool you
    can import their work into a branch in your local repository.

Merging
-------

.. Warning::

    Merging is experimental functionality. There are various circumstances
    where a merge will fail, don't worry, this won't break your model but you
    may not want to rely on this functionality without having some experience
    of what changes are likely to merge and what won't.

You can merge changes that exist in a selected revision into the current
model, even if changes have been made in both revisions - as long as these
changes don't directly conflict. After the merge you are able to view the
combined changes before discarding or committing them.

.. Note::

    Mergubg requires the *ifcmerge* tool installed in your `PATH`, if it is
    not installed the merge operator will not be enabled.

Using other Git tools
---------------------

BlenderBIM is not a full Git user interface, but it provides most of the tools
you will need for day-to-day usage. In general if you need other Git
functionality you can use external Git tools with your repository and any
changes will be reflected in the BlenderBIM UI.
