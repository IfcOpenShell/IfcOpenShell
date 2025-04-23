Desktop
=======

This folder contains everything needed to create file associations and icons to
present Bonsai as a desktop application.

Linux
-----

Assuming that blender and Bonsai are already installed on your system,
configure associations and icons for a single user by running `make`:

  make install

Test by running the wrapper script directly, this should launch Bonsai with
an empty IFC project:

  bonsai

This `Makefile` installs files to `~/.local` by default, to install to an
alternative location, set `DESTDIR`:

  sudo make install DESTDIR=/usr/local

### `command not found` error

If you have downloaded and installed blender from blender.org, then blender may
not be findable via your `PATH` environment variable.

Either add the folder containing the `blender` executable to your `PATH`, or
set the `BLENDER_EXE` environment variable to the location of the `blender`
executable.
Instructions will vary depending the linux distribution, consult your documentation.

Windows
-------

TODO
