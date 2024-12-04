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
#     * cmake * git * bzip2 * tar * c(++) compilers * autoconf                #
#                                                                             #
#   if building with USE_OCCT additionally:                                   #
#     * glx.h                                                                 #
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
#            mesa-common-dev libffi-dev libfontconfig1-dev                    #
#                                                                             #
#     on ubuntu 14.04:                                                        #
#          $ apt-get install git gcc g++ autoconf bison make cmake            #
#            mesa-common-dev libffi-dev libfontconfig1-dev                    #
#                                                                             #
#     on OS X El Capitan with homebrew:                                       #
#          $ brew install git bison autoconf automake libffi cmake            #
#                                                                             #
#     on RHEL-related distros:                                                #
#          $ yum install git gcc gcc-c++ autoconf bison make cmake            #
#            mesa-libGL-devel libffi-devel fontconfig-devel bzip2             #
#            automake patch                                                   #
###############################################################################
import logging
import os
import re
import sys
import glob
import subprocess as sp
import shutil
import tarfile
import multiprocessing
import platform
import sysconfig

# @todo temporary for expired mpfr.org certificate on 2023-04-08
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from urllib.request import urlretrieve


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

PROJECT_NAME = "IfcOpenShell"
USE_CURRENT_PYTHON_VERSION = os.getenv("USE_CURRENT_PYTHON_VERSION")
ADD_COMMIT_SHA = os.getenv("ADD_COMMIT_SHA")

PYTHON_VERSIONS = ["3.9.11", "3.10.3", "3.11.8", "3.12.1", "3.13.0"]
JSON_VERSION = "v3.6.1"
OCE_VERSION = "0.18.3"
OCCT_VERSION = "7.8.1"
BOOST_VERSION = "1.86.0"
PCRE_VERSION = "8.41"
LIBXML2_VERSION = "2.9.11"
SWIG_VERSION = "4.0.2"
OPENCOLLADA_VERSION = "v1.6.68"
HDF5_VERSION = "1.12.1"

GMP_VERSION = "6.2.1"
MPFR_VERSION = "3.1.6" # latest is 4.1.0
CGAL_VERSION = "5.3"
USD_VERSION = "23.05"
TBB_VERSION = "2021.9.0"

# binaries
cp = "cp"
bash = "bash"
git = "git"
bunzip2 = "bunzip2"
tar = "tar"
cc = "cc"
cplusplus = "c++"
autoconf = "autoconf"
automake = "automake"
make = "make"
date = "date"
curl = "curl"
wget = "wget"
strip = "strip"

explicit_targets = [s for s in sys.argv[1:] if not s.startswith("-")]
flags = set(s.lstrip('-') for s in sys.argv[1:] if s.startswith("-"))

# Helper function for coloured printing

NO_COLOR = "\033[0m" # <ref>http://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux</ref>
BLACK_ON_WHITE = "\033[0;30;107m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"

def cecho(message, color=NO_COLOR):
    """Logs message `message` in color `color`."""
    logger.info(f"{color}{message}\033[0m")

def which(cmd):
    for path in os.getenv("PATH").split(":"):
        if os.path.exists(path) and cmd in os.listdir(path):
            return cmd
    return None


# Set defaults for missing empty environment variables

USE_OCCT = os.environ.get("USE_OCCT", "true").lower() == "true"

TOOLSET = None
if platform.system() == "Darwin":
    # C++11 features used in OCCT 7+ need a more recent stdlib
    TOOLSET = "10.9" if USE_OCCT else "10.6"


IFCOS_NUM_BUILD_PROCS = os.getenv("IFCOS_NUM_BUILD_PROCS", multiprocessing.cpu_count() + 1)

CMAKE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "cmake"))

build_dir = os.environ.get("BUILD_DIR", os.path.join(os.path.dirname(__file__), "..", "build"))

path = [build_dir, platform.system(), "wasm" if "wasm" in flags else platform.machine()]
if TOOLSET:
    path.append(TOOLSET)
DEFAULT_DEPS_DIR = os.path.realpath(os.path.join(*path))

DEPS_DIR = os.getenv("DEPS_DIR", DEFAULT_DEPS_DIR)

if not os.path.exists(DEPS_DIR):
    os.makedirs(DEPS_DIR)

BUILD_CFG = os.getenv("BUILD_CFG", "RelWithDebInfo")


# Print build configuration information

cecho (f"""This script fetches and builds {PROJECT_NAME} and its dependencies
""", BLACK_ON_WHITE)
cecho("""Script configuration:

""", GREEN)
cecho(f"""* USE_OCCT               = {USE_OCCT}""", MAGENTA)
if USE_OCCT:
    cecho(" - Compiling against official Open Cascade")
else:
    cecho(" - Compiling against Open Cascade Community Edition")
cecho(f"* Dependency Directory   = {DEPS_DIR}", MAGENTA)
cecho(f" - The directory where {PROJECT_NAME} dependencies are installed.")
cecho(f"* Build Config Type      = {BUILD_CFG}", MAGENTA)
cecho(""" - The used build configuration type for the dependencies.
   Defaults to RelWithDebInfo if not specified.""")

if BUILD_CFG == "MinSizeRel":
    cecho("     WARNING: MinSizeRel build can suffer from a significant performance loss.", RED)

cecho(f"* IFCOS_NUM_BUILD_PROCS  = {IFCOS_NUM_BUILD_PROCS}", MAGENTA)
cecho(""" - How many compiler processes may be run in parallel.
""")

dependency_tree = {
    'IfcParse': ('boost', 'libxml2', 'hdf5'),
    'IfcGeom': ('IfcParse', 'occ', 'json', 'cgal', 'eigen'),
    'IfcConvert': ('IfcGeom',),
    'OpenCOLLADA': ('libxml2', 'pcre'),
    'IfcGeomServer': ('IfcGeom',),
    'IfcOpenShell-Python': ('python', 'swig', 'IfcGeom'),
    'swig': ('pcre',),
    'boost': (),
    'libxml2': (),
    'python': (),
    'occ': ('freetype',),
    'pcre': (),
    'json': (),
    'hdf5': (),
    'cgal': (),
    'eigen': (),
    'freetype': (),
    # 'usd': ('boost', 'oneTBB')
}

