#!/usr/bin/env python3
# This file was generated with the assistance of an AI coding tool.
"""
Unit tests for the consolidated WASM build system under `nix/`.

Covers:
- Lockfile parsing and validation (`nix.core`, `nix/sources.lock.json`)
- SHA-256 hash verification (`nix.core.sha256_file`)
- Profile resolution (`nix.wasm_native.PROFILES` / `get_profile`)
- CMake flag generation (`nix.wasm_native.generate_cmake_flags`)
- Cross-file patch and dependency references
- CLI dispatch (`nix.wasm_native.main`)
- `run()` utility (`nix.core.run`)
- Dependency build configuration (`nix.deps.build_occt` flag wiring)
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

# Make the repo root importable so `from nix import core, deps, wasm_native` works
# whether pytest is invoked from the repo root or from `nix/tests/`.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from nix import core, deps, wasm_native


class TestLockfileParsing(unittest.TestCase):
    """Test lockfile loading and validation."""

    def test_load_lockfile(self):
        """Test that lockfile loads correctly."""
        lock = core.load_lockfile()
        self.assertIsInstance(lock, dict)
        for name in (
            "emsdk",
            "boost",
            "occt",
            "manifold",
            "gmp",
            "mpfr",
            "cgal",
            "eigen",
            "nlohmann_json",
            "libxml2",
            "pcre",
            "opencollada",
            "swig",
            "rocksdb",
            "zstd",
        ):
            self.assertIn(name, lock, f"{name} missing from lockfile")

    def test_lockfile_entry_structure(self):
        """Test that each lockfile entry has required fields."""
        lock = core.load_lockfile()
        for name, entry in lock.items():
            self.assertIn("url", entry, f"{name} missing 'url'")
            self.assertIn("version", entry, f"{name} missing 'version'")
            self.assertIn("archive_type", entry, f"{name} missing 'archive_type'")
            self.assertIn("patches", entry, f"{name} missing 'patches'")
            self.assertIsInstance(
                entry["patches"], list, f"{name} 'patches' should be list"
            )

    def test_lockfile_archive_types(self):
        """Test that archive types are valid."""
        lock = core.load_lockfile()
        valid_types = {"tar.gz", "tar.bz2", "tar.xz", "tar", "zip", "git"}
        for name, entry in lock.items():
            self.assertIn(
                entry["archive_type"],
                valid_types,
                f"{name} has invalid archive_type: {entry['archive_type']}",
            )

    def test_lockfile_urls(self):
        """Test that URLs are well-formed."""
        lock = core.load_lockfile()
        for name, entry in lock.items():
            url = entry["url"]
            if entry["archive_type"] != "git":
                self.assertTrue(
                    url.startswith("http://") or url.startswith("https://"),
                    f"{name} URL should start with http:// or https://: {url}",
                )
            else:
                self.assertTrue(
                    url.startswith("https://"),
                    f"{name} git URL should start with https://: {url}",
                )

    def test_lockfile_patches_reference_existing_files(self):
        """Every patch referenced in the lockfile must exist under nix/patches/."""
        lock = core.load_lockfile()
        for name, entry in lock.items():
            for patch_rel in entry.get("patches", []):
                patch_path = core.PATCHES_DIR / patch_rel
                self.assertTrue(
                    patch_path.exists(),
                    f"{name} references missing patch: {patch_path}",
                )


class TestHashVerification(unittest.TestCase):
    """Test SHA-256 hash verification."""

    def test_sha256_file_handles_multiple_chunks(self):
        content = b"x" * ((1 << 20) + 17)
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as stream:
            stream.write(content)
            temp_path = Path(stream.name)
        try:
            self.assertEqual(
                core.sha256_file(temp_path), hashlib.sha256(content).hexdigest()
            )
        finally:
            temp_path.unlink()

    def test_fetch_sources_rejects_unknown_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(KeyError, "missing from the lockfile"):
                core.fetch_sources({}, ["unknown"], Path(directory))


class TestBuildJobs(unittest.TestCase):
    def test_default_is_capped(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("os.cpu_count", return_value=64),
        ):
            self.assertEqual(core.build_jobs(), 8)

    def test_environment_override_is_validated(self):
        with patch.dict(os.environ, {"WASM_NATIVE_JOBS": "3"}):
            self.assertEqual(core.build_jobs(), 3)
        with patch.dict(os.environ, {"WASM_NATIVE_JOBS": "0"}):
            with self.assertRaisesRegex(ValueError, "positive integer"):
                core.build_jobs()


class TestProfileResolution(unittest.TestCase):
    """Test profile loading and resolution from wasm_native."""

    def test_get_profile_valid(self):
        """Test getting a valid profile."""
        profile = wasm_native.get_profile("minimal")
        self.assertIsInstance(profile, dict)
        self.assertIn("dependencies", profile)
        self.assertIn("cmake_flags", profile)
        self.assertIn("plugins", profile)

    def test_get_profile_invalid(self):
        """Test getting an invalid profile raises error."""
        with self.assertRaises(ValueError) as ctx:
            wasm_native.get_profile("nonexistent")
        self.assertIn("nonexistent", str(ctx.exception))

    def test_profile_dependencies_subset_of_lockfile(self):
        """All profile dependencies must exist in lockfile."""
        lock = core.load_lockfile()
        for name, profile in wasm_native.PROFILES.items():
            for dep in profile["dependencies"]:
                self.assertIn(
                    dep,
                    lock,
                    f"Profile '{name}' references dependency '{dep}' not in lockfile",
                )

    def test_profile_manifests_cover_every_plugin_kind(self):
        for name, profile in wasm_native.PROFILES.items():
            with self.subTest(profile=name):
                self.assertEqual(set(profile["plugins"]), wasm_native._PLUGIN_KINDS)

    def test_manifest_contract_rejects_unexpected_plugins(self):
        profile = wasm_native.get_profile("minimal")
        manifest = {
            kind: {plugin_id: {} for plugin_id in profile["plugins"][kind]}
            for kind in wasm_native._PLUGIN_KINDS
        }
        manifest["kernel"]["opencascade"] = {}
        self.assertEqual(
            wasm_native._profile_manifest_errors(profile, manifest),
            ["Unexpected kernel plugin: opencascade"],
        )


class TestCMakeFlagGeneration(unittest.TestCase):
    """Test CMake flag generation."""

    def test_generate_cmake_flags_base(self):
        """Test base CMake flags are present."""
        with patch("nix.wasm_native.prefix_dir") as mock_prefix:
            mock_prefix.return_value = Path("unused-prefix")
            flags = wasm_native.generate_cmake_flags("minimal")

        flag_str = " ".join(flags)
        for expected in (
            "-DWASM_BUILD=ON",
            "-DBUILD_IFCAPI=ON",
            "-DBUILD_IFCGEOM=ON",
            "-DBUILD_IFCPYTHON=OFF",
            "-DBUILD_CONVERT=OFF",
            "-DBUILD_GEOMSERVER=OFF",
            "-DBUILD_EXAMPLES=OFF",
            "-DBUILD_SHARED_LIBS=OFF",
            "-DCOLLADA_SUPPORT=OFF",
            "-DBoost_NO_BOOST_CMAKE=On",
            "-DCMAKE_BUILD_TYPE=MinSizeRel",
        ):
            self.assertIn(expected, flag_str)
        self.assertIn(f"-DPYTHON_EXECUTABLE={sys.executable}", flags)

    def test_generate_cmake_flags_include_each_profile_contract(self):
        with patch("nix.wasm_native.prefix_dir") as mock_prefix:
            mock_prefix.return_value = Path("unused-prefix")
            for profile_name, profile in wasm_native.PROFILES.items():
                flags = wasm_native.generate_cmake_flags(profile_name)
                with self.subTest(profile=profile_name):
                    for name, value in profile["cmake_flags"].items():
                        self.assertIn(f"-D{name}={value}", flags)

    def test_dependency_roots_use_cross_compile_find_modes(self):
        with tempfile.TemporaryDirectory(prefix="wasm prefix ") as directory:
            prefix = Path(directory)
            for dependency in wasm_native.get_profile("minimal")["dependencies"]:
                (prefix / dependency).mkdir()
            with patch("nix.wasm_native.prefix_dir", return_value=prefix):
                flags = wasm_native.generate_cmake_flags("minimal")

        root_flag = next(
            flag for flag in flags if flag.startswith("-DCMAKE_FIND_ROOT_PATH=")
        )
        self.assertIn("wasm prefix ", root_flag)
        self.assertNotIn("-DCMAKE_PREFIX_PATH=//", flags)
        self.assertIn("-DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY", flags)
        self.assertIn("-DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER", flags)


class TestDependencyBuildConfiguration(unittest.TestCase):
    """Test dependency CMake configuration wiring."""

    def test_occt_uses_wasm_exception_flags(self):
        """OCCT must be built with -fwasm-exceptions to match side modules."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src"
            prefix = root / "prefix"
            src.mkdir()

            with (
                patch("nix.core.load_lockfile", return_value={"occt": {"patches": []}}),
                patch("nix.deps._dep_build_dir", return_value=root / "build"),
                patch("nix.core.run") as mock_run,
            ):
                deps.build_occt(src, prefix, {})

        # First call is the emcmake cmake configure step
        cmake_command = mock_run.call_args_list[0].args[0]
        self.assertIn(
            "-DCMAKE_CXX_FLAGS=-fwasm-exceptions -sSUPPORT_LONGJMP=wasm",
            cmake_command,
        )
        self.assertIn("-DBUILD_LIBRARY_TYPE=Static", cmake_command)
        self.assertIn("-DBUILD_MODULE_DETools=OFF", cmake_command)
        self.assertIn("-DCMAKE_BUILD_TYPE=Release", cmake_command)
        self.assertIn("-DCMAKE_C_FLAGS_RELEASE=-Oz -DNDEBUG", cmake_command)
        self.assertIn("-DCMAKE_CXX_FLAGS_RELEASE=-Oz -DNDEBUG", cmake_command)

    def test_set_build_root(self):
        """set_build_root updates BUILD_ROOT for intermediate build dirs."""
        original = deps.BUILD_ROOT
        with tempfile.TemporaryDirectory() as directory:
            try:
                new_root = Path(directory)
                deps.set_build_root(new_root)
                self.assertEqual(deps.BUILD_ROOT, new_root)
                self.assertEqual(
                    deps._dep_build_dir("occt"), new_root / "build" / "occt"
                )
            finally:
                deps.set_build_root(original)


