Docker build environment
========================

This is a small utility to make it easy to compile a perfect `_ifcopenshell_wrapper.cpython-*-x86_64-linux-gnu.so`
files.

The reason for this tool is that I was trying to follow the web page directions, and my build was behaving differently
to the release builds. Eventually I concluded that the differences between toolchains on the RHEL based rocky9 image
and Ubuntu were just too great. Getting the build setup was already a lot of trial and error, so I thought I'd spend
more time trying to reuse the github actions that perform the build, using a utility called `act`. I learnt a lot, in
particular how much time, energy, and bandwidth Github waste. I also realised I was most of the way to a regular docker
setup anyway, so I might as well just do that. So I've deconstructed all the github action steps, and turned it into
a local docker build environment that uses the exact same base, tools, libraries, and build command/flags etc.

Right now a Github action will:
- launch the rocky9 base
- upgrade all the packages
- install a bunch of extra tools
- do a recursive checkout of your repo
- checkout the build repository
- unpack dependencies
- run the build script, making all python versions (5? right now I think)
- create the .zip release files

And it does _all_ of that _every_ time. This is not a fault of the action writers - it's just how Github seems to work.

These dockers tools do the following differently, and it's actually a bit more powerful too:
- build the base image once.
- update the packages once.
- install the extra tools once.
- the repository is the one on your host, that gets bind mounted in the container as the working directory.
- by adding an environment variable to .env, restricts to compiling for just a single python version.
- when the build is finished the created files are right there under your local repositry (but not added to git) for
  ease of access
- each repository can have it's own build environment container.
- the image is shared between those environments.
- the containers share the ccache, so additional envs should get a helping hand.
- it has a simple set of user friendly commands to drive it all.

For example:
``` bash
# To see the commands (a superset of docker compose commands)
./ifcos_env

# Enable autocomplete of commands
source .ifcos_env

# First time commands
./ifcos_env create
./ifcos_env up
./ifcos_env build

# install and test library
# find an issue
# edit code
./ifcos_env build

# and so on. When done stop and optionally delete the container
./ifcos_env stop
./ifcos_env remove
```

To limit the build to one python version just add
``` bash
PY_TGT=py-311
```
or whichever version your Blender requires.

You might see UNIQUE_ID in the .env file too. This keeps containers for separate folders, separate.

System requirements
1. Linux-x64 only at this time.
2. Docker and docker-compose need to be installed.
3. Have a good amount of disk space. (image is in /var (typically the root partition) and will be about 1.7 GB)
4. The build action will create about 10GB in your repository folder. Make sure this partition is spacious
   particularly if you intent on having multiple clones building.
5. ... I think that covers most of it.

