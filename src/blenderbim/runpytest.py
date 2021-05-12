"""
Requires pytest installed under blender

Usage: `blender -b -P runpytest.py -- ARGS`
"""

import sys
import pytest

argv = [__file__]

if '--' in sys.argv:
    i = sys.argv.index('--')
    argv += sys.argv[i+1:]

pytest.main(argv)
