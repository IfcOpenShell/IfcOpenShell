# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import sys
import json
import pytest
import bonsai.core.tool
from typing import Any, Optional
from typing_extensions import Self


@pytest.fixture
def ifc():
    prophet = Prophecy(bonsai.core.tool.Ifc)
    yield prophet
    prophet.verify()


@pytest.fixture
def blender():
    prophet = Prophecy(bonsai.core.tool.Blender)
    yield prophet
    prophet.verify()


@pytest.fixture
def brick():
    prophet = Prophecy(bonsai.core.tool.Brick)
    yield prophet
    prophet.verify()


@pytest.fixture
def aggregate():
    prophet = Prophecy(bonsai.core.tool.Aggregate)
    yield prophet
    prophet.verify()


@pytest.fixture
def collector():
    prophet = Prophecy(bonsai.core.tool.Collector)
    yield prophet
    prophet.verify()


@pytest.fixture
def context():
    prophet = Prophecy(bonsai.core.tool.Context)
    yield prophet
    prophet.verify()


@pytest.fixture
def debug():
    prophet = Prophecy(bonsai.core.tool.Debug)
    yield prophet
    prophet.verify()


@pytest.fixture
def demo():
    prophet = Prophecy(bonsai.core.tool.Demo)
    yield prophet
    prophet.verify()


@pytest.fixture
def document():
    prophet = Prophecy(bonsai.core.tool.Document)
    yield prophet
    prophet.verify()


@pytest.fixture
def drawing():
    prophet = Prophecy(bonsai.core.tool.Drawing)
    yield prophet
    prophet.verify()


@pytest.fixture
def geometry():
    prophet = Prophecy(bonsai.core.tool.Geometry)
    yield prophet
    prophet.verify()


@pytest.fixture
def georeference():
    prophet = Prophecy(bonsai.core.tool.Georeference)
    yield prophet
    prophet.verify()


@pytest.fixture
def library():
    prophet = Prophecy(bonsai.core.tool.Library)
    yield prophet
    prophet.verify()


@pytest.fixture
def material():
    prophet = Prophecy(bonsai.core.tool.Material)
    yield prophet
    prophet.verify()


@pytest.fixture
def misc():
    prophet = Prophecy(bonsai.core.tool.Misc)
    yield prophet
    prophet.verify()


@pytest.fixture
def nest():
    prophet = Prophecy(bonsai.core.tool.Nest)
    yield prophet
    prophet.verify()


@pytest.fixture
def owner():
    prophet = Prophecy(bonsai.core.tool.Owner)
    yield prophet
    prophet.verify()


@pytest.fixture
def patch():
    prophet = Prophecy(bonsai.core.tool.Patch)
    yield prophet
    prophet.verify()


@pytest.fixture
def project():
    prophet = Prophecy(bonsai.core.tool.Project)
    yield prophet
    prophet.verify()


@pytest.fixture
def pset():
    prophet = Prophecy(bonsai.core.tool.Pset)
    yield prophet
    prophet.verify()


@pytest.fixture
def qto():
    prophet = Prophecy(bonsai.core.tool.Qto)
    yield prophet
    prophet.verify()


@pytest.fixture
def root():
    prophet = Prophecy(bonsai.core.tool.Root)
    yield prophet
    prophet.verify()


@pytest.fixture
def selector():
    prophet = Prophecy(bonsai.core.tool.Selector)
    yield prophet
    prophet.verify()


@pytest.fixture
def sequence():
    prophet = Prophecy(bonsai.core.tool.Sequence)
    yield prophet
    prophet.verify()


@pytest.fixture
def spatial():
    prophet = Prophecy(bonsai.core.tool.Spatial)
    yield prophet
    prophet.verify()


@pytest.fixture
def style():
    prophet = Prophecy(bonsai.core.tool.Style)
    yield prophet
    prophet.verify()


@pytest.fixture
def surveyor():
    prophet = Prophecy(bonsai.core.tool.Surveyor)
    yield prophet
    prophet.verify()


@pytest.fixture
def system():
    prophet = Prophecy(bonsai.core.tool.System)
    yield prophet
    prophet.verify()


@pytest.fixture
def type():
    prophet = Prophecy(bonsai.core.tool.Type)
    yield prophet
    prophet.verify()


@pytest.fixture
def unit():
    prophet = Prophecy(bonsai.core.tool.Unit)
    yield prophet
    prophet.verify()


@pytest.fixture
def voider():
    prophet = Prophecy(bonsai.core.tool.Voider)
    yield prophet
    prophet.verify()


class Prophecy:
    def __init__(self, cls):
        self.subject = cls
        self.predictions: list[dict] = []
        self.calls: list[dict] = []
        self.return_values: dict[str, Any] = {}
        self.should_call: Optional[dict] = None

    def __getattr__(self, attr: str):
        if not hasattr(self.subject, attr):
            raise AttributeError(f"Prophecy {self.subject} has no attribute {attr}")

        def decorate(*args, **kwargs):
            call = {"name": attr, "args": args, "kwargs": kwargs}
            # Ensure that signature is valid
            getattr(self.subject, attr)(*args, **kwargs)
            try:
                key = json.dumps(call, sort_keys=True)
                self.calls.append(call)
                if key in self.return_values:
                    return self.return_values[key]
            except:
                pass
            return self

        return decorate

    def should_be_called(self, number=None):
        self.should_call = self.calls.pop()
        self.predictions.append({"type": "SHOULD_BE_CALLED", "number": number, "call": self.should_call})
        return self

    def will_return(self, value: Any) -> Self:
        key = json.dumps(self.should_call, sort_keys=True)
        self.return_values[key] = value
        return self

    def verify(self) -> None:
        predicted_calls = []
        for prediction in self.predictions:
            predicted_calls.append(prediction["call"])
            if prediction["type"] == "SHOULD_BE_CALLED":
                self.verify_should_be_called(prediction)
        for call in self.calls:
            if call not in predicted_calls:
                raise Exception(f"Unpredicted call: {call}")

    def verify_should_be_called(self, prediction: dict) -> None:
        if prediction["number"]:
            count = self.calls.count(prediction["call"])
            if count != prediction["number"]:
                raise Exception(f"Called {count}: {prediction}")
        else:
            if prediction["call"] not in self.calls:
                error_msg = f"{self.subject} was not called with {prediction['call']['name']}:\n - {prediction}"

                # Print all unprocessed calls if pytest was started in verbose mode.
                if "-v" in sys.argv or "-vv" in sys.argv:
                    if not self.calls:
                        error_msg += "\nNo unprocessed calls."
                    else:
                        error_msg += "\nUnprocessed calls:"
                        for call in self.calls:
                            error_msg += f"\n - {call}"

                raise Exception(error_msg)
