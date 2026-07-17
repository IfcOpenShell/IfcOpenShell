<!-- This file was generated with the assistance of an AI coding tool. -->

# pyradiance exec bit: packaging vs runtime — issue #7156

> **Living dev note** for the `fix-7156-chmod-permission-error` branch/PR (#8583). Read
> before working on this feature; append decisions and findings as the PR is refined.
> This is *not* user documentation, at merge it is removed or its durable parts
> promoted to code comments. Follows the `docs/dev-notes/` convention proposed in
> PR #8201 (one living note per unmerged feature branch); no `README.md` exists on
> this branch yet since that convention itself is not merged.

## Problem

Bonsai's `light` module chmod's every bundled pyradiance binary at every `register()`
call, to make sure they're executable. On a read only/systemwide (eg. AUR) install
where the running user does not own the extension directory, that raised
`PermissionError` and disabled the whole addon (#7156).

## Key facts established

- pyradiance's PyPI wheels already ship every `bin/` binary with the exec bit set
  (`0o100755`), verified directly against the actual linux (`manylinux_2_28_x86_64`,
  92 bins) and macOS (`macosx_10_13_x86_64`, 70 bins) wheels the Makefile downloads.
  The bundled artifact is correct at rest.
- The bit is lost later, inside Blender's own wheel installer
  (`_bpy_internal/extensions/wheel_manager.py`, unchanged across 4.5/5.1/5.2), which
  extracts via plain `zipfile.ZipFile.extract()`. That call does not restore unix
  permissions, confirmed empirically (`0o755` in the zip becomes `0o644` on disk after
  extraction). This is the real, original reason the runtime chmod exists at all
  (commit `233b0856af`, issue #5033), and it happens on every officially distributed
  install, not just AUR.
- The AUR crash (#7156) is a second, distinct case: a system pip package (already
  executable, correctly so) living in a read only location that the old code
  unconditionally tried to chmod anyway.
- Existing precedent: `tool.Blender.ensure_bin_in_path` already does the identical
  best effort chmod for the bundled `ifcmerge` binary, for the same Blender
  wheel-extraction reason. This is not a new pattern.

## Design

Two distinct problems need two distinct fixes, not one:

1. **Is the shipped artifact correct?** Yes, already. Added a read only build time
   safeguard (`scripts/check_pyradiance_exec_bits.py`, wired into the Makefile next to
   the existing wheel safeguards) that fails the build if a future pyradiance release
   ever regresses this. This is the packaging time guarantee CyrilWaechter asked for in
   review. Deliberately does **not** mutate/repack the wheel: that would be a
   functional no-op today, would not survive Blender's own extraction anyway, and
   carries real risk (a corrupted wheel breaks radiance for everyone).
2. **Blender still strips the bit on extraction, every time.** `register()` is the
   earliest point Bonsai controls after that lossy step, so a best effort runtime
   restore is unavoidable there, exactly as already accepted for `ifcmerge`. Refactored
   into `ensure_pyradiance_binaries_executable()`, scoped to only ever touch a
   pyradiance we own (already executable installs, eg. AUR, are skipped entirely), and
   broadened from `except PermissionError` to `except OSError` so a read only *mount*
   (`EROFS`) cannot crash registration either, closing the actual "read only
   systemwide installs" case from the issue title that the narrower except clause had
   still missed.

Rejected: moving the fix entirely into the Makefile and dropping the runtime code.
Cyril's review premise (fix it at packaging, not registration) does not fully hold
here, since packaging cannot control what Blender's installer does to the wheel after
packaging. The correct split is packaging owns the artifact invariant, runtime owns
recovery from the one specific mutation Blender performs on every install.

## Test checklist

- [x] Guard script against the real pyradiance wheels (linux + macOS): passes.
- [x] Guard script against a synthetically exec-stripped wheel: fails with all
      offenders listed.
- [x] Guard script against a wheel-less directory: fails cleanly.
- [x] Runtime loop, scratch reproduction: already-exec file skipped, non-exec file
      promoted, `PermissionError`/`OSError` both caught.
- [x] black/ruff clean on both touched Python files.
- [ ] Full Makefile build end to end (needs CI's per-platform venvs and network wheel
      downloads, not run locally).
- [ ] Live in-Blender `register()` call on an actual read only/AUR-style install.
