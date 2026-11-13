# This file was generated with the assistance of an AI coding tool.

import logging
import sys

import pytest

from ifcclash import ifcclash


class TestSmartGroupClashes:
    def test_missing_scikit_learn_raises_a_clear_error(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "sklearn.cluster", None)
        settings = ifcclash.ClashSettings()
        settings.logger = logging.getLogger("ifcclash-test")
        with pytest.raises(ImportError, match="scikit-learn"):
            ifcclash.Clasher(settings).smart_group_clashes([], 1.0)
