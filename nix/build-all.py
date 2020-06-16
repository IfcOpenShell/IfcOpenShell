#!/usr/bin/python
###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

###############################################################################
#                                                                             #
# This script builds IfcOpenShell and its dependencies                        #
#                                                                             #
# Prerequisites for this script to function correctly:                        #
#     * cmake * git * bzip2 * tar * c(++) compilers * yacc * autoconf         #
#                                                                             #
#   if building with USE_OCCT additionally:                                   #
#     * freetype * glx.h                                                      #
#                                                                             #
#   if building with OCCT 7.4.0 additionally:                                 #
#     * libfontconfig1-dev                                                    #
#                                                                             #
#   if building with -shared                                                  #
#     * libgl1-mesa-dev libxext-dev libxmu-dev libxmu-headers libxi-dev       #
#                                                                             #
#   for python37 to install correctly additionally:                           #
#     * libffi(-dev[el])                                                      #
#                                                                             #
#     on debian 7.8 these can be obtained with:                               #
#          $ apt-get install git gcc g++ autoconf bison bzip2 cmake           #
#            libfreetype6-dev mesa-common-dev libffi-dev libfontconfig1-dev   #
#                                                                             #
#     on ubuntu 14.04:                                                        #
#          $ apt-get install git gcc g++ autoconf bison make cmake            #
#            libfreetype6-dev mesa-common-dev libffi-dev libfontconfig1-dev   #
#                                                                             #
#     on OS X El Capitan with homebrew:                                       #
#          $ brew install git bison autoconf automake freetype libffi cmake   #
#                                                                             #
###############################################################################

from __future__ import print_function

import logging
import os
import sys
import subprocess as sp
import shutil
import time
import tarfile
import multiprocessing

PYTHON_MAJOR = sys.version_info[0]

if PYTHON_MAJOR >= 3:
    from urllib.request import urlretrieve
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlretrieve


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

PROJECT_NAME="IfcOpenShell"
PYTHON_VERSIONS=["2.7.16", "3.2.6", "3.3.6", "3.4.6", "3.5.3", "3.6.2", "3.7.3", "3.8.6", "3.9.1"]
JSON_VERSION="v3.6.1"
OCE_VERSION="0.18"
# OCCT_VERSION="7.1.0"
# OCCT_HASH="89aebde"
# OCCT_VERSION="7.2.0"
# OCCT_HASH="88af392"
OCCT_VERSION="7.3.0p3"
BOOST_VERSION="1.71.0"
#PCRE_VERSION="8.39"
PCRE_VERSION="8.41"
#LIBXML2_VERSION="2.9.3"
LIBXML2_VERSION="2.9.9"
SWIG_VERSION="3.0.12"
#SWIG_VERSION="4.0.0"
#OPENCOLLADA_VERSION="v1.6.63"
OPENCOLLADA_VERSION="v1.6.68"



# binaries
cp="cp"
bash="bash"
uname="uname"
git="git"
bunzip2="bunzip2"
tar="tar"
cc="cc"
cplusplus="c++"
autoconf="autoconf"
automake="automake"
yacc="yacc"
make="make"
date = "date"
curl="curl"
wget="wget"
strip="strip"

# Helper function for coloured printing

NO_COLOR="\033[0m" # <ref>http://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux</ref>
BLACK_ON_WHITE="\033[0;30;107m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
MAGENTA="\033[35m"

def cecho(message, color=NO_COLOR):
    """Logs message `message` in color `color`."""
    logger.info("%s%s\033[0m" % (color, message))

def which(cmd):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path) and cmd in os.listdir(path):
            return cmd
    return None

def get_os():
    ret_value = sp.check_output([uname, "-s"]).strip()
    return ret_value

def to_pystring(x):
    """ Python 2 & 3 compatibility function for strings handling 
    (to solve TypeError "Can't mix strings and bytes in path components" for Python 3).
    Reference https://github.com/hugsy/gef/issues/382 """
    res = str(x, encoding="utf-8") if PYTHON_MAJOR == 3 else x
    substs = [("\n","\\n"), ("\r","\\r"), ("\t","\\t"), ("\v","\\v"), ("\b","\\b"), ]
    for x,y in substs: res = res.replace(x,y)
    return res

# Set defaults for missing empty environment variables

USE_OCCT = os.environ.get("USE_OCCT", "true").lower() == "true"

TOOLSET = None
if get_os() == "Darwin":
    # C++11 features used in OCCT 7+ need a more recent stdlib
    TOOLSET = "10.9" if USE_OCCT else "10.6"

