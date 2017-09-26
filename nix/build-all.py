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
#     * git * bzip2 * tar * c(++) compilers * yacc * autoconf                 #
#                                                                             #
#   if building with USE_OCCT additionally:                                   #
#     * freetype * glx.h                                                      #
#                                                                             #
#     on debian 7.8 these can be obtained with:                               #
#          $ apt-get install git gcc g++ autoconf bison bzip2                 #
#            libfreetype6-dev mesa-common-dev                                 #
#                                                                             #
#     on ubuntu 14.04:                                                        #
#          $ apt-get install git gcc g++ autoconf bison make                  #
#            libfreetype6-dev mesa-common-dev                                 #
#                                                                             #
#     on OS X El Capitan with homebrew:                                       #
#          $ brew install git bison autoconf automake freetype                #
#                                                                             #
###############################################################################

import logging
import os
import sys
import subprocess as sp
import shutil
import time
import tarfile
import multiprocessing
import urllib

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

PROJECT_NAME="IfcOpenShell"
OCE_VERSION="0.18"
OCCT_VERSION="7.1.0"
OCCT_HASH="89aebde"
PYTHON_VERSIONS=["2.7.12", "3.2.6", "3.3.6", "3.4.6", "3.5.3", "3.6.2"]
BOOST_VERSION="1.59.0"
PCRE_VERSION="8.39"
LIBXML_VERSION="2.9.3"
CMAKE_VERSION="3.4.1"
ICU_VERSION="56.1"

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

def fullpath(arg):
	return os.path.realpath(os.path.dirname(sys.argv[1]))

def which(cmd):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path) and cmd in os.listdir(path):
            return cmd
    return None

def get_os():
    ret_value = sp.check_output([uname, "-s"]).strip()
    return ret_value

# Set defaults for missing empty environment variables

try:
    IFCOS_NUM_BUILD_PROCS = os.environ["IFCOS_NUM_BUILD_PROCS"]
except KeyError:
    IFCOS_NUM_BUILD_PROCS=multiprocessing.cpu_count() + 1
    os.environ["IFCOS_NUM_BUILD_PROCS"]=str(IFCOS_NUM_BUILD_PROCS)

try:
    TARGET_ARCH = os.environ["TARGET_ARCH"]
    del os.environ["TARGET_ARCH"]
except KeyError:
    TARGET_ARCH = sp.check_output([uname, "-m"]).strip()

CMAKE_DIR=os.path.realpath(os.path.join("..", "cmake"))

try:
    DEPS_DIR = os.environ["DEPS_DIR"]
except KeyError:
    DEPS_DIR = os.path.realpath(os.path.join("..", "build", sp.check_output(uname).strip(), TARGET_ARCH))
    os.environ["DEPS_DIR"] = DEPS_DIR
    if not os.path.exists(DEPS_DIR):
        os.makedirs(DEPS_DIR)

try:
    BUILD_CFG=os.environ["BUILD_CFG"]
except KeyError:
    BUILD_CFG="RelWithDebInfo"
    os.environ["BUILD_CFG"]=BUILD_CFG

USE_OCCT = os.environ.get("USE_OCCT", "true").lower() == "true"

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

# Check that required tools are in PATH

for cmd in [git, bunzip2, tar, cc, cplusplus, autoconf, automake, yacc, make]:
    if which(cmd) is None:
        raise ValueError("Required tool '%s' not installed or not added to PATH" % (cmd,))

# identifiers for the download tool (could be less memory consuming as ints, but are more verbose as strings)
download_tool_curl="curl"
download_tool_wget="wget"
download_tool_git = "git"

if which(wget) != None:
    download_tool_default = download_tool_wget
elif which(curl) != None:
    download_tool_default = download_tool_curl
else:
    raise ValueError("No download application found, tried: curl, wget")

CURL = ["curl", "-sL"]
WGET= ["wget", "-q", "--no-check-certificate"]

# Create log directory and file

