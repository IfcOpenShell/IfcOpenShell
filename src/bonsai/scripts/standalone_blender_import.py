import ifcopenshell
import ifcopenshell.api
import ifcopenshell.geom
import multiprocessing


class BlenderImporter:
    def __init__(self):
        self.file = ifcopenshell.open("/home/dion/untitled.ifc")
        self.cache_path = "cache.h5"
        self.should_use_cpu_multiprocessing = True
        self.deflection_tolerance = 0.001
        self.angular_tolerance = 0.5

    def execute(self):
        self.created_guids = set()

        self.settings = ifcopenshell.geom.settings()
        self.settings.set("keep-bounding-boxes", True)
        self.settings.set("mesher-linear-deflection", self.deflection_tolerance)
        self.settings.set("mesher-angular-deflection", self.angular_tolerance)
        self.settings_2d = ifcopenshell.geom.settings()
        self.settings_2d.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)

        self.process_element_filter()
        self.process_context_filter()
        self.create_elements(self.elements)

    def process_element_filter(self):
        # Blender users can typically customise a filtered set of elements to import.
        # For simplicity, let's select everything:
        self.elements = set(self.file.by_type("IfcProduct"))

    def process_context_filter(self):
        # Facetation is to accommodate broken Revit files
        # See https://forums.buildingsmart.org/t/suggestions-on-how-to-improve-clarity-of-representation-context-usage-in-documentation/3663/6?u=moult
        self.body_contexts = [
            c.id()
            for c in self.file.by_type("IfcGeometricRepresentationSubContext")
            if c.ContextIdentifier in ["Body", "Facetation"]
        ]
        # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
        self.body_contexts.extend(
            [
                c.id()
                for c in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
                if c.ContextType == "Model"
            ]
        )
        if self.body_contexts:
            self.settings.set("context-ids", self.body_contexts)
        # Annotation is to accommodate broken Revit files
        # See https://github.com/Autodesk/revit-ifc/issues/187
        self.plan_contexts = [
            c.id()
            for c in self.file.by_type("IfcGeometricRepresentationContext")
            if c.ContextType in ["Plan", "Annotation"]
        ]
        if self.plan_contexts:
            self.settings_2d.set("context-ids", self.plan_contexts)

    def create_elements(self, elements):
        # Based on my experience in viewing BIM models, representations are prioritised as follows:
        # 1. 3D Body, 2. 2D Plans, 3. Point clouds, 4. No representation
        # If an element has a representation that doesn't follow 1, 2, or 3, it will not show by default.
        # The user can load them later if they want to view them.
        products = self.create_products(elements)
        elements -= products
        products = self.create_products(elements, is_curve=True)
        elements -= products
        # Creating point clouds and non geometric objects are specific to Blender so no code is shown.
        pass

    def create_products(self, products, is_curve=False):
        results = set()
        if not products:
            return results
        settings = self.settings_2d if is_curve else self.settings
        if self.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(settings, self.file, multiprocessing.cpu_count(), include=products)
        else:
            iterator = ifcopenshell.geom.iterator(settings, self.file, include=products)
        cache = self.get_cache()
        if cache:
            iterator.set_cache(cache)
        valid_file = iterator.initialize()
        if not valid_file:
            return results
        total = 0
        while True:
            total += 1
            if total % 250 == 0:
                print(f"{total} elements processed")
            shape = iterator.get()
            if shape:
                product = self.file.by_id(shape.guid)
                if self.body_contexts:
                    print("Created", product)
                    self.created_guids.add(shape.guid)
                    results.add(product)
                else:
                    if shape.context not in ["Body", "Facetation"] and shape.guid in self.created_guids:
                        # We only load a single context, and we prioritise the Body context. See #1290.
                        pass
                    else:
                        print("Created", product)
                        self.created_guids.add(shape.guid)
                        results.add(product)
            if not iterator.next():
                break
        print("Done creating geometry")
        return results

    def get_cache(self):
        cache_settings = ifcopenshell.geom.settings()
        serializer_settings = ifcopenshell.geom.serializer_settings()
        try:
            return ifcopenshell.geom.serializers.hdf5(self.cache_path, cache_settings, serializer_settings)
        except:
            return


BlenderImporter().execute()