def v(dep):
   yield dep
   for d in dependency_tree[dep]:
     for x in v(d):
       yield x

if "v" in flags:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

OFF_ON = ["OFF", "ON"]
BUILD_STATIC = "shared" not in flags
ENABLE_FLAG = "--enable-static" if BUILD_STATIC else "--enable-shared"
DISABLE_FLAG = "--disable-shared" if BUILD_STATIC else "--disable-static"
LINK_TYPE = "static" if BUILD_STATIC else "shared"
LINK_TYPE_UCFIRST = LINK_TYPE[0].upper() + LINK_TYPE[1:]
LIBRARY_EXT = "a" if BUILD_STATIC else "so"
PIC = "-fPIC" if BUILD_STATIC else ""

if any(f.startswith("py-") for f in flags):
    PYTHON_VERSIONS = [pyv for pyv in PYTHON_VERSIONS if "py-%s" % "".join(pyv.split('.')[0:2]) in flags]

if len(explicit_targets):
    targets = set(sum((list(v(target)) for target in explicit_targets), []))
else:
    targets = set(dependency_tree.keys())
    
targets = set(t for t in targets if 'without-%s' % t.lower() not in flags)

print("Building:", *sorted(targets, key=lambda t: len(list(v(t)))))

# Check that required tools are in PATH

for cmd in [git, bunzip2, tar, cc, cplusplus, autoconf, automake, make, "patch", "cmake"]:
    if which(cmd) is None:
        raise ValueError(f"Required tool '{cmd}' not installed or not added to PATH")

# identifiers for the download tool (could be less memory consuming as ints, but are more verbose as strings)
download_tool_default = download_tool_py = "py"
download_tool_git = "git"

# Create log directory and file