log_dir = os.path.join(DEPS_DIR, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
LOG_FILE="%s.log" % (os.path.join(log_dir, sp.check_output([date, "+%Y%m%d"]).strip()),)
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()
logger.info("using command log file '%s'" % (LOG_FILE,))

def __check_call__(cmds, cwd=None):
    logger.debug("running command %r in directory %r" % (" ".join(cmds), cwd))
    log_file_handle = open(LOG_FILE, "a")
    proc = sp.Popen(cmds, cwd=cwd, stdout=log_file_handle, stderr=sp.PIPE)
    _, stderr = proc.communicate()
    log_file_handle.write(stderr)
    log_file_handle.close()

    if proc.returncode != 0:
        print "-" * 70
        print stderr
        print "-" * 70
        raise Exception("Command `%s` returned exit code %d" % (" ".join(cmds), proc.returncode))

def __check_output__(cmds, cwd=None):
    """Wraps `subprocess.check_output` and logs the command being executed,
    sets up logging `stderr` to `LOG_FILE` (in append mode) and strips the
    return value because it's unlikely that the newline at the end of output is
    useful and it often causes errors"""
    logger.debug("running command '%s' in directory %r" % (" ".join(cmds), cwd))
    log_file_handle = open(LOG_FILE, "a")
    ret_value = sp.check_output(cmds, cwd=cwd, stderr=log_file_handle).strip()
    logger.debug("command returned %r" % ret_value)
    log_file_handle.close()
    return ret_value

BOOST_VERSION_UNDERSCORE=BOOST_VERSION.replace(".", "_")
ICU_VERSION_UNDERSCORE=ICU_VERSION.replace(".", "_")
CMAKE_VERSION_2=CMAKE_VERSION[0:3]

OCE_LOCATION="https://github.com/tpaviot/oce/archive/OCE-%s.tar.gz" % (OCE_VERSION,)
BOOST_LOCATION="http://downloads.sourceforge.net/project/boost/boost/%s/boost_%s.tar.bz2" % (BOOST_VERSION, BOOST_VERSION_UNDERSCORE)
OPENCOLLADA_LOCATION="https://github.com/KhronosGroup/OpenCOLLADA.git"
OPENCOLLADA_COMMIT="f99d59e73e565a41715eaebc00c7664e1ee5e628"

# Helper functions

def run_autoconf(arg1, configure_args, cwd):
    configure_path = os.path.realpath(os.path.join(cwd, "..", "configure"))
    if not os.path.exists(configure_path):
        __check_call__([bash, "./autogen.sh"], cwd=os.path.realpath(os.path.join(cwd, ".."))) # only run autogen.sh in the directory it is located and use cwd to achieve that in order to not mess up things
    # Using `sh` over `bash` fixes issues with building swig 
    __check_call__(["/bin/sh", "../configure"]+configure_args+["--prefix=%s" % (os.path.realpath("%s/install/%s" % (DEPS_DIR, arg1)),)], cwd=cwd)

def run_cmake(arg1, cmake_args, cmake_dir=None, cwd=None):
    if cmake_dir is None:
        P=".."
    else:
        P=cmake_dir
    cmake_path= os.path.join(DEPS_DIR, "install", "cmake-%s" % (CMAKE_VERSION,), "bin", "cmake")
    __check_call__([cmake_path, P]+cmake_args+["-DCMAKE_BUILD_TYPE=%s" % (BUILD_CFG,)], cwd=cwd)

def run_icu(arg1, icu_args, cwd):
    PLATFORM=get_os()
    if PLATFORM == "Darwin":
        PLATFORM="MacOSX"
    __check_call__([bash, "../source/runConfigureICU", PLATFORM]+icu_args+["--prefix=%s/install/%s" % (DEPS_DIR, arg1)], cwd=cwd)

def git_clone(clone_url, target_dir, revision=None):
    """Lazily clones the `git` repository denoted by `clone_url` into
    `target_dir`, i.e. skips cloning if `target_dir` exists (naively assumes
    that a working clone exists there) and optionally checks out a revision
    `revision` after cloning or in the existing clone if `revision` is not
    `None`."""
    if not os.path.exists(target_dir):
        logger.info("cloning '%s' into '%s'" % (clone_url, target_dir))
        __check_call__([git, "clone", clone_url, target_dir])
    else:
        logger.info("directory '%s' exists, skipping cloning" % (target_dir,))
    if revision != None:
        __check_call__([git, "checkout", revision], cwd=target_dir)

def build_dependency(name, mode, build_tool_args, download_url, download_name, download_tool=download_tool_default, revision=None, additional_files={}, no_append_name=False):
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
    
    if download_tool == download_tool_curl or download_tool == download_tool_wget:
        if no_append_name:
            url = download_url
        else:
            url = os.path.join(download_url, download_name)
    
    if download_tool == download_tool_curl:
        download_path = os.path.join(build_dir, download_name)
        if not os.path.exists(download_path):
            __check_call__(CURL + ["-o", download_name, url], cwd=build_dir)
        else:
            logger.info("Download '%s' already exists, assuming it's an undamaged download and that it has been extracted if possible, skipping" % (download_path,))
    elif download_tool == download_tool_wget:
        download_path = os.path.join(build_dir, download_name)
        if not os.path.exists(download_path):
            __check_call__(WGET + ["-O", download_name, url], cwd=build_dir)
        else:
            logger.info("Download '%s' already exists, assuming it's an undamaged download and that it has been extracted if possible, skipping" % (download_path,))
    elif download_tool == download_tool_git:
        git_clone(download_url, target_dir=os.path.join(build_dir, download_name), revision=revision)
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
        #__check_output__([tar, "--exclude=\"*/*\"", "-tf", download_name], cwd=build_dir).strip() no longer works
        if extract_dir_name is None:
            extract_dir_name= __check_output__([bash, "-c", "tar -tf %s 2> /dev/null | head -n 1 | cut -f1 -d /" % (download_name,)], cwd=build_dir)
        extract_dir = os.path.join(build_dir, extract_dir_name)
        if not os.path.exists(extract_dir):
            __check_call__([tar, "-xf", download_name], cwd=build_dir)
    
    for path, url in additional_files.items():
        if not os.path.exists(path):
            urllib.urlretrieve(url, os.path.join(extract_dir, path))
            
    if mode != "bjam":
        extract_build_dir = os.path.join(extract_dir, "build")
        if os.path.exists(extract_build_dir):
            shutil.rmtree(extract_build_dir)
        os.makedirs(extract_build_dir)

        logger.info("\rConfiguring %s..." % (name,))
        if mode == "icu":
            run_icu(name, build_tool_args, cwd=extract_build_dir)
        elif mode == "autoconf":
            run_autoconf(name, build_tool_args, cwd=extract_build_dir)
        elif mode == "cmake":
            run_cmake(name, build_tool_args, cwd=extract_build_dir)
        else:
            raise ValueError()
        logger.info("\rBuilding %s...   " % (name,))
        __check_call__([make, "-j%s" % (IFCOS_NUM_BUILD_PROCS,)], cwd=extract_build_dir)
        logger.info( "\rInstalling %s... " % (name,))
        __check_call__([make, "install"], cwd=extract_build_dir)
        logger.info( "\rInstalled %s     \n" % (name,))
    else:
        logger.info( "\rConfiguring %s..." % (name,))
        __check_call__([bash, "./bootstrap.sh"], cwd=extract_dir)
        logger.info("\rBuilding %s...   " % (name,))
        __check_call__(["./b2", "-j%s" % (IFCOS_NUM_BUILD_PROCS,)]+build_tool_args, cwd=extract_dir)
        logger.info("\rInstalling %s... " % (name,))
        shutil.copytree(os.path.join(extract_dir, "boost"), os.path.join(DEPS_DIR, "install", "boost-%s" % BOOST_VERSION, "boost"))
        logger.info("\rInstalled %s     \n" % (name,))

cecho("Collecting dependencies:", GREEN)

# Set compiler flags for 32bit builds on 64bit system
# TODO: This is untested

ADDITIONAL_ARGS=[]
BOOST_ADDRESS_MODEL=[]
if TARGET_ARCH == "i686" and __check_output__([uname, "-m"]).strip() == "x86_64":
    ADDITIONAL_ARGS=["-m32", "-arch i386"]
    BOOST_ADDRESS_MODEL=["architecture=x86", "address-model=32"]

if get_os() == "Darwin":
    # C++11 features used in OCCT 7+ need a more recent stdlib
    version_min = "10.9" if USE_OCCT else "10.6"
    ADDITIONAL_ARGS=["-mmacosx-version-min=%s" % version_min]+ADDITIONAL_ARGS

# If the linker supports GC sections, set it up to reduce binary file size
# -fPIC is required for the shared libraries to work

try:
    CXXFLAGS=os.environ["CXXFLAGS"]
except KeyError:
    CXXFLAGS=""
try:
    CFLAGS=os.environ["CFLAGS"]
except KeyError:
    CFLAGS=""
try:
    LDFLAGS=os.environ["LDFLAGS"]
except KeyError:
    LDFLAGS=""
if sp.call([bash, "-c", "man ld 2> /dev/null | grep gc-sections &> /dev/null"]) == 0:
    CXXFLAGS_MINIMAL="%s -fPIC %s" % (CXXFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CXXFLAGS_MINIMAL"]=CXXFLAGS_MINIMAL
    CFLAGS_MINIMAL="%s -fPIC %s" % (CFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CFLAGS_MINIMAL"]=CFLAGS_MINIMAL
    CXXFLAGS="%s -fPIC -fdata-sections -ffunction-sections -fvisibility=hidden -fvisibility-inlines-hidden %s" % (CXXFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CXXFLAGS"]=CXXFLAGS
    CFLAGS="%s   -fPIC -fdata-sections -ffunction-sections -fvisibility=hidden %s"% (CFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CFLAGS"]=CFLAGS
    LDFLAGS="%s  -Wl,--gc-sections %s" % (LDFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["LDFLAGS"]=LDFLAGS
else:
    CXXFLAGS_MINIMAL="%s -fPIC %s" % (CXXFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CXXFLAGS_MINIMAL"]=CXXFLAGS_MINIMAL
    CFLAGS_MINIMAL="%s   -fPIC %s" % (CFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CFLAGS_MINIMAL"]=CFLAGS_MINIMAL
    CXXFLAGS="%s -fPIC -fvisibility=hidden -fvisibility-inlines-hidden %s" % (CXXFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CXXFLAGS"]=CXXFLAGS
    CFLAGS="%s   -fPIC -fvisibility=hidden -fvisibility-inlines-hidden %s" % (CFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["CFLAGS"]=CFLAGS
    LDFLAGS="%s %s" % (LDFLAGS, str.join(" ", ADDITIONAL_ARGS))
    os.environ["LDFLAGS"]=LDFLAGS

# Some dependencies need a more recent CMake version than most distros provide
build_dependency(name="cmake-%s" % (CMAKE_VERSION,), mode="autoconf", build_tool_args=[], download_url="https://cmake.org/files/v%s" % (CMAKE_VERSION_2,), download_name="cmake-%s.tar.gz" % (CMAKE_VERSION,))

# Extract compiler flags from CMake to harmonize settings with other autoconf dependencies
CMAKE_FLAG_EXTRACT_DIR="ifcopenshell_cmake_test_%s" % (time.time(),)
# was sp.check_output([bash, "-c", "cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | head -c 32"]), in bash script, unclear what the exact required format is and whether it's needed
if os.path.exists(CMAKE_FLAG_EXTRACT_DIR):
    shutil.rmtree(CMAKE_FLAG_EXTRACT_DIR)
os.makedirs(CMAKE_FLAG_EXTRACT_DIR)
BUILD_CFG_UPPER=BUILD_CFG.upper()
for FL in ["C", "CXX"]:
    __check_call__([bash, "-c", """echo "
    message(\"\${CMAKE_%s_FLAGS_%s}\")
    " > CMakeLists.txt""" % (FL, BUILD_CFG_UPPER)], cwd=CMAKE_FLAG_EXTRACT_DIR)
    FL="%sFLAGS" % (FL,)
    FLM="%sFLAGS_MINIMAL" % (FL,)
# @TODO: bash code unclear
#    exec("%sFLAGS=%s" % (FL, sp.check_output([os.path.join(DEPS_DIR, "install", "cmake-%s" % (CMAKE_VERSION,), "bin", "cmake"), "."
#    declare ${FL}FLAGS_MINIMAL="`$DEPS_DIR/install/cmake-$CMAKE_VERSION/bin/cmake . 2>&1 >/dev/null` ${!FLM}"
shutil.rmtree(CMAKE_FLAG_EXTRACT_DIR)

build_dependency(name="pcre-%s" % (PCRE_VERSION,), mode="autoconf", build_tool_args=["--disable-shared"], download_url="https://downloads.sourceforge.net/project/pcre/pcre/%s/" % (PCRE_VERSION,), download_name="pcre-%s.tar.bz2" % (PCRE_VERSION,))

# An issue exists with swig-1.3 and python >= 3.2
# Therefore, build a recent copy from source
build_dependency(name="swig", mode="autoconf", build_tool_args=["--with-pcre-prefix=%s/install/pcre-%s" % (DEPS_DIR, PCRE_VERSION)], download_url="https://github.com/swig/swig.git", download_name="swig", download_tool=download_tool_git, revision="rel-3.0.8")

if USE_OCCT:
    long_filename = "src/RWStepVisual/RWStepVisual_RWCharacterizedObjectAndCharacterizedRepresentationAndDraughtingModelAndRepresentation"
    occt_gitweb = "http://git.dev.opencascade.org/gitweb/?p=occt.git"
    build_dependency(
        name="occt-%s" % OCCT_VERSION,
        mode="cmake",
        build_tool_args=[
            "-DINSTALL_DIR=%s/install/occt-%s" % (DEPS_DIR, OCCT_VERSION),
            "-DBUILD_LIBRARY_TYPE=Static",
            "-DBUILD_MODULE_Draw=0",
        ],
        download_url="%s;a=snapshot;h=%s;sf=tgz" % (occt_gitweb, OCCT_HASH),
        additional_files = {
            "%s.hxx" % (long_filename): "%s;a=blob_plain;hb=%s;f=%s.hxx" % (occt_gitweb, OCCT_HASH, long_filename),
            "%s.cxx" % (long_filename): "%s;a=blob_plain;hb=%s;f=%s.cxx" % (occt_gitweb, OCCT_HASH, long_filename)
        },
        download_name="occt-%s.tar.gz" % OCCT_HASH,
        no_append_name=True)
else:
    build_dependency(name="oce-%s" % (OCE_VERSION,), mode="cmake", build_tool_args=["-DOCE_DISABLE_TKSERVICE_FONT=ON", "-DOCE_TESTING=OFF", "-DOCE_BUILD_SHARED_LIB=OFF", "-DOCE_DISABLE_X11=ON", "-DOCE_VISUALISATION=OFF", "-DOCE_OCAF=OFF", "-DOCE_INSTALL_PREFIX=%s/install/oce-%s" % (DEPS_DIR, OCE_VERSION)], download_url="https://github.com/tpaviot/oce/archive/", download_name="OCE-%s.tar.gz" % (OCE_VERSION,))
        
build_dependency("libxml2-%s" % (LIBXML_VERSION,), "autoconf", build_tool_args=["--without-python", "--disable-shared", "--without-zlib", "--without-iconv", "--without-lzma"], download_url="ftp://xmlsoft.org/libxml2/", download_name="libxml2-%s.tar.gz" % (LIBXML_VERSION,))
build_dependency("OpenCOLLADA", "cmake", build_tool_args=["-DLIBXML2_INCLUDE_DIR=%s/install/libxml2-%s/include/libxml2" % (DEPS_DIR, LIBXML_VERSION), "-DLIBXML2_LIBRARIES=%s/install/libxml2-%s/lib/libxml2.a" % (DEPS_DIR, LIBXML_VERSION), "-DPCRE_INCLUDE_DIR=%s/install/pcre-%s/include" % (DEPS_DIR, PCRE_VERSION), "-DPCRE_PCREPOSIX_LIBRARY=%s/install/pcre-%s/lib/libpcreposix.a" % (DEPS_DIR, PCRE_VERSION), "-DPCRE_PCRE_LIBRARY=%s/install/pcre-%s/lib/libpcre.a" % (DEPS_DIR, PCRE_VERSION), "-DCMAKE_INSTALL_PREFIX=%s/install/OpenCOLLADA/" % (DEPS_DIR,)], download_url="https://github.com/KhronosGroup/OpenCOLLADA.git", download_name="OpenCOLLADA", download_tool=download_tool_git, revision=OPENCOLLADA_COMMIT)

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
    build_dependency("python-%s%s" % (PYTHON_VERSION,abi_tag), "autoconf", PYTHON_CONFIGURE_ARGS + [unicode_conf], "http://www.python.org/ftp/python/%s/" % (PYTHON_VERSION,), "Python-%s.tgz" % (PYTHON_VERSION,))

os.environ["CXXFLAGS"]=OLD_CXX_FLAGS
os.environ["CFLAGS"]=OLD_C_FLAGS

str_concat = lambda prefix: lambda postfix: "=".join((prefix, postfix.strip()))
build_dependency("boost-%s" % (BOOST_VERSION,), mode="bjam", build_tool_args=["--stagedir=%s/install/boost-%s" % (DEPS_DIR, BOOST_VERSION), "--with-system", "--with-program_options", "--with-regex", "--with-thread", "--with-date_time", "--with-iostreams", "link=static"]+BOOST_ADDRESS_MODEL+list(map(str_concat("cxxflags"), CXXFLAGS.strip().split(' '))) + list(map(str_concat("linkflags"), LDFLAGS.strip().split(' '))) + ["stage", "-s", "NO_BZIP2=1"], download_url="http://downloads.sourceforge.net/project/boost/boost/%s/" % (BOOST_VERSION,), download_name="boost_%s.tar.bz2" % (BOOST_VERSION_UNDERSCORE,))

build_dependency(name="icu-%s" % (ICU_VERSION,), mode="icu", build_tool_args=["--enable-static", "--disable-shared"], download_url="http://download.icu-project.org/files/icu4c/%s/" % (ICU_VERSION,), download_name="icu4c-%s-src.tgz" % (ICU_VERSION_UNDERSCORE,))

cecho("Building IfcOpenShell:", GREEN)

IFCOS_DIR=os.path.join(DEPS_DIR, "build", "ifcopenshell")
if os.path.exists(IFCOS_DIR):
    shutil.rmtree(IFCOS_DIR)
os.makedirs(IFCOS_DIR)

executables_dir = os.path.join(IFCOS_DIR, "executables")
if not os.path.exists(executables_dir):
    os.makedirs(executables_dir)

logger.info("\rConfiguring executables...")

if USE_OCCT:
    occ_include_dir = "%s/install/occt-%s/include/opencascade" % (DEPS_DIR, OCCT_VERSION)
    occ_library_dir = "%s/install/occt-%s/lib" % (DEPS_DIR, OCCT_VERSION)
else:
    occ_include_dir = "%s/install/oce-%s/include/oce" % (DEPS_DIR, OCE_VERSION)
    occ_library_dir = "%s/install/oce-%s/lib" % (DEPS_DIR, OCE_VERSION)

run_cmake("", cmake_args=[
    "-DBOOST_ROOT="              "%s/install/boost-%s" % (DEPS_DIR, BOOST_VERSION),
    "-DOCC_INCLUDE_DIR="        +occ_include_dir,
    "-DOCC_LIBRARY_DIR="        +occ_library_dir,
    "-DOPENCOLLADA_INCLUDE_DIR=" "%s/install/OpenCOLLADA/include/opencollada" % (DEPS_DIR,),
    "-DOPENCOLLADA_LIBRARY_DIR=" "%s/install/OpenCOLLADA/lib/opencollada" % (DEPS_DIR,),
    "-DICU_INCLUDE_DIR="         "%s/install/icu-%s/include" % (DEPS_DIR, ICU_VERSION),
    "-DICU_LIBRARY_DIR="         "%s/install/icu-%s/lib" % (DEPS_DIR, ICU_VERSION),
    "-DPCRE_LIBRARY_DIR="        "%s/install/pcre-%s/lib" % (DEPS_DIR, PCRE_VERSION),
    "-DBUILD_IFCPYTHON="         "OFF",
    "-DUSE_MMAP="                "OFF",
    "-DCMAKE_INSTALL_PREFIX="    "%s/install/ifcopenshell" % (DEPS_DIR,)], cmake_dir=CMAKE_DIR, cwd=executables_dir)

logger.info("\rBuilding executables...   ")

__check_call__([make, "-j%s" % (IFCOS_NUM_BUILD_PROCS,)], cwd=executables_dir)
__check_call__([make, "install/strip"], cwd=executables_dir)

# On OSX the actual Python library is not linked against.
ADDITIONAL_ARGS=""
if get_os() == "Darwin":
    ADDITIONAL_ARGS="-Wl,-flat_namespace,-undefined,suppress"

os.environ["CXXFLAGS"]="%s %s" % (CXXFLAGS_MINIMAL, ADDITIONAL_ARGS)
os.environ["CFLAGS"]="%s %s" % (CFLAGS_MINIMAL, ADDITIONAL_ARGS)
os.environ["LDFLAGS"]="%s %s" % (LDFLAGS, ADDITIONAL_ARGS)

for PYTHON_VERSION, _, TAG in PYTHON_VERSION_CONFS():
    logger.info("\rConfiguring python %s%s wrapper..." % (PYTHON_VERSION, TAG))
    
    python_dir = os.path.join(IFCOS_DIR, "python-%s%s" % (PYTHON_VERSION, TAG))
    if not os.path.exists(python_dir):
        os.makedirs(python_dir)

    PYTHON_LIBRARY=__check_output__([bash, "-c", "ls    %s/install/python-%s%s/lib/libpython*.*" % (DEPS_DIR, PYTHON_VERSION, TAG)], cwd=None).strip()
    PYTHON_INCLUDE=__check_output__([bash, "-c", "ls -d %s/install/python-%s%s/include/python*" % (DEPS_DIR, PYTHON_VERSION, TAG)], cwd=None).strip()
    PYTHON_EXECUTABLE=os.path.join(DEPS_DIR, "install", "python-%s%s" % (PYTHON_VERSION, TAG), "bin", "python%s" % (PYTHON_VERSION[0],))
    os.environ["PYTHON_LIBRARY_BASENAME"]=os.path.basename(PYTHON_LIBRARY)
    
    run_cmake("", cmake_args=["-DBOOST_ROOT=%s/install/boost-%s" % (DEPS_DIR, BOOST_VERSION),
    "-DOCC_INCLUDE_DIR="+occ_include_dir,
    "-DOCC_LIBRARY_DIR="+occ_library_dir,
    "-DOPENCOLLADA_INCLUDE_DIR=%s/install/OpenCOLLADA/include/opencollada" % (DEPS_DIR,),
    "-DOPENCOLLADA_LIBRARY_DIR=%s/install/OpenCOLLADA/lib/opencollada" % (DEPS_DIR,),
    "-DICU_INCLUDE_DIR=%s/install/icu-%s/include" % (DEPS_DIR, ICU_VERSION),
    "-DICU_LIBRARY_DIR=%s/install/icu-%s/lib" % (DEPS_DIR, ICU_VERSION),
    "-DPYTHON_LIBRARY=%s" % (PYTHON_LIBRARY,),
    "-DPYTHON_EXECUTABLE=%s" % (PYTHON_EXECUTABLE,),
    "-DPYTHON_INCLUDE_DIR=%s" % (PYTHON_INCLUDE,),
    "-DSWIG_EXECUTABLE=%s/install/swig/bin/swig"  % (DEPS_DIR,),
    "-DCMAKE_INSTALL_PREFIX=%s/install/ifcopenshell/tmp" % (DEPS_DIR,),
    "-DCOLLADA_SUPPORT=OFF"], cmake_dir=CMAKE_DIR, cwd=python_dir)
    
    logger.info("\rBuilding python %s%s wrapper...   " % (PYTHON_VERSION, TAG))
    
    __check_call__([make, "-j%s" % (IFCOS_NUM_BUILD_PROCS,), "_ifcopenshell_wrapper"], cwd=python_dir)
    __check_call__([make, "install/local"], cwd=os.path.join(python_dir, "ifcwrap"))
    
    module_dir = os.path.dirname(__check_output__([PYTHON_EXECUTABLE, "-c", "from __future__ import print_function; import inspect, ifcopenshell; print(inspect.getfile(ifcopenshell))"]))
    
    if get_os() != "Darwin":
        # TODO: This symbol name depends on the Python version?
        __check_call__([strip, "-s", "-K", "PyInit__ifcopenshell_wrapper", "_ifcopenshell_wrapper.so"], cwd=module_dir)
        
    __check_call__([cp, "-R", module_dir, os.path.join(DEPS_DIR, "install", "ifcopenshell", "python-%s%s" % (PYTHON_VERSION, TAG))])

logger.info("\rBuilt IfcOpenShell...\n\n")