# python 3.4 doesn't seem to build anymore on recent versions of clang
if get_os() == "Darwin":
    try:
        PYTHON_VERSIONS.remove("3.4.6")
    except ValueError as e:
        pass
   
try:
    IFCOS_NUM_BUILD_PROCS = os.environ["IFCOS_NUM_BUILD_PROCS"]
except KeyError:
    IFCOS_NUM_BUILD_PROCS=multiprocessing.cpu_count() + 1

try:
    TARGET_ARCH = os.environ["TARGET_ARCH"]
except KeyError:
    TARGET_ARCH = sp.check_output([uname, "-m"]).strip()

CMAKE_DIR=os.path.realpath(os.path.join("..", "cmake"))

try:
    DEPS_DIR = os.environ["DEPS_DIR"]
except KeyError:
    path = [b"..", b"build", sp.check_output(uname).strip(), TARGET_ARCH]
    if TOOLSET:
        path.append(TOOLSET)
        
    DEPS_DIR = to_pystring(os.path.realpath(os.path.join(*path)))

if not os.path.exists(DEPS_DIR):
    os.makedirs(DEPS_DIR)

try:
    BUILD_CFG=os.environ["BUILD_CFG"]
except KeyError:
    BUILD_CFG="RelWithDebInfo"


# Print build configuration information

cecho ("""This script fetches and builds %s and its dependencies
""" % (PROJECT_NAME,), BLACK_ON_WHITE)
cecho("""Script configuration:

""", GREEN)
cecho("""* Target Architecture    = %s""" % (TARGET_ARCH,), MAGENTA)
cecho(" - Whether 32-bit (i686) or 64-bit (x86_64) will be built.")
cecho("""* USE_OCCT               = %r""" % (USE_OCCT,), MAGENTA)
if USE_OCCT:
    cecho(" - Compiling against official Open Cascade")
else:
    cecho(" - Compiling against Open Cascade Community Edition")
cecho("* Dependency Directory   = %s" % (DEPS_DIR,), MAGENTA)
cecho(" - The directory where %s dependencies are installed." % (PROJECT_NAME,))
cecho("* Build Config Type      = %s" % (BUILD_CFG,), MAGENTA)
cecho(""" - The used build configuration type for the dependencies.
   Defaults to RelWithDebInfo if not specified.""")

if BUILD_CFG == "MinSizeRel":
    cecho("     WARNING: MinSizeRel build can suffer from a significant performance loss.", RED)

cecho("* IFCOS_NUM_BUILD_PROCS  = %s" % (IFCOS_NUM_BUILD_PROCS,), MAGENTA)
cecho(""" - How many compiler processes may be run in parallel.
""")

dependency_tree = {
    'IfcParse': ('boost',  'libxml2'),
    'IfcGeom': ('IfcParse',  'occ'),
    'IfcConvert': ('IfcGeom',  'OpenCOLLADA', 'json'),
    'OpenCOLLADA': ('libxml2',  'pcre'),
    'IfcGeomServer': ('IfcGeom',),
    'IfcOpenShell-Python': ('python',  'swig',  'IfcGeom'),
    'swig': ('pcre',),
    'boost': (),
    'libxml2': (),
    'python': (),
    'occ': (),
    'pcre': (),
    'json': ()
}

def v(dep):
   yield dep
   for d in dependency_tree[dep]:
     for x in v(d):
       yield x

tgts = [s for s in sys.argv[1:] if not s.startswith("-")]
flags = set(s for s in sys.argv[1:] if s.startswith("-"))

BUILD_STATIC = not "-shared" in flags
ENABLE_FLAG = "--enable-static" if BUILD_STATIC else "--enable-shared"
DISABLE_FLAG = "--disable-shared" if BUILD_STATIC else "--disable-static"
LINK_TYPE = "static" if BUILD_STATIC else "shared"
LINK_TYPE_UCFIRST = LINK_TYPE[0].upper() + LINK_TYPE[1:]
LIBRARY_EXT = "a" if BUILD_STATIC else "so"
PIC = "-fPIC" if BUILD_STATIC else ""

if len(tgts):
    targets = set(sum((list(v(target)) for target in tgts), []))
else:
    targets = set(dependency_tree.keys())

print("Building:", *sorted(targets, key=lambda t: len(list(v(t)))))

# Check that required tools are in PATH

for cmd in [git, bunzip2, tar, cc, cplusplus, autoconf, automake, yacc, make, "patch", "cmake"]:
    if which(cmd) is None:
        raise ValueError("Required tool '%s' not installed or not added to PATH" % (cmd,))

# identifiers for the download tool (could be less memory consuming as ints, but are more verbose as strings)
download_tool_default = download_tool_py = "py"
download_tool_git = "git"

