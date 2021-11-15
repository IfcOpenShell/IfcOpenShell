import test.bootstrap
import ifcopenshell.api


class TestEditTextLiteral(test.bootstrap.IFC4):
    def test_run(self):
        text = self.file.createIfcTextLiteralWithExtent()
        ifcopenshell.api.run("drawing.edit_text_literal", self.file, text_literal=text, attributes={
            "Literal": "Literal",
            "Path": "RIGHT",
            "BoxAlignment": "middle",
        })
        assert text.Literal == "Literal"
        assert text.Path == "RIGHT"
        assert text.BoxAlignment == "middle"