log_dir = os.path.join(DEPS_DIR, "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
LOG_FILE = os.path.join(log_dir, sp.check_output([date, "+%Y%m%d"], encoding="utf-8").strip()) + ".log"
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()
logger.info(f"using command log file '{LOG_FILE}'")

# Causing havoc in python 3.11 build
try:
    del os.environ['__PYVENV_LAUNCHER__']
except: pass

def run(cmds, cwd=None, can_fail=False):

    """
    Wraps `subprocess.Popen.communicate()` and logs the command being executed,
    sets up logging `stderr` to `LOG_FILE` (in append mode) and returns stdout
    with leading and trailing whitespace removed.
    """

    logger.debug(f"running command {' '.join(cmds)} in directory {cwd}")
    log_file_handle = open(LOG_FILE, "a")
    proc = sp.Popen(cmds, cwd=cwd, stdout=sp.PIPE, stderr=sp.PIPE, encoding="utf-8")
    stdout, stderr = proc.communicate()
    log_file_handle.write(stdout)
    log_file_handle.write(stderr)
    log_file_handle.close()
    logger.debug(f"command returned {proc.returncode}")

    if proc.returncode != 0 and not can_fail:
        print("-" * 70)
        print(stderr)
        print("-" * 70)
        raise RuntimeError(f"Command `{' '.join(cmds)}` returned exit code {proc.returncode}")

    return stdout.strip()

if platform.system() == "Darwin":
    if run(["sw_vers", "-productVersion"]) >= "11.":
        # Apparently not supported
        PYTHON_VERSIONS = [pv for pv in PYTHON_VERSIONS if tuple(map(int, pv.split("."))) >= (3, 7)]
    if run(["sw_vers", "-productVersion"]) < "10.16":
        # This is now solved with the '__PYVENV_LAUNCHER__' hack
        # PYTHON_VERSIONS = [pv for pv in PYTHON_VERSIONS if tuple(map(int, pv.split("."))) < (3, 11)]
        pass

BOOST_VERSION_UNDERSCORE = BOOST_VERSION.replace(".", "_")

OCE_LOCATION = f"https://github.com/tpaviot/oce/archive/OCE-{OCE_VERSION}.tar.gz"
BOOST_LOCATION = f"https://boostorg.jfrog.io/artifactory/main/release/{BOOST_VERSION}/source/"

# Helper functions


def run_autoconf(arg1, configure_args, cwd):
    configure_path = os.path.realpath(os.path.join(cwd, "..", "configure"))
    if not os.path.exists(configure_path):
        run([bash, "./autogen.sh"], cwd=os.path.realpath(os.path.join(cwd, ".."))) # only run autogen.sh in the directory it is located and use cwd to achieve that in order to not mess up things
    # Using `sh` over `bash` fixes issues with building swig 
    prefix = os.path.realpath(f"{DEPS_DIR}/install/{arg1}")

    wasm = []
    if "wasm" in flags:
        wasm.append("emconfigure")

    run([*wasm, "/bin/sh", "../configure"] + configure_args + [f"--prefix={prefix}"], cwd=cwd)


def run_cmake(arg1, cmake_args, cmake_dir=None, cwd=None):
    if cmake_dir is None:
        P = ".."
    else:
        P = cmake_dir
        
    wasm = []
    if "wasm" in flags:
        wasm.append("emcmake")
        
    run([*wasm, "cmake", P, *cmake_args, f"-DCMAKE_BUILD_TYPE={BUILD_CFG}", f"-DBUILD_SHARED_LIBS={OFF_ON[not BUILD_STATIC]}"], cwd=cwd)


def git_clone_or_pull_repository(clone_url, target_dir, revision=None):
    """Lazily clones the `git` repository denoted by `clone_url` into
    the `target_dir` or pulls latest changes if the `target_dir` exists (naively assumes
    that a working clone exists there) and optionally checks out a revision
    `revision` after cloning or in the existing clone if `revision` is not
    `None`."""
    if not os.path.exists(target_dir):
        logger.info(f"cloning '{clone_url}' into '{target_dir}'")
        run([git, "clone", "--recursive", clone_url, target_dir])
    else:
        logger.info(f"directory '{target_dir}' already cloned. Pulling latest changes.")
        run([git, "-C", target_dir, "fetch", "--all", "--tags"])

    # detect whether we are on a branch and pull
    if run([git, "rev-parse", "--abbrev-ref", "HEAD"], cwd=target_dir) != "HEAD":
        run([git, "pull", clone_url], cwd=target_dir)

    if revision != None:
        run([git, "reset", "--hard"], cwd=target_dir)
        run([git, "fetch", "--all"], cwd=target_dir)
        run([git, "checkout", revision], cwd=target_dir)


def build_dependency(name, mode, build_tool_args, download_url, download_name, download_tool=download_tool_default, revision=None, patch=None, additional_files={}, no_append_name=False, **kwargs):
    """Handles building of dependencies with different tools (which are
    distinguished with the `mode` argument. `build_tool_args` is expected to be
    a list which is necessary in order to not mess up quoting of compiler and
    linker flags."""
    check_dir = os.path.join(DEPS_DIR, "install", name)
    if os.path.exists(check_dir):
        logger.info(f"Found existing {name}, skipping")
        return
    build_dir = os.path.join(DEPS_DIR, "build")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        
    logger.info(f"\rFetching {name}...   ")
    
    if download_tool == download_tool_py:
        if no_append_name:
            url = download_url
        else:
            url = os.path.join(download_url, download_name)
            
        download_path = os.path.join(build_dir, download_name)
        if not os.path.exists(download_path):
            urlretrieve(url, os.path.join(build_dir, download_path))
        else:
            logger.info(f"Download '{download_path}' already exists, assuming it's an undamaged download and that it has been extracted if possible, skipping")
    elif download_tool == download_tool_git:
        logger.info(f"\rChecking {name}...   ")
        git_clone_or_pull_repository(download_url, target_dir=os.path.join(build_dir, download_name), revision=revision)
    else:
        raise ValueError(f"download tool '{download_tool}' is not supported")
    download_dir = os.path.join(build_dir, download_name)
    
    if os.path.isdir(download_dir):
        extract_dir_name = download_name
        extract_dir = os.path.join(build_dir, extract_dir_name)
    else:
        download_tarfile_path = os.path.join(build_dir, download_name)
        if download_name.endswith(".tar.gz") or download_name.endswith(".tgz"):
            compr = "gz"
        elif download_name.endswith(".tar.bz2"):
            compr = "bz2"
        else:
            raise RuntimeError("fix source for new download type")
        download_tarfile = tarfile.open(name=download_tarfile_path, mode=f"r:{compr}")
        # tarfile seriously doesn't have a function to retrieve the root directory more easily
        extract_dir_name = os.path.commonprefix([x for x in download_tarfile.getnames() if x != "."])
        #run([tar, "--exclude=\"*/*\"", "-tf", download_name], cwd=build_dir).strip() no longer works
        if extract_dir_name is None:
            extract_dir_name = run([bash, "-c", f"tar -tf {download_name} 2> /dev/null | head -n 1 | cut -f1 -d /"], cwd=build_dir)
        extract_dir = os.path.join(build_dir, extract_dir_name)
        if not os.path.exists(extract_dir):
            run([tar, "-xf", download_name], cwd=build_dir)
    
    for path, url in additional_files.items():
        if not os.path.exists(path):
            urlretrieve(url, os.path.join(extract_dir, path))
            
    if patch is not None:
        if isinstance(patch, str):
            patch = [patch]
        for p in patch:
            patch_abs = os.path.abspath(os.path.join(os.path.dirname(__file__), p))
            if os.path.exists(patch_abs):
                try: run(["patch", "-p1", "--batch", "--forward", "-i", patch_abs], cwd=extract_dir)
                except Exception as e:
                    # Assert that the patch has already been applied
                    run(["patch", "-p1", "--batch", "--reverse", "--dry-run", "-i", patch_abs], cwd=extract_dir)
    
    if mode == "ctest":
        run(["ctest", "-S", "HDF5config.cmake,BUILD_GENERATOR=Unix", "-C", BUILD_CFG, "-V", "-O", "hdf5.log"], cwd=extract_dir)
        run([tar, "-xf", kwargs["ctest_result"] + ".tar.gz"], cwd=os.path.join(extract_dir, 'build'))
        shutil.copytree(
            os.path.join(extract_dir, "build", kwargs["ctest_result"], kwargs["ctest_result_path"]),
            os.path.join(DEPS_DIR, "install", name)
        )
    elif mode != "bjam":
        extract_build_dir = os.path.join(extract_dir, "build")
        if os.path.exists(extract_build_dir):
            shutil.rmtree(extract_build_dir)
        os.makedirs(extract_build_dir)

        logger.info(f"\rConfiguring {name}...")
        if mode == "autoconf":
            run_autoconf(name, build_tool_args, cwd=extract_build_dir)
        elif mode == "cmake":
            run_cmake(name, build_tool_args, cwd=extract_build_dir)
        else:
            raise ValueError()
        logger.info(f"\rBuilding {name}...   ")
        run([make, f"-j{IFCOS_NUM_BUILD_PROCS}", "VERBOSE=1"], cwd=extract_build_dir)
        logger.info(f"\rInstalling {name}... ")
        run([make, "install"], cwd=extract_build_dir)
        logger.info(f"\rInstalled {name}     \n")
    else:
        logger.info(f"\rConfiguring {name}...")
        run([bash, "./bootstrap.sh"], cwd=extract_dir)
        logger.info(f"\rBuilding {name}...   ")
        run(["./b2", f"-j{IFCOS_NUM_BUILD_PROCS}"] + build_tool_args, cwd=extract_dir, can_fail="wasm" in flags)
        logger.info(f"\rInstalling {name}... ")
        shutil.copytree(os.path.join(extract_dir, "boost"), os.path.join(DEPS_DIR, "install", f"boost-{BOOST_VERSION}", "boost"))
        logger.info(f"\rInstalled {name}     \n")

    if "diskcleanup" in flags:
        shutil.rmtree(build_dir, ignore_errors=True)

cecho("Collecting dependencies:", GREEN)

# Set compiler flags for 32bit builds on 64bit system
# TODO: This is untested

ADDITIONAL_ARGS = []

if platform.system() == "Darwin":
    ADDITIONAL_ARGS = [f"-mmacosx-version-min={TOOLSET}"] + ADDITIONAL_ARGS

if "wasm" in flags:
    ADDITIONAL_ARGS.extend(("-sWASM_BIGINT", "-fexceptions"))

# If the linker supports GC sections, set it up to reduce binary file size
# -fPIC is required for the shared libraries to work

compiler_flags = "CFLAGS", "CXXFLAGS", "LDFLAGS"

CXXFLAGS = os.environ.get("CXXFLAGS", "")
CFLAGS = os.environ.get("CFLAGS", "")
LDFLAGS = os.environ.get("LDFLAGS", "")

ADDITIONAL_ARGS_STR = " ".join(ADDITIONAL_ARGS)
if "wasm" not in flags and sp.call([bash, "-c", "ld --gc-sections 2>&1 | grep -- --gc-sections &> /dev/null"]) != 0:
    CXXFLAGS_MINIMAL = f"{CXXFLAGS} {PIC} {ADDITIONAL_ARGS_STR}"
    CFLAGS_MINIMAL = f"{CFLAGS} {PIC} {ADDITIONAL_ARGS_STR}"
    if BUILD_STATIC:
        CXXFLAGS = f"{CXXFLAGS} {PIC} -fdata-sections -ffunction-sections -fvisibility=hidden -fvisibility-inlines-hidden {ADDITIONAL_ARGS_STR}"
        CFLAGS = f"{CFLAGS}   {PIC} -fdata-sections -ffunction-sections -fvisibility=hidden {ADDITIONAL_ARGS_STR}"
    else:
        CXXFLAGS = CXXFLAGS_MINIMAL
        CFLAGS = CFLAGS_MINIMAL
    LDFLAGS = f"{LDFLAGS}  -Wl,--gc-sections {ADDITIONAL_ARGS_STR}"
else:
    CXXFLAGS_MINIMAL = f"{CXXFLAGS} {PIC} {ADDITIONAL_ARGS_STR}"
    CFLAGS_MINIMAL = f"{CFLAGS}   {PIC} {ADDITIONAL_ARGS_STR}"
    if BUILD_STATIC:
        CXXFLAGS = f"{CXXFLAGS} {PIC} -fvisibility=hidden -fvisibility-inlines-hidden {ADDITIONAL_ARGS_STR}"
        CFLAGS = f"{CFLAGS}   {PIC} -fvisibility=hidden -fvisibility-inlines-hidden {ADDITIONAL_ARGS_STR}"
    else:
        CXXFLAGS=CXXFLAGS_MINIMAL
        CFLAGS=CFLAGS_MINIMAL
    LDFLAGS = f"{LDFLAGS} {ADDITIONAL_ARGS_STR}"

if "lto" in flags:
    for f in compiler_flags:
        locals()[f] += f" -flto={IFCOS_NUM_BUILD_PROCS}"

os.environ["CXXFLAGS"] = CXXFLAGS
os.environ["CFLAGS"] = CFLAGS
os.environ["LDFLAGS"] = LDFLAGS

# Some dependencies need a more recent CMake version than most distros provide
# @tfk: this is no longer needed
# build_dependency(name="cmake-%s" % (CMAKE_VERSION,), mode="autoconf", build_tool_args=[], download_url="https://cmake.org/files/v%s" % (CMAKE_VERSION_2,), download_name="cmake-%s.tar.gz" % (CMAKE_VERSION,))

if 'hdf5' in targets:
    # not supported
    orig = [os.environ[f] for f in compiler_flags]
    for f in compiler_flags:
        os.environ[f] = re.sub(r"-flto(=\w+)?", "", os.environ[f])

    HDF5_MAJOR = ".".join(HDF5_VERSION.split(".")[:-1])
    build_dependency(
        name=f"hdf5-{HDF5_VERSION}",
        mode="ctest",
        build_tool_args=[],
        download_url=f"https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-{HDF5_MAJOR}/hdf5-{HDF5_VERSION}/src/",
        download_name=f"CMake-hdf5-{HDF5_VERSION}.tar.gz",
        ctest_result=f"HDF5-{HDF5_VERSION}-{platform.system()}",
        ctest_result_path=f"HDF_Group/HDF5/{HDF5_VERSION}"
    )
    
    for f, o in zip(compiler_flags, orig):
        os.environ[f] = o
    

if "json" in targets:
    json_url = f"https://github.com/nlohmann/json/releases/download/{JSON_VERSION}/json.hpp"
    json_install_path = f"{DEPS_DIR}/install/json/nlohmann/json.hpp"
    if not os.path.exists(os.path.dirname(json_install_path)):
        os.makedirs(os.path.dirname(json_install_path))
    if not os.path.exists(json_install_path):
        urlretrieve(json_url, json_install_path)
        
if "eigen" in targets:
    git_clone_or_pull_repository("https://gitlab.com/libeigen/eigen.git", f"{DEPS_DIR}/install/eigen-3.3.9", revision="3.3.9")

if "pcre" in targets:
    build_dependency(
        name=f"pcre-{PCRE_VERSION}",
        mode="autoconf",
        build_tool_args=[DISABLE_FLAG],
        download_url=f"https://downloads.sourceforge.net/project/pcre/pcre/{PCRE_VERSION}/",
        download_name=f"pcre-{PCRE_VERSION}.tar.bz2"
    )

# An issue exists with swig-1.3 and python >= 3.2
# Therefore, build a recent copy from source
if "swig" in targets:
    build_dependency(
        name="swig",
        mode="autoconf",
        build_tool_args=["--disable-ccache", f"--with-pcre-prefix={DEPS_DIR}/install/pcre-{PCRE_VERSION}"],
        download_url="https://github.com/swig/swig.git",
        download_name="swig",
        download_tool=download_tool_git,
        revision=f"rel-{SWIG_VERSION}"
    )
    
if "freetype" in targets:
    build_dependency(
        name=f"freetype",
        mode="cmake",
        build_tool_args=[
            f"-DCMAKE_INSTALL_PREFIX={DEPS_DIR}/install/freetype"
        ],
        download_url = "https://github.com/freetype/freetype",
        download_name = "freetype2",
        download_tool=download_tool_git,
        revision="VER-2-11-1"
    )

if USE_OCCT and "occ" in targets:
    patches = []
    if OCCT_VERSION < "7.4":
        patches.append("./patches/occt/enable-exception-handling.patch")
        
    if OCCT_VERSION == "7.7.1":
        patches.append("./patches/occt/no_ExpToCasExe.patch")
    
    if OCCT_VERSION == "7.7.2":
        patches.append("./patches/occt/no_ExpToCasExe_7_7_2.patch")

    if OCCT_VERSION == "7.8.1":
        patches.append("./patches/occt/no_ExpToCasExe_7_8_1.patch")
    
    if "wasm" in flags:
        patches.append("./patches/occt/no_em_js.patch")

    build_dependency(
        name=f"occt-{OCCT_VERSION}",
        mode="cmake",
        build_tool_args=[
            f"-DINSTALL_DIR={DEPS_DIR}/install/occt-{OCCT_VERSION}",
            f"-DBUILD_LIBRARY_TYPE={LINK_TYPE_UCFIRST}",
            "-DBUILD_MODULE_Draw=0",
            "-DBUILD_RELEASE_DISABLE_EXCEPTIONS=Off",
            f"-D3RDPARTY_FREETYPE_DIR={DEPS_DIR}/install/freetype"
        ],
        download_url = "https://github.com/Open-Cascade-SAS/OCCT",
        download_name = "occt",
        download_tool=download_tool_git,
        patch=patches,
        revision="V" + OCCT_VERSION.replace('.', '_')
    )
elif "occ" in targets:
    build_dependency(
        name=f"oce-{OCE_VERSION}",
        mode="cmake",
        build_tool_args=[
            "-DOCE_DISABLE_TKSERVICE_FONT=ON",
            "-DOCE_TESTING=OFF",
            "-DOCE_BUILD_SHARED_LIB=OFF",
            "-DOCE_DISABLE_X11=ON",
            "-DOCE_VISUALISATION=OFF",
            "-DOCE_OCAF=OFF",
            f"-DOCE_INSTALL_PREFIX={DEPS_DIR}/install/oce-{OCE_VERSION}"
        ],
        download_url="https://github.com/tpaviot/oce/archive/",
        download_name=f"OCE-{OCE_VERSION}.tar.gz"
    )
        
if "libxml2" in targets:
    build_dependency(
        f"libxml2-{LIBXML2_VERSION}",
        "autoconf",
        build_tool_args=[
            "--without-python",
            ENABLE_FLAG,
            DISABLE_FLAG,
            "--without-zlib",
            "--without-iconv",
            "--without-lzma"
        ],
        download_url="ftp://xmlsoft.org/libxml2/",
        download_name=f"libxml2-{LIBXML2_VERSION}.tar.gz"
    )
    
if "OpenCOLLADA" in targets:
    patches = ["./patches/opencollada/pr622_and_disable_subdirs.patch"]

    if "wasm" in flags:
        # This is necessary for the WASM build, because recent versions of
        # clang don't have the tr1:: namespace anymore. However, it breaks
        # some versions of gcc (9.4.0 at least) due to specializing std::hash
        # outside of the std:: namespace.
        patches.append("./patches/opencollada/remove_tr1.patch")

    build_dependency(
        "OpenCOLLADA",
        "cmake",
        build_tool_args=[
            f"-DLIBXML2_INCLUDE_DIR={DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/include/libxml2",
            f"-DLIBXML2_LIBRARIES={DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/lib/libxml2.{LIBRARY_EXT}",
            f"-DPCRE_INCLUDE_DIR={DEPS_DIR}/install/pcre-{PCRE_VERSION}/include",
            f"-DPCRE_PCREPOSIX_LIBRARY={DEPS_DIR}/install/pcre-{PCRE_VERSION}/lib/libpcreposix.{LIBRARY_EXT}",
            f"-DPCRE_PCRE_LIBRARY={DEPS_DIR}/install/pcre-{PCRE_VERSION}/lib/libpcre.{LIBRARY_EXT}",
            f"-DCMAKE_INSTALL_PREFIX={DEPS_DIR}/install/OpenCOLLADA/"
        ],
        download_url="https://github.com/KhronosGroup/OpenCOLLADA.git",
        download_name="OpenCOLLADA",
        download_tool=download_tool_git,
        patch=patches,
        revision=OPENCOLLADA_VERSION
    )

if "python" in targets and not USE_CURRENT_PYTHON_VERSION and "wasm" not in flags:
    # Python should not be built with -fvisibility=hidden, from experience that introduces segfaults
    OLD_CXX_FLAGS = os.environ["CXXFLAGS"]
    OLD_C_FLAGS = os.environ["CFLAGS"]
    os.environ["CXXFLAGS"] = CXXFLAGS_MINIMAL
    os.environ["CFLAGS"] = CFLAGS_MINIMAL

    # On OSX a dynamic python library is built or it would not be compatible
    # with the system python because of some threading initialization
    PYTHON_CONFIGURE_ARGS = []
    if platform.system() == "Darwin":
        PYTHON_CONFIGURE_ARGS = ["--enable-shared"]

    for PYTHON_VERSION in PYTHON_VERSIONS:
        try:
            build_dependency(
                f"python-{PYTHON_VERSION}",
                "autoconf",
                PYTHON_CONFIGURE_ARGS,
                f"http://www.python.org/ftp/python/{PYTHON_VERSION}/",
                f"Python-{PYTHON_VERSION}.tgz"
            )
        except RuntimeError as e:
            # Sometimes setting up modules such as pip/lzma can cause
            # the python installer script to return a non zero exit
            # code where actually the headers and dynamic libraries
            # are installed correctly. This is all we need so we catch
            # the exception and only reraise if a partially successful
            # install is not detected.
            if not os.path.exists(
                os.path.join(DEPS_DIR, "install", f"python-{PYTHON_VERSION}")
            ):
                raise e

    os.environ["CXXFLAGS"] = OLD_CXX_FLAGS
    os.environ["CFLAGS"] = OLD_C_FLAGS

if "boost" in targets:
    str_concat = lambda prefix: lambda postfix: "" if postfix.strip() == "" else "=".join((prefix, postfix.strip()))
    toolset = []
    if "wasm" in flags:
        toolset.append("toolset=emscripten")
    build_dependency(
        f"boost-{BOOST_VERSION}",
        mode="bjam",
        build_tool_args=[
            f"--stagedir={DEPS_DIR}/install/boost-{BOOST_VERSION}",
            "--with-system",
            "--with-program_options",
            "--with-regex",
            "--with-thread",
            "--with-date_time",
            "--with-iostreams",
            "--with-filesystem",
            f"link={LINK_TYPE}",
            *toolset,
            *map(str_concat("cxxflags"), CXXFLAGS.strip().split(' ')),
            *map(str_concat("linkflags"), LDFLAGS.strip().split(' ')),
            "stage", "-s", "NO_BZIP2=1"],
        download_url=BOOST_LOCATION,
        # don't remember what this is, but fail on 1.86
        # patch="./patches/boost/boostorg_regex_62.patch",
        download_name=f"boost_{BOOST_VERSION_UNDERSCORE}.tar.bz2"
    )
    if "wasm" in flags:
        # only supported on nix for now
        run(("find", ".", "-name", "*.bc", "-exec", "bash", "-c", "emar q ${1%.bc}.a $1", "bash", "{}", ";"), cwd=f"{DEPS_DIR}/install/boost-{BOOST_VERSION}/lib")
    
if "cgal" in targets:
    gmp_args = []
    mpfr_args = []
    if "wasm" in flags:
        gmp_args.extend(("--disable-assembly", "--host", "none", "--enable-cxx"))
        mpfr_args.extend(("--host", "none"))

    build_dependency(
        name=f"gmp-{GMP_VERSION}",
        mode="autoconf",
        build_tool_args=[ENABLE_FLAG, DISABLE_FLAG, "--with-pic", *gmp_args],
        download_url="https://ftp.gnu.org/gnu/gmp/",
        download_name=f"gmp-{GMP_VERSION}.tar.bz2"
    )
    
    build_dependency(
        name=f"mpfr-{MPFR_VERSION}",
        mode="autoconf",
        build_tool_args=[ENABLE_FLAG, DISABLE_FLAG, *mpfr_args, f"--with-gmp={DEPS_DIR}/install/gmp-{GMP_VERSION}"],
        download_url=f"http://www.mpfr.org/mpfr-{MPFR_VERSION}/",
        download_name=f"mpfr-{MPFR_VERSION}.tar.bz2"
    )
    
    build_dependency(
        name=f"cgal-{CGAL_VERSION}",
        mode="cmake",
        build_tool_args=[
            f"-DGMP_LIBRARIES={DEPS_DIR}/install/gmp-{GMP_VERSION}/lib/libgmp.{LIBRARY_EXT}",
            f"-DGMP_INCLUDE_DIR={DEPS_DIR}/install/gmp-{GMP_VERSION}/include",
            f"-DMPFR_LIBRARIES={DEPS_DIR}/install/mpfr-{MPFR_VERSION}/lib/libmpfr.{LIBRARY_EXT}" ,
            f"-DMPFR_INCLUDE_DIR={DEPS_DIR}/install/mpfr-{MPFR_VERSION}/include",
            f"-DBoost_INCLUDE_DIR={DEPS_DIR}/install/boost-{BOOST_VERSION}",
            f"-DCMAKE_INSTALL_PREFIX={DEPS_DIR}/install/cgal-{CGAL_VERSION}/",
            "-DCGAL_HEADER_ONLY=On",            
            "-DBUILD_SHARED_LIBS=Off"
        ],
        download_url="https://github.com/CGAL/cgal.git",
        download_name="cgal",
        download_tool=download_tool_git,
        revision=f"v{CGAL_VERSION}"
    )

if "usd" in targets:
    build_dependency(
        name=f"oneTBB-{TBB_VERSION}",
        mode="cmake",
        build_tool_args=[
            f"-DCMAKE_INSTALL_PREFIX={DEPS_DIR}/install/tbb-{TBB_VERSION}",
            f"-DTBB_TEST=OFF"
        ],
        download_url="https://github.com/oneapi-src/oneTBB",
        download_name="oneTBB",
        download_tool=download_tool_git,
        revision=f"v{TBB_VERSION}"
    )

    build_dependency(
        name=f"usd-{USD_VERSION}",
        mode="cmake",
        build_tool_args=[
            f"-DCMAKE_INSTALL_PREFIX={DEPS_DIR}/install/usd-{USD_VERSION}",
            f"-DBOOST_ROOT={DEPS_DIR}/install/boost-{BOOST_VERSION}",
            f"-DTBB_ROOT_DIR={DEPS_DIR}/install/tbb-{TBB_VERSION}",
            f"-DPXR_ENABLE_PYTHON_SUPPORT=FALSE",
            f"-DPXR_ENABLE_GL_SUPPORT=FALSE",
            f"-DPXR_BUILD_IMAGING=FALSE",
            f"-DPXR_BUILD_TUTORIALS=FALSE",
            f"-DPXR_BUILD_EXAMPLES=FALSE",
            f"-DPXR_BUILD_USD_TOOLS=FALSE",
            f"-DPXR_BUILD_TESTS=FALSE"
        ],
        download_url="https://github.com/PixarAnimationStudios/USD",
        download_name="USD",
        download_tool=download_tool_git,
        revision=f"v{USD_VERSION}"
    )

cecho("Building IfcOpenShell:", GREEN)

IFCOS_DIR = os.path.join(DEPS_DIR, "build", "ifcopenshell")
if os.environ.get("NO_CLEAN", "").lower() not in {"1", "on", "true"}:
    if os.path.exists(IFCOS_DIR):
        shutil.rmtree(IFCOS_DIR)
os.makedirs(IFCOS_DIR, exist_ok=True)
executables_dir = os.path.join(IFCOS_DIR, "executables")
os.makedirs(executables_dir, exist_ok=True)


cmake_args = [
    "-DUSE_MMAP="                      "OFF",
    "-DBUILD_EXAMPLES="                "OFF",
    "-DBUILD_SHARED_LIBS="             +OFF_ON[not BUILD_STATIC],
    "-DBOOST_ROOT="                    f"{DEPS_DIR}/install/boost-{BOOST_VERSION}",
    "-DGLTF_SUPPORT="                  "ON",
    "-DJSON_INCLUDE_DIR="              f"{DEPS_DIR}/install/json",
    "-DEIGEN_DIR="                     f"{DEPS_DIR}/install/eigen-3.3.9",
    "-DBoost_NO_BOOST_CMAKE="          "On",
    "-DADD_COMMIT_SHA="              +("On" if ADD_COMMIT_SHA else "Off"),
    "-DVERSION_OVERRIDE="            +("On" if ADD_COMMIT_SHA else "Off")
]

if "wasm" in flags:
    # Boost is built by the build script so should not be found
    # inside of the sysroot set by the emscriptem toolchain
    cmake_args.append("-DWASM_BUILD=On")

if "cgal" in targets:
    cmake_args.extend([
        "-DCGAL_INCLUDE_DIR="          f"{DEPS_DIR}/install/cgal-{CGAL_VERSION}/include",
        "-DGMP_INCLUDE_DIR="           f"{DEPS_DIR}/install/gmp-{GMP_VERSION}/include",
        "-DGMP_LIBRARY_DIR="           f"{DEPS_DIR}/install/gmp-{GMP_VERSION}/lib",
        "-DMPFR_INCLUDE_DIR="          f"{DEPS_DIR}/install/mpfr-{MPFR_VERSION}/include",
        "-DMPFR_LIBRARY_DIR="          f"{DEPS_DIR}/install/mpfr-{MPFR_VERSION}/lib",
    ])

if "occ" in targets and USE_OCCT:
    occ_include_dir =                  f"{DEPS_DIR}/install/occt-{OCCT_VERSION}/include/opencascade"
    occ_library_dir =                  f"{DEPS_DIR}/install/occt-{OCCT_VERSION}/lib"
    cmake_args.extend([
        "-DOCC_INCLUDE_DIR="           +occ_include_dir,
        "-DOCC_LIBRARY_DIR="           +occ_library_dir
    ])

elif "occ" in targets:
    occ_include_dir =                  f"{DEPS_DIR}/install/oce-{OCE_VERSION}/include/oce"
    occ_library_dir =                  f"{DEPS_DIR}/install/oce-{OCE_VERSION}/lib"
    cmake_args.extend([
        "-DOCC_INCLUDE_DIR="           +occ_include_dir,
        "-DOCC_LIBRARY_DIR="           +occ_library_dir
    ])

if "OpenCOLLADA" in targets:
    cmake_args.extend([
        "-DOPENCOLLADA_INCLUDE_DIR="   f"{DEPS_DIR}/install/OpenCOLLADA/include/opencollada",
        "-DOPENCOLLADA_LIBRARY_DIR="   f"{DEPS_DIR}/install/OpenCOLLADA/lib/opencollada"
    ])
else:
    cmake_args.extend([
        "-DCOLLADA_SUPPORT="           "Off",
    ])

if "pcre" in targets:
    cmake_args.append(
        "-DPCRE_LIBRARY_DIR="          f"{DEPS_DIR}/install/pcre-{PCRE_VERSION}/lib"
    )

if "libxml2" in targets:
    cmake_args.extend([
        "-DLIBXML2_INCLUDE_DIR="       f"{DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/include/libxml2",
        "-DLIBXML2_LIBRARIES="         f"{DEPS_DIR}/install/libxml2-{LIBXML2_VERSION}/lib/libxml2.{LIBRARY_EXT}"
    ])

if "hdf5" in targets:
    cmake_args.extend([
        "-DHDF5_INCLUDE_DIR="          f"{DEPS_DIR}/install/hdf5-{HDF5_VERSION}/include",
        "-DHDF5_LIBRARY_DIR="          f"{DEPS_DIR}/install/hdf5-{HDF5_VERSION}/lib"
    ])
else:
    cmake_args.append("-DHDF5_SUPPORT=Off")

if "usd" in targets:
    cmake_args.extend([
        "-DUSD_SUPPORT="               "On",
        "-DUSD_INCLUDE_DIR="           f"{DEPS_DIR}/install/usd-{USD_VERSION}/include",
        "-DUSD_LIBRARY_DIR="           f"{DEPS_DIR}/install/usd-{USD_VERSION}/lib"
    ])

if not explicit_targets or {"IfcGeom", "IfcConvert", "IfcGeomServer"} & set(explicit_targets):
    logger.info("\rConfiguring executables...")

    exec_args = [
        "-DBUILD_IFCGEOM="                 +OFF_ON["IfcGeom" in targets],
        "-DBUILD_GEOMSERVER="              +OFF_ON["IfcGeomServer" in targets],
        "-DBUILD_CONVERT="                 +OFF_ON["IfcConvert" in targets],
        "-DBUILD_IFCPYTHON="               "OFF",
        "-DCMAKE_INSTALL_PREFIX="          f"{DEPS_DIR}/install/ifcopenshell",
    ]
    
    run_cmake("", exec_args + cmake_args, cmake_dir=CMAKE_DIR, cwd=executables_dir)

    logger.info("\rBuilding executables...   ")

    run([make, f"-j{IFCOS_NUM_BUILD_PROCS}"], cwd=executables_dir)
    run([make, "install/strip" if BUILD_CFG == "Release" else "install"], cwd=executables_dir)

if "IfcOpenShell-Python" in targets:
    # On OSX the actual Python library is not linked against.
    ADDITIONAL_ARGS = ""
    if platform.system() == "Darwin":
        ADDITIONAL_ARGS = "-Wl,-flat_namespace,-undefined,suppress"
        
    if "wasm" in flags:
        ADDITIONAL_ARGS = f"-Wl,-undefined,suppress -sSIDE_MODULE=2 -sEXPORTED_FUNCTIONS=_PyInit__ifcopenshell_wrapper"
        
    os.environ["CXXFLAGS"] = f"{CXXFLAGS_MINIMAL} {ADDITIONAL_ARGS}"
    os.environ["CFLAGS"] = f"{CFLAGS_MINIMAL} {ADDITIONAL_ARGS}"
    os.environ["LDFLAGS"] = f"{LDFLAGS} {ADDITIONAL_ARGS}"

    python_dir = os.path.join(IFCOS_DIR, "pythonwrapper")
    os.makedirs(python_dir, exist_ok=True)

    def compile_python_wrapper(python_version, python_library, python_include, python_executable):
        logger.info(f"\rConfiguring python {python_version} wrapper...")

        cache_path = os.path.join(python_dir, "CMakeCache.txt")
        if os.path.exists(cache_path):
            os.remove(cache_path)

        os.environ["PYTHON_LIBRARY_BASENAME"] = os.path.basename(python_library)

        swig_when_built = []
        if "swig" in targets:
            swig_when_built.append(f"-DSWIG_EXECUTABLE={DEPS_DIR}/install/swig/bin/swig")

        run_cmake("",
            cmake_args + [
                "-DPYTHON_LIBRARY="          +python_library,
                *([f"-DPYTHON_EXECUTABLE={python_executable}"] if python_executable else []),
                # *([f"-DPYTHON_MODULE_INSTALL_DIR={os.environ['PYTHONPATH']}/ifcopenshell"] if "wasm" in flags else []),
                *(["-DPYTHON_MODULE_INSTALL_DIR="+os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "package"))] if "wasm" in flags else []),
                "-DPYTHON_INCLUDE_DIR="      +python_include,
                "-DCMAKE_INSTALL_PREFIX="    f"{DEPS_DIR}/install/ifcopenshell/tmp",
                "-DUSERSPACE_PYTHON_PREFIX=" +["Off", "On"][os.environ.get("PYTHON_USER_SITE", "").lower() in {"1", "on", "true"}],
                *swig_when_built],
            cmake_dir=CMAKE_DIR, cwd=python_dir)

        logger.info(f"\rBuilding python {python_version} wrapper...   ")

        run([make, f"-j{IFCOS_NUM_BUILD_PROCS}", "ifcopenshell_wrapper"], cwd=python_dir)
        run([make, "install/local"], cwd=os.path.join(python_dir, "ifcwrap"))

        if python_executable:
            module_dir = os.path.dirname(run([python_executable, "-c", "import inspect, ifcopenshell; print(inspect.getfile(ifcopenshell))"]))

            if platform.system() != "Darwin":
                if BUILD_CFG == "Release":
                    # TODO: This symbol name depends on the Python version?
                    run([strip, "-s", "-K", "PyInit__ifcopenshell_wrapper", glob.glob(os.path.join(module_dir, "_ifcopenshell_wrapper*.so"))[0]], cwd=module_dir)

            return module_dir

    if "wasm" in flags:
        compile_python_wrapper(
            f"{os.environ['PYMAJOR']}.{os.environ['PYMINOR']}.{os.environ['PYMICRO']}",
            f"{os.environ['TARGETINSTALLDIR']}/lib/libpython{os.environ['PYMAJOR']}.{os.environ['PYMINOR']}.a",
            os.environ['PYTHONINCLUDE'],
            None
        )
    
    elif USE_CURRENT_PYTHON_VERSION:
        python_info = sysconfig.get_paths()

        py_path_components = [
            sysconfig.get_config_var('LIBDIR'),
            sysconfig.get_config_var("INSTSONAME")
        ]

        if sysconfig.get_config_var('multiarchsubdir'):
            py_path_components.insert(1, sysconfig.get_config_var('multiarchsubdir').replace("/", ""))

        python_lib = os.path.join(*py_path_components)

        compile_python_wrapper(platform.python_version(), python_lib, python_info["include"], sys.executable)
    else:
        for python_version in PYTHON_VERSIONS:
            python_library = run([bash, "-c", f"ls    {DEPS_DIR}/install/python-{python_version}/lib/libpython*.*"])
            python_include = run([bash, "-c", f"ls -d {DEPS_DIR}/install/python-{python_version}/include/python*"])
            python_executable = os.path.join(DEPS_DIR, "install", f"python-{python_version}", "bin", f"python{python_version[0]}")

            module_dir = compile_python_wrapper(python_version, python_library, python_include, python_executable)
            run([cp, "-R", module_dir, os.path.join(DEPS_DIR, "install", "ifcopenshell", f"python-{python_version}")])

logger.info("\rBuilt IfcOpenShell...\n\n")
