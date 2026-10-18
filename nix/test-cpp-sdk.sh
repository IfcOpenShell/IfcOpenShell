#!/bin/bash
# Exercise the delivered archive with only a compiler, CMake, Ninja and unzip.
set -euo pipefail

archive_dir="$(cd "$1" && pwd)"
mapfile -t archives < <(find "$archive_dir" -maxdepth 1 -name '*.zip' -type f)
if [ "${#archives[@]}" -ne 1 ]; then
  echo "Expected one SDK archive in $archive_dir" >&2
  exit 1
fi
archive="${archives[0]}"
(cd "$(dirname "$archive")" && sha256sum --check "$(basename "$archive").sha256")

test_root="$(mktemp -d)/relocated sdk"
mkdir -p "$test_root"
unzip -q "$archive" -d "$test_root"
sdk_root="$(find "$test_root" -mindepth 1 -maxdepth 1 -type d)"
test -s "$sdk_root/README.md"
test -s "$sdk_root/doc/html/index.html"
test -s "$sdk_root/doc/html/output/api/library_root.html"
test ! -d "$sdk_root/doc/html/autoapi"
test ! -d "$sdk_root/doc/html/output/typescript-api"
unset LD_LIBRARY_PATH CMAKE_PREFIX_PATH

cmake --version
c++ --version
cmake -S "$sdk_root/examples" -B "$test_root/examples-build" -G Ninja \
  -DCMAKE_PREFIX_PATH="$sdk_root" -DCMAKE_BUILD_TYPE=Release
cmake --build "$test_root/examples-build" --parallel 2
mkdir "$test_root/run"
cd "$test_root/run"
for binary_dir in "$sdk_root/bin" "$test_root/examples-build"; do
  "$binary_dir/IfcOpenHouse"
  test -s IfcOpenHouse.ifc
  "$binary_dir/IfcParseExamples" IfcOpenHouse.ifc
  "$binary_dir/IfcAdvancedHouse"
  test -s IfcAdvancedHouse.ifc
  "$binary_dir/IfcAlignment"
  test -s FHWA_Bridge_Geometry_Alignment_Example.ifc
  "$binary_dir/IfcSimplifiedAlignment"
  test -s FHWA_Bridge_Geometry_Alignment_Example_Simplified.ifc
  rm -f ./*.ifc
done
"$sdk_root/bin/IfcOpenHouse"
"$sdk_root/bin/IfcConvert" --yes IfcOpenHouse.ifc model.obj
test -s model.obj
echo "SDK archive verified on $(uname -m)."