# Create log directory and file

log_dir = os.path.join(DEPS_DIR, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
LOG_FILE="%s.log" % (os.path.join(log_dir, to_pystring(sp.check_output([date, "+%Y%m%d"]).strip())),)
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()
logger.info("using command log file '%s'" % (LOG_FILE,))

def run(cmds, cwd=None):

    """
    Wraps `subprocess.Popen.communicate()` and logs the command being executed,
    sets up logging `stderr` to `LOG_FILE` (in append mode) and returns stdout
    with leading and trailing whitespace removed.
    """

    logger.debug("running command %r in directory %r" % (" ".join(cmds), cwd))
    log_file_handle = open(LOG_FILE, "ab")
    proc = sp.Popen(cmds, cwd=cwd, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = proc.communicate()
    log_file_handle.write(stdout)
    log_file_handle.write(stderr)
    log_file_handle.close()
    logger.debug("command returned %r" % proc.returncode)

    if proc.returncode != 0:
        print("-" * 70)
        print(stderr)
        print("-" * 70)
        raise Exception("Command `%s` returned exit code %d" % (" ".join(cmds), proc.returncode))

    return stdout.strip()

BOOST_VERSION_UNDERSCORE=BOOST_VERSION.replace(".", "_")

OCE_LOCATION="https://github.com/tpaviot/oce/archive/OCE-%s.tar.gz" % (OCE_VERSION,)
BOOST_LOCATION="https://dl.bintray.com/boostorg/release/%s/source/" % (BOOST_VERSION,)

# Helper functions

def run_autoconf(arg1, configure_args, cwd):
    configure_path = os.path.realpath(os.path.join(cwd, "..", "configure"))
    if not os.path.exists(configure_path):
        run([bash, "./autogen.sh"], cwd=os.path.realpath(os.path.join(cwd, ".."))) # only run autogen.sh in the directory it is located and use cwd to achieve that in order to not mess up things
    # Using `sh` over `bash` fixes issues with building swig 
    run(["/bin/sh", "../configure"]+configure_args+["--prefix=%s" % (os.path.realpath("%s/install/%s" % (DEPS_DIR, arg1)),)], cwd=cwd)

def run_cmake(arg1, cmake_args, cmake_dir=None, cwd=None):
    if cmake_dir is None:
        P=".."
    else:
        P=cmake_dir
    run(["cmake", P]+cmake_args+["-DCMAKE_BUILD_TYPE=%s" % (BUILD_CFG,)], cwd=cwd)

def git_clone_or_pull_repository(clone_url, target_dir, revision=None):
    """Lazily clones the `git` repository denoted by `clone_url` into
    the `target_dir` or pulls latest changes if the `target_dir` exists (naively assumes
    that a working clone exists there) and optionally checks out a revision
    `revision` after cloning or in the existing clone if `revision` is not
    `None`."""
    if not os.path.exists(target_dir):
        logger.info("cloning '%s' into '%s'" % (clone_url, target_dir))
        run([git, "clone", "--recursive", clone_url, target_dir])
    else:
        logger.info("directory '%s' already cloned. Pulling latest changes." % (target_dir,))

    # detect whether we are on a branch and pull
    if run([git, "rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir) != "HEAD":
        run([git, "pull", clone_url], cwd=target_dir)

    if revision != None:
        run([git, "checkout", revision], cwd=target_dir)


def build_dependency(name, mode, build_tool_args, download_url, download_name, download_tool=download_tool_default, revision=None, patch=None, additional_files={}, no_append_name=False):
    """Handles building of dependencies with different tools (which are
    distinguished with the `mode` argument. `build_tool_args` is expected to be
    a list which is necessary in order to not mess up quoting of compiler and
    linker flags."""
    check_dir = os.path.join(DEPS_DIR, "install", name)
    if os.path.exists(check_dir):
        logger.info( "Found existing %s, skipping" % (name,))
        return
    build_dir = os.path.join(DEPS_DIR, "build")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        
    logger.info("\rFetching %s...   " % (name,))
    
    if download_tool == download_tool_py:
        if no_append_name:
            url = download_url
        else:
            url = os.path.join(download_url, download_name)
            
        download_path = os.path.join(build_dir, download_name)
        if not os.path.exists(download_path):
            urlretrieve(url, os.path.join(build_dir, download_path))
        else:
            logger.info("Download '%s' already exists, assuming it's an undamaged download and that it has been extracted if possible, skipping" % (download_path,))
    elif download_tool == download_tool_git:
        logger.info("\rChecking %s...   " % (name,))
        git_clone_or_pull_repository(download_url, target_dir=os.path.join(build_dir, download_name), revision=revision)
    else:
        raise ValueError("download tool '%s' is not supported" % (download_tool,))
    download_dir = os.path.join(build_dir, download_name)
    
    if os.path.isdir(download_dir):
        extract_dir_name=download_name
        extract_dir = os.path.join(build_dir, extract_dir_name)
    else:
        download_tarfile_path = os.path.join(build_dir, download_name)
        if download_name.endswith(".tar.gz") or download_name.endswith(".tgz"):
            compr = "gz"
        elif download_name.endswith(".tar.bz2"):
            compr = "bz2"
        else:
            raise RuntimeError("fix source for new download type")
        download_tarfile = tarfile.open(name=download_tarfile_path, mode="r:%s" % (compr,))
        extract_dir_name= os.path.commonprefix(download_tarfile.getnames()) # tarfile seriously doesn't have a function to retrieve the root directory more easily
        #run([tar, "--exclude=\"*/*\"", "-tf", download_name], cwd=build_dir).strip() no longer works
        if extract_dir_name is None:
            extract_dir_name= run([bash, "-c", "tar -tf %s 2> /dev/null | head -n 1 | cut -f1 -d /" % (download_name,)], cwd=build_dir)
        extract_dir = os.path.join(build_dir, extract_dir_name)
        if not os.path.exists(extract_dir):
            run([tar, "-xf", download_name], cwd=build_dir)
    
    for path, url in additional_files.items():
        if not os.path.exists(path):
            urlretrieve(url, os.path.join(extract_dir, path))
            
    if patch is not None:
        patch_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), patch))
        if os.path.exists(patch_abs):
            try: run(["patch", "-p1", "--batch", "--forward", "-i", patch_abs], cwd=extract_dir)
            except Exception as e:
                # Assert that the patch has already been applied
                run(["patch", "-p1", "--batch", "--reverse", "--dry-run", "-i", patch_abs], cwd=extract_dir)
            
    if mode != "bjam":
        extract_build_dir = os.path.join(extract_dir, "build")
        if os.path.exists(extract_build_dir):
            shutil.rmtree(extract_build_dir)
        os.makedirs(extract_build_dir)

        logger.info("\rConfiguring %s..." % (name,))
        if mode == "autoconf":
            run_autoconf(name, build_tool_args, cwd=extract_build_dir)
        elif mode == "cmake":
            run_cmake(name, build_tool_args, cwd=extract_build_dir)
        else:
            raise ValueError()
        logger.info("\rBuilding %s...   " % (name,))
        run([make, "-j%s" % (IFCOS_NUM_BUILD_PROCS,), "VERBOSE=1"], cwd=extract_build_dir)
        logger.info( "\rInstalling %s... " % (name,))
        run([make, "install"], cwd=extract_build_dir)
        logger.info( "\rInstalled %s     \n" % (name,))
    else:
        logger.info( "\rConfiguring %s..." % (name,))
        run([bash, "./bootstrap.sh"], cwd=extract_dir)
        logger.info("\rBuilding %s...   " % (name,))
        run(["./b2", "-j%s" % (IFCOS_NUM_BUILD_PROCS,)]+build_tool_args, cwd=extract_dir)
        logger.info("\rInstalling %s... " % (name,))
        shutil.copytree(os.path.join(extract_dir, "boost"), os.path.join(DEPS_DIR, "install", "boost-%s" % BOOST_VERSION, "boost"))
        logger.info("\rInstalled %s     \n" % (name,))

cecho("Collecting dependencies:", GREEN)

# Set compiler flags for 32bit builds on 64bit system
# TODO: This is untested

ADDITIONAL_ARGS=[]
BOOST_ADDRESS_MODEL=[]
if TARGET_ARCH == "i686" and run([uname, "-m"]).strip() == "x86_64":
    if get_os() == "Darwin":
        ADDITIONAL_ARGS=["-m32", "-arch i386"]
    else:
        ADDITIONAL_ARGS=["-m32"]
    BOOST_ADDRESS_MODEL=["architecture=x86", "address-model=32"]

if get_os() == "Darwin":
    ADDITIONAL_ARGS=["-mmacosx-version-min=%s" % TOOLSET]+ADDITIONAL_ARGS

# If the linker supports GC sections, set it up to reduce binary file size
# -fPIC is required for the shared libraries to work

CXXFLAGS=os.environ.get("CXXFLAGS", "")
CFLAGS=os.environ.get("CFLAGS", "")
LDFLAGS=os.environ.get("LDFLAGS", "")

if sp.call([bash, "-c", "ld --gc-sections 2>&1 | grep -- --gc-sections &> /dev/null"]) != 0:
    CXXFLAGS_MINIMAL="%s %s %s" % (CXXFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
    CFLAGS_MINIMAL="%s %s %s" % (CFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
    if BUILD_STATIC:
        CXXFLAGS="%s %s -fdata-sections -ffunction-sections -fvisibility=hidden -fvisibility-inlines-hidden %s" % (CXXFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
        CFLAGS="%s   %s -fdata-sections -ffunction-sections -fvisibility=hidden %s"% (CFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
    else:
        CXXFLAGS=CXXFLAGS_MINIMAL
        CFLAGS=CFLAGS_MINIMAL
    LDFLAGS="%s  -Wl,--gc-sections %s" % (LDFLAGS, str.join(" ", ADDITIONAL_ARGS))
else:
    CXXFLAGS_MINIMAL="%s %s %s" % (CXXFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
    CFLAGS_MINIMAL="%s   %s %s" % (CFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
    if BUILD_STATIC:
        CXXFLAGS="%s %s -fvisibility=hidden -fvisibility-inlines-hidden %s" % (CXXFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
        CFLAGS="%s   %s -fvisibility=hidden -fvisibility-inlines-hidden %s" % (CFLAGS, PIC, str.join(" ", ADDITIONAL_ARGS))
    else:
        CXXFLAGS=CXXFLAGS_MINIMAL
        CFLAGS=CFLAGS_MINIMAL
    LDFLAGS="%s %s" % (LDFLAGS, str.join(" ", ADDITIONAL_ARGS))
    
os.environ["CXXFLAGS"] = CXXFLAGS
os.environ["CFLAGS"] = CFLAGS
os.environ["LDFLAGS"] = LDFLAGS

# Some dependencies need a more recent CMake version than most distros provide
# @tfk: this is no longer needed
# build_dependency(name="cmake-%s" % (CMAKE_VERSION,), mode="autoconf", build_tool_args=[], download_url="https://cmake.org/files/v%s" % (CMAKE_VERSION_2,), download_name="cmake-%s.tar.gz" % (CMAKE_VERSION,))

if "json" in targets:
    json_url = "https://github.com/nlohmann/json/releases/download/{JSON_VERSION}/json.hpp".format(**locals())
    json_install_path = "{DEPS_DIR}/install/json/nlohmann/json.hpp".format(**locals())
    if not os.path.exists(os.path.dirname(json_install_path)):
        os.makedirs(os.path.dirname(json_install_path))
    if not os.path.exists(json_install_path):
        urlretrieve(json_url, json_install_path)

if "pcre" in targets:
    build_dependency(
        name="pcre-{PCRE_VERSION}".format(**locals()),
        mode="autoconf",
        build_tool_args=[DISABLE_FLAG],
        download_url="https://downloads.sourceforge.net/project/pcre/pcre/{PCRE_VERSION}/".format(**locals()),
        download_name="pcre-{PCRE_VERSION}.tar.bz2".format(**locals())
    )

# An issue exists with swig-1.3 and python >= 3.2
# Therefore, build a recent copy from source
if "swig" in targets:
    build_dependency(
        name="swig",
        mode="autoconf",
        build_tool_args=["--disable-ccache", "--with-pcre-prefix={DEPS_DIR}/install/pcre-{PCRE_VERSION}".format(**locals())],
        download_url="https://github.com/swig/swig.git",
        download_name="swig",
        download_tool=download_tool_git,
        revision="rel-{SWIG_VERSION}".format(**locals())
    )

if USE_OCCT and "occ" in targets:
    build_dependency(
        name="occt-{OCCT_VERSION}".format(**locals()),
        mode="cmake",
        build_tool_args=[
            "-DINSTALL_DIR={DEPS_DIR}/install/occt-{OCCT_VERSION}".format(**locals()),
            "-DBUILD_LIBRARY_TYPE={LINK_TYPE_UCFIRST}".format(**locals()),
            "-DBUILD_MODULE_Draw=0",
            "-DBUILD_RELEASE_DISABLE_EXCEPTIONS=Off"
        ],
        download_url = "https://git.dev.opencascade.org/repos/occt.git",
        download_name = "occt",
        download_tool=download_tool_git,
        patch=None if OCCT_VERSION >= "7.4" else "./patches/occt/enable-exception-handling.patch",
        revision="V" + OCCT_VERSION.replace('.', '_')
    )
elif "occ" in targets:
    build_dependency(
        name="oce-{OCE_VERSION}".format(**locals()),
        mode="cmake",
        build_tool_args=[
            "-DOCE_DISABLE_TKSERVICE_FONT=ON",
            "-DOCE_TESTING=OFF",
            "-DOCE_BUILD_SHARED_LIB=OFF",
            "-DOCE_DISABLE_X11=ON",
            "-DOCE_VISUALISATION=OFF",
            "-DOCE_OCAF=OFF",
            "-DOCE_INSTALL_PREFIX={DEPS_DIR}/install/oce-{OCE_VERSION}".format(**locals())
        ],
        download_url="https://github.com/tpaviot/oce/archive/",
        download_name="OCE-{OCE_VERSION}.tar.gz".format(**locals())
    )
        
if "libxml2" in targets:
    build_dependency(
        "libxml2-{LIBXML2_VERSION}".format(**locals()),
        "autoconf",
        build_tool_args=[
            "--without-python",
            ENABLE_FLAG,
            DISABLE_FLAG,
            "--without-zlib",
            "--without-iconv",
            "--without-lzma"
        ],
        download_url="http://xmlsoft.org/download/",
        download_name="libxml2-{LIBXML2_VERSION}.tar.gz".format(**locals())
    )
    
if "OpenCOLLADA" in targets:
    build_dependency(
        "OpenCOLLADA",
        "cmake",
        build_tool_args=[
            "-DLIBXML2_INCLUDE_DIR={DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/include/libxml2".format(**locals()),
            "-DLIBXML2_LIBRARIES={DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/lib/libxml2.{LIBRARY_EXT}".format(**locals()),
            "-DPCRE_INCLUDE_DIR={DEPS_DIR}/install/pcre-{PCRE_VERSION}/include".format(**locals()),
            "-DPCRE_PCREPOSIX_LIBRARY={DEPS_DIR}/install/pcre-{PCRE_VERSION}/lib/libpcreposix.{LIBRARY_EXT}".format(**locals()),
            "-DPCRE_PCRE_LIBRARY={DEPS_DIR}/install/pcre-{PCRE_VERSION}/lib/libpcre.{LIBRARY_EXT}".format(**locals()),
            "-DCMAKE_INSTALL_PREFIX={DEPS_DIR}/install/OpenCOLLADA/".format(**locals())
        ],
        download_url="https://github.com/KhronosGroup/OpenCOLLADA.git",
        download_name="OpenCOLLADA",
        download_tool=download_tool_git,
        patch="./patches/opencollada/pr622_and_disable_subdirs.patch",
        revision=OPENCOLLADA_VERSION
    )

if "python" in targets:
    # Python should not be built with -fvisibility=hidden, from experience that introduces segfaults
    OLD_CXX_FLAGS=os.environ["CXXFLAGS"]
    OLD_C_FLAGS=os.environ["CFLAGS"]
    os.environ["CXXFLAGS"]=CXXFLAGS_MINIMAL
    os.environ["CFLAGS"]=CFLAGS_MINIMAL

    # On OSX a dynamic python library is built or it would not be compatible
    # with the system python because of some threading initialization
    PYTHON_CONFIGURE_ARGS=[]
    if get_os() == "Darwin":
        PYTHON_CONFIGURE_ARGS=["--disable-static", "--enable-shared"]

    def get_python_unicode_confs(py_ver):
        if py_ver < "3.3":
            return [("--enable-unicode=ucs2",""), ("--enable-unicode=ucs4","u")]
        else: return [("","")]

    def PYTHON_VERSION_CONFS():
        for v in PYTHON_VERSIONS:
            for unicode_conf, abi_tag in get_python_unicode_confs(v):
                yield v, unicode_conf, abi_tag

    for PYTHON_VERSION, unicode_conf, abi_tag in PYTHON_VERSION_CONFS():
        try:
            build_dependency(
                "python-{PYTHON_VERSION}{abi_tag}".format(**locals()),
                "autoconf",
                PYTHON_CONFIGURE_ARGS + [unicode_conf],
                "http://www.python.org/ftp/python/{PYTHON_VERSION}/".format(**locals()),
                "Python-{PYTHON_VERSION}.tgz".format(**locals())
            )
        except Exception as e:
            pyver2 = PYTHON_VERSION[:PYTHON_VERSION.rfind('.')]
            if os.path.exists("{DEPS_DIR}/install/python-{PYTHON_VERSION}{abi_tag}/bin/python{pyver2}".format(**locals())):
                print("Installation partially failed")
            else: raise e

    os.environ["CXXFLAGS"]=OLD_CXX_FLAGS
    os.environ["CFLAGS"]=OLD_C_FLAGS

if "boost" in targets:
    str_concat = lambda prefix: lambda postfix: "" if postfix.strip() == "" else "=".join((prefix, postfix.strip()))
    build_dependency(
        "boost-{BOOST_VERSION}".format(**locals()),
        mode="bjam",
        build_tool_args=[
            "--stagedir={DEPS_DIR}/install/boost-{BOOST_VERSION}".format(**locals()),
            "--with-system",
            "--with-program_options",
            "--with-regex",
            "--with-thread",
            "--with-date_time",
            "--with-iostreams",
            "link={LINK_TYPE}".format(**locals())
                                                                         ] + \
            BOOST_ADDRESS_MODEL                                            + \
            list(map(str_concat("cxxflags"), CXXFLAGS.strip().split(' '))) + \
            list(map(str_concat("linkflags"), LDFLAGS.strip().split(' '))) + \
            ["stage", "-s", "NO_BZIP2=1"],
        download_url=BOOST_LOCATION,
        download_name="boost_{BOOST_VERSION_UNDERSCORE}.tar.bz2".format(**locals())
    )
    
cecho("Building IfcOpenShell:", GREEN)

IFCOS_DIR=os.path.join(DEPS_DIR, "build", "ifcopenshell")
if os.path.exists(IFCOS_DIR):
    shutil.rmtree(IFCOS_DIR)
os.makedirs(IFCOS_DIR)

executables_dir = os.path.join(IFCOS_DIR, "executables")
if not os.path.exists(executables_dir):
    os.makedirs(executables_dir)

logger.info("\rConfiguring executables...")

OFF_ON = ["OFF", "ON"]

cmake_args=[
    "-DUSE_MMAP="                      "OFF",
    "-DBUILD_EXAMPLES="                "OFF",
    "-DBUILD_IFCPYTHON="               "OFF",
    "-DBUILD_SHARED_LIBS="            +OFF_ON[not BUILD_STATIC],
    "-DBUILD_IFCGEOM="                +OFF_ON["IfcGeom" in targets],
    "-DBUILD_GEOMSERVER="             +OFF_ON["IfcGeomServer" in targets],
    "-DBUILD_CONVERT="                +OFF_ON["IfcConvert" in targets],
    "-DCMAKE_INSTALL_PREFIX="          "{DEPS_DIR}/install/ifcopenshell".format(**locals()),
    "-DBOOST_ROOT="                    "{DEPS_DIR}/install/boost-{BOOST_VERSION}".format(**locals()),
    "-DGLTF_SUPPORT="                  "ON",
    "-DJSON_INCLUDE_DIR="              "{DEPS_DIR}/install/json".format(**locals()),
    "-DBoost_NO_BOOST_CMAKE="          "On"
]

if "occ" in targets and USE_OCCT:
    occ_include_dir =                  "{DEPS_DIR}/install/occt-{OCCT_VERSION}/include/opencascade".format(**locals())
    occ_library_dir =                  "{DEPS_DIR}/install/occt-{OCCT_VERSION}/lib".format(**locals())
    cmake_args.extend([
        "-DOCC_INCLUDE_DIR="           +occ_include_dir,
        "-DOCC_LIBRARY_DIR="           +occ_library_dir
    ])
elif "occ" in targets:
    occ_include_dir =                  "{DEPS_DIR}/install/oce-{OCE_VERSION}/include/oce".format(**locals())
    occ_library_dir =                  "{DEPS_DIR}/install/oce-{OCE_VERSION}/lib"
    cmake_args.extend([
        "-DOCC_INCLUDE_DIR="           +occ_include_dir,
        "-DOCC_LIBRARY_DIR="           +occ_library_dir
    ])

if "OpenCOLLADA" in targets:
    cmake_args.extend([
        "-DOPENCOLLADA_INCLUDE_DIR="   "{DEPS_DIR}/install/OpenCOLLADA/include/opencollada".format(**locals()),
        "-DOPENCOLLADA_LIBRARY_DIR="   "{DEPS_DIR}/install/OpenCOLLADA/lib/opencollada".format(**locals())
    ])

if "pcre" in targets:
    cmake_args.append(
        "-DPCRE_LIBRARY_DIR="          "{DEPS_DIR}/install/pcre-{PCRE_VERSION}/lib".format(**locals())
    )

if "libxml2" in targets:
    cmake_args.extend([
        "-DLIBXML2_INCLUDE_DIR="       "{DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/include/libxml2".format(**locals()),
        "-DLIBXML2_LIBRARIES="         "{DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/lib/libxml2.{LIBRARY_EXT}".format(**locals())
    ])

run_cmake("", cmake_args, cmake_dir=CMAKE_DIR, cwd=executables_dir)

logger.info("\rBuilding executables...   ")

run([make, "-j{IFCOS_NUM_BUILD_PROCS}".format(**locals())], cwd=executables_dir)
run([make, "install/strip" if BUILD_CFG == "Release" else "install"], cwd=executables_dir)

if "IfcOpenShell-Python" in targets:

    # On OSX the actual Python library is not linked against.
    ADDITIONAL_ARGS=""
    if get_os() == "Darwin":
        ADDITIONAL_ARGS="-Wl,-flat_namespace,-undefined,suppress"

    os.environ["CXXFLAGS"]="%s %s" % (CXXFLAGS_MINIMAL, ADDITIONAL_ARGS)
    os.environ["CFLAGS"]="%s %s" % (CFLAGS_MINIMAL, ADDITIONAL_ARGS)
    os.environ["LDFLAGS"]="%s %s" % (LDFLAGS, ADDITIONAL_ARGS)

    for PYTHON_VERSION, _, TAG in PYTHON_VERSION_CONFS():
        logger.info("\rConfiguring python {PYTHON_VERSION}{TAG} wrapper...".format(**locals()))

        # python_dir = os.path.join(IFCOS_DIR, "python-{PYTHON_VERSION}{TAG}".format(**locals()))
        python_dir = os.path.join(IFCOS_DIR, "pythonwrapper")
        if not os.path.exists(python_dir):
            os.makedirs(python_dir)

        cache_path = os.path.join(python_dir, "CMakeCache.txt")
        if os.path.exists(cache_path):
            os.unlink(cache_path)

        PYTHON_LIBRARY=run([bash, "-c", "ls    {DEPS_DIR}/install/python-{PYTHON_VERSION}{TAG}/lib/libpython*.*".format(**locals())])
        PYTHON_INCLUDE=run([bash, "-c", "ls -d {DEPS_DIR}/install/python-{PYTHON_VERSION}{TAG}/include/python*".format(**locals())])
        PYTHON_EXECUTABLE=os.path.join(DEPS_DIR, "install", "python-{PYTHON_VERSION}{TAG}".format(**locals()), "bin", "python{PYTHON_VERSION[0]}".format(**locals()))
        os.environ["PYTHON_LIBRARY_BASENAME"]=os.path.basename(PYTHON_LIBRARY)

        run_cmake("",
            cmake_args=[
                "-DBUILD_SHARED_LIBS="       "OFF" if BUILD_STATIC else "ON",
                "-DBOOST_ROOT="              "{DEPS_DIR}/install/boost-{BOOST_VERSION}".format(**locals()),
                "-DOCC_INCLUDE_DIR="         +occ_include_dir,
                "-DOCC_LIBRARY_DIR="         +occ_library_dir,
                "-DPYTHON_LIBRARY="          +PYTHON_LIBRARY,
                "-DPYTHON_EXECUTABLE="       +PYTHON_EXECUTABLE,
                "-DPYTHON_INCLUDE_DIR="      +PYTHON_INCLUDE,
                "-DSWIG_EXECUTABLE="         "{DEPS_DIR}/install/swig/bin/swig".format(**locals()),
                "-DCMAKE_INSTALL_PREFIX="    "{DEPS_DIR}/install/ifcopenshell/tmp".format(**locals()),
                "-DLIBXML2_INCLUDE_DIR="     "{DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/include/libxml2".format(**locals()),
                "-DLIBXML2_LIBRARIES="       "{DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/lib/libxml2.{LIBRARY_EXT}".format(**locals()),
                "-DCOLLADA_SUPPORT=OFF"
            ], cmake_dir=CMAKE_DIR, cwd=python_dir)
        
        logger.info("\rBuilding python %s%s wrapper...   " % (PYTHON_VERSION, TAG))

        run([make, "-j%s" % (IFCOS_NUM_BUILD_PROCS,), "_ifcopenshell_wrapper"], cwd=python_dir)
        run([make, "install/local"], cwd=os.path.join(python_dir, "ifcwrap"))

        module_dir = os.path.dirname(run([PYTHON_EXECUTABLE, "-c", "from __future__ import print_function; import inspect, ifcopenshell; print(inspect.getfile(ifcopenshell))"]))

        if get_os() != "Darwin":
            # TODO: This symbol name depends on the Python version?
            run([strip, "-s", "-K", "PyInit__ifcopenshell_wrapper", "_ifcopenshell_wrapper.so"], cwd=module_dir)

        run([cp, "-R", module_dir, os.path.join(DEPS_DIR, "install", "ifcopenshell", "python-%s%s" % (PYTHON_VERSION, TAG))])

logger.info("\rBuilt IfcOpenShell...\n\n")
