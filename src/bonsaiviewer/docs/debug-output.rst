.. This file was generated with the assistance of an AI coding tool.

Capturing debug output
======================

When BonsaiViewer misbehaves — a crash, a black viewport, a hang — the
single most useful thing you can hand off to a developer is a
**stack trace at the point of failure**. This page covers how to capture
one on Linux, macOS, and Windows.

Pre-flight: always run from a terminal
--------------------------------------

GUI launches discard everything BonsaiViewer prints. Double-clicking
``BonsaiViewer`` (or ``open -a`` on macOS, or a Start Menu shortcut on
Windows) hides every ``qWarning``, ``[wgpu] …`` line, and runtime error
message. **Always launch from a terminal first** when something is
wrong:

.. code-block:: bash

   # Linux
   /path/to/BonsaiViewer

   # macOS
   /Applications/BonsaiViewer.app/Contents/MacOS/BonsaiViewer

.. code-block:: bat

   :: Windows
   "C:\path\to\BonsaiViewer.exe"

If the problem reproduces just by running from a terminal, copy the
console output verbatim — it's usually enough on its own. If the
process disappears without printing anything useful, you need a
debugger; pick the section below for your OS.

Linux
-----

GDB is the standard debugger and ships with every distribution.

.. code-block:: bash

   gdb --args /path/to/BonsaiViewer <any args you'd normally pass>
   (gdb) run
   # ... reproduce the crash ...
   (gdb) bt 30           # backtrace of the crashing thread, top 30 frames
   (gdb) thread apply all bt    # all threads, full backtraces

If BonsaiViewer crashed *without* a debugger and you have core dumps
enabled (``ulimit -c unlimited``), open the core file directly:

.. code-block:: bash

   gdb /path/to/BonsaiViewer /path/to/core.<pid>
   (gdb) bt 30

Most distributions hand crashes to ``systemd-coredump``; ``coredumpctl
list`` shows recent dumps and ``coredumpctl debug BonsaiViewer`` jumps
straight into GDB.

For runtime memory errors (use-after-free, buffer overflows) that don't
crash immediately, run under ``valgrind`` or rebuild with ASAN
(``-fsanitize=address``).

macOS
-----

LLDB is bundled with the Xcode Command Line Tools (``xcode-select
--install`` if you don't already have it).

.. code-block:: bash

   lldb -- /Applications/BonsaiViewer.app/Contents/MacOS/BonsaiViewer
   (lldb) run
   # ... reproduce the crash ...
   (lldb) bt 30                  # backtrace of the crashing thread
   (lldb) thread backtrace all   # all threads

macOS also writes automatic crash reports (``.ips`` files since macOS
12) at ``~/Library/Logs/DiagnosticReports/``. ``ls -lt
~/Library/Logs/DiagnosticReports/ | head`` shows the most recent ones.
Open the newest ``BonsaiViewer-*.ips`` in Console.app or any text
editor — the JSON contains a full symbolicated stack.

Obj-C use-after-free aborts (``message sent to deallocated instance
…``) often show up as a vague segfault with NSZombieEnabled disabled.
Re-run with zombies turned on to get the real recipient of the dead
message:

.. code-block:: bash

   NSZombieEnabled=YES lldb -- /Applications/BonsaiViewer.app/Contents/MacOS/BonsaiViewer
   (lldb) run

Windows
-------

There's no preinstalled debugger on Windows; install **WinDbg Preview**
from the Microsoft Store (free) or grab **ProcDump** as a single
standalone ``.exe`` from
https://learn.microsoft.com/en-us/sysinternals/downloads/procdump.

**Live debugging with WinDbg Preview**

1. Install ``WinDbg Preview`` from the Microsoft Store.
2. ``File → Launch executable → Browse`` to ``BonsaiViewer.exe``.
3. Press F5 to start. Reproduce the crash.
4. When WinDbg breaks in, type ``kn30`` in the command bar at the
   bottom — that's the stack trace with frame numbers.

**Post-mortem dump with ProcDump (no install)**

Useful when the crash is hard to reach inside a debugger (e.g. it
happens during a Bonsai-launched child process):

.. code-block:: bat

   procdump -ma -e BonsaiViewer.exe -accepteula

In a second terminal, run ``BonsaiViewer.exe``. When it crashes,
ProcDump writes ``BonsaiViewer.exe_YYMMDD_HHMMSS.dmp`` in the current
directory. Open that ``.dmp`` in WinDbg Preview
(``File → Open dump file``) and type ``kn30``.

**Getting symbolicated frames**

The shipping ``BonsaiViewer.exe`` doesn't include ``.pdb`` symbols. The
stack will show DLL boundaries (which is often enough to narrow a bug
down to ``BonsaiViewer.exe`` vs. ``wgpu_native.dll`` vs.
``KERNELBASE.dll``), but function names will be addresses. To get
symbol names:

1. Find the matching ``BonsaiViewer.pdb`` in the build artifacts of the
   workflow run that produced your ``.exe`` (under "Upload Build
   Logs").
2. Drop it next to ``BonsaiViewer.exe``.
3. Re-launch under WinDbg; it'll pick up the symbols automatically.

For runtime memory errors that don't crash immediately, the
**Application Verifier** (in the Windows SDK) is the closest analogue
to valgrind / ASAN.

What to send the developer
--------------------------

A stack trace alone is usually enough. If the crash is reliable but
needs specific input to trigger, also include:

1. The exact command line you launched with (env vars matter — e.g.
   ``WGPU_PRESENT_MODE=immediate``).
2. The model file (or its publicly-shareable equivalent) that triggers
   the crash, plus the smallest model that *doesn't* trigger it.
3. The terminal output from before the crash (the ``[wgpu …]`` /
   ``Sidecar metadata read: …`` / ``Streamer done: …`` lines tell us
   which subsystem was active when things went south).
4. Your GPU + driver version and OS version. On Linux: ``glxinfo |
   grep "OpenGL renderer"`` and ``uname -r``. On macOS: Apple menu →
   About this Mac. On Windows: ``dxdiag``.