class TestCLIParsing(unittest.TestCase):
    """Test CLI argument parsing."""

    def test_main_resolves_default_to_all(self):
        """main() with explicit 'all' command invokes the all pipeline."""
        with patch("nix.wasm_native.cmd_all", return_value=0) as mock_all:
            rc = wasm_native.main(["all"])
        self.assertEqual(rc, 0)
        mock_all.assert_called_once()


class TestPackageCommand(unittest.TestCase):
    def test_incomplete_build_does_not_replace_existing_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build = root / "build"
            output = root / "dist"
            output.mkdir()
            marker = output / "keep"
            marker.write_text("existing")
            with (
                patch("nix.wasm_native.ifcopenshell_build_dir", return_value=build),
                patch("nix.wasm_native.dist_dir", return_value=output),
            ):
                with self.assertRaisesRegex(FileNotFoundError, "incomplete WASM build"):
                    wasm_native.cmd_package(SimpleNamespace(profile="minimal"))
            self.assertEqual(marker.read_text(), "existing")

    def test_package_is_profile_scoped_and_copies_only_manifest_plugins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build = root / "build"
            wasm = build / "ifcwrap" / "wasm"
            plugins = wasm / "plugins"
            plugins.mkdir(parents=True)
            profile = wasm_native.get_profile("minimal")
            manifest = {
                kind: {
                    plugin_id: {"wasm": f"plugins/{kind}.{plugin_id}.wasm"}
                    for plugin_id in profile["plugins"][kind]
                }
                for kind in wasm_native._PLUGIN_KINDS
                if profile["plugins"][kind]
            }
            for entries in manifest.values():
                for entry in entries.values():
                    (wasm / entry["wasm"]).write_bytes(b"wasm")
            for name in (
                "ifcopenshell_wasm.wasm",
                "ifcopenshell_wasm.mjs",
                "ifcopenshell_wasm.node.mjs",
                "ifcopenshell_api.mjs",
                "ifcopenshell_api.d.ts",
            ):
                (wasm / name).write_text(name)
            (wasm / "ifcopenshell_plugins.json").write_text(json.dumps(manifest))
            (plugins / "stale.wasm").write_bytes(b"stale")

            with (
                patch("nix.wasm_native.ifcopenshell_build_dir", return_value=build),
                patch.object(wasm_native, "BUILD_ROOT", root),
            ):
                wasm_native.cmd_package(SimpleNamespace(profile="minimal"))

            output = root / "dist" / "minimal"
            self.assertTrue((output / "ifcopenshell_wasm.node.mjs").is_file())
            self.assertFalse((output / "plugins" / "stale.wasm").exists())
            metadata = json.loads((output / "ifcopenshell_profile.json").read_text())
            self.assertEqual(metadata["profile"], "minimal")


class TestRunUtility(unittest.TestCase):
    """Test the run() utility in nix.core."""

    def test_run_honors_check(self):
        with self.assertRaises(subprocess.CalledProcessError):
            core.run([sys.executable, "-c", "raise SystemExit(3)"], check=True)
        result = core.run(
            [sys.executable, "-c", "raise SystemExit(3)"], check=False, capture=True
        )
        self.assertNotEqual(result.returncode, 0)

    def test_run_env_merge(self):
        """run() must merge `env` on top of the current environment."""
        result = core.run(
            [
                sys.executable,
                "-c",
                "import os; print(os.environ['WASM_BUILD_TEST_VAR'])",
            ],
            env={"WASM_BUILD_TEST_VAR": "merged-value"},
            capture=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("merged-value", result.stdout)


if __name__ == "__main__":
    unittest.main()
