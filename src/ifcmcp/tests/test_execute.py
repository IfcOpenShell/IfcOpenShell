# This file was generated with the assistance of an AI coding tool.
import pytest

from ifcmcp.core import IfcSession, IfcSessionError


@pytest.fixture
def exec_session(model):
    s = IfcSession(allow_execute=True)
    s.model = model
    return s


def walls(session):
    return sorted(w.Name for w in session.model.by_type("IfcWall"))


class TestExecute:
    def test_disabled_by_default(self, loaded_session):
        with pytest.raises(IfcSessionError, match="disabled"):
            loaded_session.ifc_execute("result = 1")

    def test_no_model(self):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            IfcSession(allow_execute=True).ifc_execute("result = 1")

    def test_returns_result(self, exec_session):
        result = exec_session.ifc_execute("result = {'walls': len(model.by_type('IfcWall'))}")
        assert result == {"ok": True, "result": {"walls": 1}, "stdout": ""}

    def test_entities_are_summarised(self, exec_session):
        result = exec_session.ifc_execute("result = model.by_type('IfcWall')")
        assert result["result"][0]["type"] == "IfcWall"
        assert result["result"][0]["name"] == "Wall001"

    def test_print_is_captured(self, exec_session, capsys):
        result = exec_session.ifc_execute("print('hello')")
        assert result["stdout"] == "hello\n"
        assert capsys.readouterr().out == ""

    def test_api_and_util_are_imported(self, exec_session):
        code = (
            "wall = model.by_type('IfcWall')[0]\n"
            "ifcopenshell.api.attribute.edit_attributes(model, product=wall, attributes={'Name': 'Renamed'})\n"
            "result = ifcopenshell.util.element.get_container(wall).Name"
        )
        assert exec_session.ifc_execute(code)["result"] == "Ground Floor"
        assert walls(exec_session) == ["Renamed"]

    def test_error_returns_the_traceback(self, exec_session):
        result = exec_session.ifc_execute("raise ValueError('bad value')")
        assert result["ok"] is False
        assert "ValueError: bad value" in result["error"]
        assert "<ifc_execute>" in result["error"]

    def test_error_rolls_back_every_change(self, exec_session):
        code = (
            "for name in ('A', 'B'):\n"
            "    ifcopenshell.api.root.create_entity(model, ifc_class='IfcWall', name=name)\n"
            "raise RuntimeError('stop')"
        )
        assert exec_session.ifc_execute(code)["ok"] is False
        assert walls(exec_session) == ["Wall001"]

    def test_one_call_is_one_undo_step(self, exec_session):
        code = "for name in ('A', 'B', 'C'):\n    ifcopenshell.api.root.create_entity(model, ifc_class='IfcWall', name=name)"
        assert exec_session.ifc_execute(code)["ok"]
        assert walls(exec_session) == ["A", "B", "C", "Wall001"]
        exec_session.ifc_undo()
        assert walls(exec_session) == ["Wall001"]

    @pytest.mark.parametrize(
        "statement, error",
        [
            ("import sys; sys.exit(3)", "SystemExit: 3"),
            ("raise KeyboardInterrupt", "KeyboardInterrupt"),
            ("raise GeneratorExit", "GeneratorExit"),
        ],
    )
    def test_exits_are_errors_not_exits(self, exec_session, statement, error):
        code = f"ifcopenshell.api.root.create_entity(model, ifc_class='IfcWall', name='A')\n{statement}"
        result = exec_session.ifc_execute(code)
        assert result["ok"] is False
        assert error in result["error"]
        assert walls(exec_session) == ["Wall001"]

    def test_syntax_error(self, exec_session):
        result = exec_session.ifc_execute("result = (")
        assert result["ok"] is False
        assert "SyntaxError" in result["error"]


class TestEmbedded:
    def test_execute_is_off_in_the_embedded_session(self):
        from ifcmcp import embedded

        embedded.call_tool("ifc_new", {})
        result = embedded.call_tool("ifc_execute", {"code": "result = 1"})
        assert result["ok"] is False
        assert "disabled" in result["error"]

    def test_execute_is_not_offered_to_embedded_clients(self):
        from ifcmcp import embedded

        assert "ifc_execute" not in [t["name"] for t in embedded.tools_openai()]
