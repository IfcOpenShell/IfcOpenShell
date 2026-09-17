# Conan based build

The aims of this folder is to replace `nix/build-all.py` for Linux/MacOS systems and `win/build-all.py` for Windows system.

The only prerequisite is to have [conan](https://docs.conan.io/2/installation.html) installed.

You can simply invoke `python3 .conan2/build-all-conan.py` which will install `conan` for you.
Otherwise, to invoke conan yourself, see followings sections.

## Linux build

To install dependencies for Linux system, invoke following command:

```
conan install . -pr:h=.conan2/profiles/linux_host -pr:b=.conan2/profiles/linux_host --build=missing -o "*/*:shared=True" -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=True
```

To build IfcOpenShell components:

```
conan build . -pr:h=.conan2/profiles/linux_host -pr:b=.conan2/profiles/linux_host -o "*/*:shared=True"
```

## MacOS build

To install dependencies for MacOS system, invoke following command:

```
conan install . -pr:h=.conan2/profiles/macos_host -pr:b=.conan2/profiles/macos_host --build=missing -o "*/*:shared=True" -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=True
```

To build IfcOpenShell components:

```
conan build . -pr:h=.conan2/profiles/macos_host -pr:b=.conan2/profiles/macos_host -o "*/*:shared=True"
```

## Windows build

To install dependencies for Windows system, invoke following command:

```
conan install . -pr:h=.conan2/profiles/windows_host -pr:b=.conan2/profiles/windows_host --build=missing -o "*/*:shared=True" -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=True
```

To build IfcOpenShell components:

```
conan build . -pr:h=.conan2/profiles/windows_host -pr:b=.conan2/profiles/windows_host -o "*/*:shared=True"
```

## Cross build

It is possible to do cross compilation, for example to target rasberry pi host from a Linux build machine:

```
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
conan install . -pr:h=.conan2/profiles/raspberrypi_host -pr:b=.conan2/profiles/linux_host --build=missing -o "*/*:shared=True" -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=True
conan build . -pr:h=.conan2/profiles/raspberrypi_host -pr:b=.conan2/profiles/linux_host -o "*/*:shared=True"
```

TODO: fix following error on `conan install ...`:

```
opengl/system: RUN: sudo apt-get install -y --no-install-recommends libgl1-mesa-dev:arm64
Lecture des listes de paquets... Fait
Construction de l'arbre des dépendances... Fait
Lecture des informations d'état... Fait      
E: Impossible de trouver le paquet libgl1-mesa-dev:arm64

opengl/system: WARN: Command 'sudo apt-get install -y --no-install-recommends libgl-dev:arm64' failed with exit code 100
opengl/system: WARN: Command 'sudo apt-get install -y --no-install-recommends libgl1-mesa-dev:arm64' failed with exit code 100
ERROR: opengl/system: Error in system_requirements() method, line 36
	apt.install_substitutes(["libgl-dev"], ["libgl1-mesa-dev"], update=True, check=True)
	ConanException: None of the installs for the package substitutes succeeded.
```

or to target Emscripten (FIXME):

```
git clone https://github.com/conan-io/conan-toolchains.git
conan remote add conan-toolchains ./conan-toolchains
conan install . -pr:h=.conan2/profiles/emscripten_host -pr:b=.conan2/profiles/linux_host --build=missing -o "*/*:shared=True" -c tools.system.package_manager:mode=install -c tools.system.package_manager:sudo=True
conan build . -pr:h=.conan2/profiles/emscripten_host -pr:b=.conan2/profiles/linux_host -o "*/*:shared=True"


or more simply:

```
python3 .conan2/build-all-conan.py --host-profile emscripten_host
```

## Misc

At the end, you will have binary like `BonsaiViewer` in `build/Release/bonsaiviewer/BonsaiViewer` without debug symbols and linked to shared libraries located in conan cache `~/.conan2/p/` for external dependencies and in `build/Release/` for IfcOpenShell dependencies.

To have binaries and libraries with debug symbols, add `-s build_type=Debug`.
To have static binaries, remove `-o "*/*:shared=True"` but note that Qt based doesn't run with static build.