import argparse
import multiprocessing
from typing import NamedTuple

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element

# W.turn_on_detailed_logging()


class LineworkContexts(NamedTuple):
    body: list[list[int]]
    annotation: list[list[int]]


class Args(NamedTuple):
    ifc_path: str
    drawing_guid: str
    drawing_element_guids: str | None
    output_path: str


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument("ifc_path", help="IFC file to draw.")
    parser.add_argument("drawing_guid", help="GlobalId of the drawing camera.")
    parser.add_argument(
        "drawing_element_guids",
        nargs="?",
        help="Comma-separated GlobalIds of elements to draw (all elements by default).",
    )
    parser.add_argument("output_path", help="SVG file to write.")
    namespace = parser.parse_args()
    return Args(
        ifc_path=namespace.ifc_path,
        drawing_guid=namespace.drawing_guid,
        drawing_element_guids=namespace.drawing_element_guids,
        output_path=namespace.output_path,
    )


ARGS = parse_args()


class Drawer:
    def execute(self):
        ifc: ifcopenshell.file
        ifc = ifcopenshell.open(ARGS.ifc_path)
        self.camera_element = ifc.by_guid(ARGS.drawing_guid)
        # Don't use draw.main() just whilst we're prototyping and experimenting
        # Get all representation contexts to see what we're dealing with.
        target_view = ifcopenshell.util.element.get_psets(self.camera_element)["EPset_Drawing"]["TargetView"]
        contexts = self.get_linework_contexts(ifc, target_view)
        if ARGS.drawing_element_guids:
            drawing_elements = set([ifc.by_guid(g) for g in ARGS.drawing_element_guids.split(",")])
        else:
            drawing_elements = set(ifc.by_type("IfcElement")) - set(ifc.by_type("IfcFeatureElement"))

        self.setup_serialiser(ifc, target_view)

        tree = ifcopenshell.geom.tree()
        tree.enable_face_styles(True)

        self.serialize_contexts_elements(ifc, tree, contexts, "body", drawing_elements, target_view)
        self.serialize_contexts_elements(ifc, tree, contexts, "annotation", drawing_elements, target_view)

        if self.camera_element not in drawing_elements:
            # The camera must always be included, regardless of any include/exclude filters.
            geom_settings = ifcopenshell.geom.settings()
            geom_settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            geom_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)

            # geom_settings.set_deflection_tolerance(0.0001)
            it = ifcopenshell.geom.iterator(geom_settings, ifc, include=[self.camera_element])
            for elem in it:
                self.serialiser.write(elem)

        self.serialiser.finalize()
        results = self.svg_buffer.get_value()
        print("results", results)

        with open(ARGS.output_path, "w") as svg:
            svg.write(results)

    def get_linework_contexts(self, ifc, target_view) -> LineworkContexts:
        plan_body_target_contexts = []
        plan_body_model_contexts = []
        model_body_target_contexts = []
        model_body_model_contexts = []

        plan_annotation_target_contexts = []
        plan_annotation_model_contexts = []
        model_annotation_target_contexts = []
        model_annotation_model_contexts = []

        for rep_context in ifc.by_type("IfcGeometricRepresentationContext"):
            if rep_context.is_a("IfcGeometricRepresentationSubContext"):
                if rep_context.ContextType == "Plan":
                    if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                        if rep_context.TargetView == target_view:
                            plan_body_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            plan_body_model_contexts.append(rep_context.id())
                    elif rep_context.ContextIdentifier == "Annotation":
                        if rep_context.TargetView == target_view:
                            plan_annotation_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            plan_annotation_model_contexts.append(rep_context.id())
                elif rep_context.ContextType == "Model":
                    if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                        if rep_context.TargetView == target_view:
                            model_body_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            model_body_model_contexts.append(rep_context.id())
                    elif rep_context.ContextIdentifier == "Annotation":
                        if rep_context.TargetView == target_view:
                            model_annotation_target_contexts.append(rep_context.id())
                        elif rep_context.TargetView == "MODEL_VIEW":
                            model_annotation_model_contexts.append(rep_context.id())
            elif rep_context.ContextType == "Model":
                # You should never purely assign to a "Model" context, but
                # if you do, this is what we assume your intention is.
                model_body_model_contexts.append(rep_context.id())
                continue

        body_contexts = (
            [
                plan_body_target_contexts,
                plan_body_model_contexts,
                model_body_target_contexts,
                model_body_model_contexts,
            ]
            if target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]
            else [
                model_body_target_contexts,
                model_body_model_contexts,
            ]
        )

        annotation_contexts = (
            [
                plan_annotation_target_contexts,
                plan_annotation_model_contexts,
                model_annotation_target_contexts,
                model_annotation_model_contexts,
            ]
            if target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]
            else [
                model_annotation_target_contexts,
                model_annotation_model_contexts,
            ]
        )

        return LineworkContexts(body_contexts, annotation_contexts)

    def serialize_contexts_elements(
        self,
        ifc,
        tree: ifcopenshell.geom.tree,
        contexts: LineworkContexts,
        context_type,
        drawing_elements,
        target_view,
    ):
        drawing_elements = drawing_elements.copy()
        contexts = getattr(contexts, context_type)
        for context in contexts:
            if not context or not drawing_elements:
                continue
            geom_settings = ifcopenshell.geom.settings()
            geom_settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            geom_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)

            # geom_settings.set_deflection_tolerance(0.0001)
            if ifc.by_id(context[0]).ContextType == "Plan" and "PLAN_VIEW" in target_view:
                geom_settings.set("model-offset", (0.0, 0.0, 0.002 if target_view == "PLAN_VIEW" else -0.002))
            geom_settings.set("context-ids", context)
            it = ifcopenshell.geom.iterator(geom_settings, ifc, multiprocessing.cpu_count(), include=drawing_elements)
            processed = set()
            for elem in it:
                processed.add(ifc.by_id(elem.id))
                self.serialiser.write(elem)
                tree.add_element(elem)
            drawing_elements -= processed

    def setup_serialiser(self, ifc, target_view):
        self.svg_settings = ifcopenshell.geom.settings()
        self.svg_settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        self.svg_settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)

        # self.svg_settings.set_deflection_tolerance(0.0001)
        self.svg_buffer = ifcopenshell.geom.serializers.buffer()
        self.svg_settings.set("svg-without-storeys", True)
        self.svg_settings.set("svg-write-poly", True)
        self.svg_settings.set("svg-poly", True)
        # Objects with more than these edges are rendered as wireframe instead of HLR for optimisation
        self.svg_settings.set("profile-threshold", 10000)
        self.svg_settings.set("svg-xmlns", True)
        self.svg_settings.set("svg-project", True)
        self.svg_settings.set("auto-elevation", False)
        self.svg_settings.set("auto-section", False)
        self.svg_settings.set("print-space-names", False)
        self.svg_settings.set("print-space-areas", False)
        self.svg_settings.set("door-arcs", False)
        self.svg_settings.set("svg-no-css", True)
        self.svg_settings.set("elevation-ref-guid", self.camera_element.GlobalId)
        self.svg_settings.set("scale", "1/50")
        self.svg_settings.set("svg-subtract-before", "always")
        self.svg_settings.set("svg-prefilter", True)  # See #3359
        # self.svg_settings.set("svg-prefilter", False)  # See #3359
        self.svg_settings.set("svg-unify-inputs", True)
        self.svg_settings.set("svg-segment-projection", True)
        if target_view == "REFLECTED_PLAN_VIEW":
            self.svg_settings.set("svg-mirror-y", True)
        self.serialiser = ifcopenshell.geom.serializers.svg(self.svg_buffer, self.svg_settings)
        self.serialiser.setFile(ifc)


Drawer().execute()
