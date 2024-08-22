Tracking revisions with Git
===========================

Bonsai supports tracking the development of your IFC files with a Git
repository.

Bonsai is an IFC file editor, you can create or load an IFC project,
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
otherwise Bonsai will offer to convert the folder into a repository.

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
to *commit* this to the Git repository. Bonsai gives you three options:

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

Viewing object history
----------------------

The history of *everything* in the project is tracked in Git, the revision log
for the currently selected object can be viewed with the Bonsai side-bar.

Retrieving Revisions
--------------------

Colourising the model will show you *which* things are different, but it won't
show you *how* they are different. As long as you have no uncommitted changes,
you can switch to the selected revision, this will load in Bonsai as a
full model that can be viewed and even edited.

.. Warning::

    Switching to a different revision actually changes the file on disk before
    loading it in Bonsai. Don't worry, the original hasn't been lost,
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
    Bonsai will not allow you to create invalid branch names.

To create a new branch from the current HEAD (ie. the top of the revision list)
enter a branch name when committing. Leaving this field empty just adds a
normal commit without creating a branch, however committing a change to an
earlier revision necessarily implies a new branch, so Bonsai will insist
that you give it a name.

Each branch can now be navigated separately in the revision list, to switch
between branches, and to any previous revision in any branch, select the
revision you are interested-in and switch as before.

.. Tip::

    Conceptually a local branch is equivalent to a remote fork in somebody
    else's copy of your repository, and indeed by adding a remote you
    can fetch their work into a *remote branch* in your local repository.

Merging
-------

.. Warning::

    Merging is experimental functionality. There are various circumstances
    where a merge will fail, don't worry, this won't break your model but you
    may not want to rely on this functionality without having some experience
    of what changes are likely to merge and what won't.

You can merge changes that exist in a selected revision into the current
model, even if changes have been made in both revisions - as long as these
changes don't directly conflict.

.. Note::

    Merging requires the *ifcmerge* tool installed in your `PATH`, if it is
    not installed the merge operator will not be enabled.

When two branches have diverged, merging an IFC model requires *conflict
resolution* (because added entities may inadvertently reuse the same Step-IDs),
this means that data on one side or the other may be rewritten by Bonsai in
order to accommodate both sets of changes. ie. the merge process is
*asymmetrical*.  Bonsai privileges data in the remote `origin/main` branch
over the local working branch, similarly it privileges data in the local `main`
branch over any other local working branch. The practical result of this is
that branches branched-off the `main` branch can generally be merged back into
`main`, but any sub-branches of these will need to be merged back into their
parent-branch *before* merging the parent-branch back into `main`.

Tags
----

Git tags are useful to label important revisions (think of *TENDER*,
*CONSTRUCTION*, *RevA* etc..). Tags appear as a prefix in the revision list,
which can be filtered to only show revisions with tags. Tags for the selected
revision are also listed in full below the revision list along with their
optional message text.

.. Note::

    Tag names have the same limitations as branch names, names should be short
    and without spaces, but can contain unicode characters, emojis etc...
    Bonsai will not allow you to create invalid or duplicate tag names.
    Similar to commit messages, tag messages should be 50 characters or less,
    though there is no practical limit.

.. Warning::

    Tags can be deleted locally, but Git is distributed, so if the tag has
    migrated to a remote repository it will reappear when you fetch changes
    from that repository.

Remote operations
-----------------

Git is a *distributed revision control system*, your local repository can be a
version of a remote repository and vice-versa. This is conceptually similar to
local branching except this remote repository could belong to someone else or
could be hosted by an online Git-forge service.

Your repository can have multiple remote repositories registered, each
can have potentially multiple branches.

Bonsai allows you to make a local *clone* of a remote repository.  You will
need to provide a URL *origin* to fetch, and an empty local folder to become
the local repository.

The *Fetch* operator retrieves new data from the remote repository. This isn't
automatically merged, each branch fetched from the remote repository appears as
a branch that can be browsed, switched-to or merged just like a local branch.
These remote branches have prefixed names, eg. `origin/main`.

Once you have committed changes to your local repository, the *Push* operator
tries to update the remote branch using changes from the selected local branch.

.. Warning::

    Remote repositories can be accessed in multiple ways; ssh, ftp or https
    protocols, for example, can require authentication. This authentication may
    expect you to generate and upload ssh keys, store API tokens, save
    username/password pairs, or use some other form of credential.
    Bonsai can't configure these credentials for you, follow the
    configuration instructions provided by your online service before trying
    actions that require authentication.

Using other Git tools
---------------------

Bonsai is not a full Git user interface, but it provides most of the tools
you will need for day-to-day usage. In general if you need other Git
functionality you can use external Git tools with your repository and any
changes will be reflected in the Bonsai UI.
