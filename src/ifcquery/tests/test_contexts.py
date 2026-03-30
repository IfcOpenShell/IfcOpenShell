import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit

from ifcquery.contexts import contexts


class TestContexts:
    def test_empty_model(self):
        f = ifcopenshell.api.project.create_file()
        result = contexts(f)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_model_context(self, model):
        import ifcopenshell.api.context

        ifcopenshell.api.context.add_context(model, context_type="Model")
        result = contexts(model)
        assert len(result) == 1
        entry = result[0]
        assert entry["type"] == "IfcGeometricRepresentationContext"
        assert entry["context_type"] == "Model"
        assert "id" in entry
        assert "context_identifier" in entry

    def test_subcontext(self, model):
        import ifcopenshell.api.context

        model_ctx = ifcopenshell.api.context.add_context(model, context_type="Model")
        ifcopenshell.api.context.add_context(
            model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model_ctx,
        )
        result = contexts(model)
        assert len(result) == 2
        subctx = next(e for e in result if e["type"] == "IfcGeometricRepresentationSubContext")
        assert subctx["context_identifier"] == "Body"
        assert subctx["target_view"] == "MODEL_VIEW"
        assert subctx["parent_context_id"] == model_ctx.id()

    def test_ids_are_integers(self, model):
        import ifcopenshell.api.context

        ifcopenshell.api.context.add_context(model, context_type="Model")
        result = contexts(model)
        for entry in result:
            assert isinstance(entry["id"], int)
