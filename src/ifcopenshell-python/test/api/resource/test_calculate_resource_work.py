import test.bootstrap
import ifcopenshell.api


class TestCalculateResourceWork(test.bootstrap.IFC4):
    def test_calculating_resource_work_based_on_a_daily_productivity_rate(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")

        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=resource, name="EPset_Productivity")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={
            "BaseQuantityConsumed": "P0.5D",
            "BaseQuantityProducedName": "GrossVolume",
            "BaseQuantityProducedValue": 5,
        })

        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=slab, name="Qto_SlabBaseQuantities")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"GrossVolume": 20})

        task = ifcopenshell.api.run("sequence.add_task", self.file)
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=slab, related_object=task)
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("resource.calculate_resource_work", self.file, resource=resource)
        assert resource.Usage.ScheduleWork == "P2.0D"


    def test_calculating_resource_work_based_on_an_hourly_productivity_rate(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")

        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=resource, name="EPset_Productivity")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={
            "BaseQuantityConsumed": "PT1H",
            "BaseQuantityProducedName": "GrossVolume",
            "BaseQuantityProducedValue": 5,
        })

        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=slab, name="Qto_SlabBaseQuantities")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"GrossVolume": 20})

        task = ifcopenshell.api.run("sequence.add_task", self.file)
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=slab, related_object=task)
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("resource.calculate_resource_work", self.file, resource=resource)
        assert resource.Usage.ScheduleWork == "PT4.0H"

    def test_no_calculation_if_no_productivity_data_available(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")

        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")

        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=slab, name="Qto_SlabBaseQuantities")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"GrossVolume": 20})

        task = ifcopenshell.api.run("sequence.add_task", self.file)
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=slab, related_object=task)
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("resource.calculate_resource_work", self.file, resource=resource)

        assert resource.Usage is None

        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=resource, name="EPset_Productivity")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"BaseQuantityProducedName": "foo"})

        ifcopenshell.api.run("resource.calculate_resource_work", self.file, resource=resource)

        assert resource.Usage is None

    def test_calculating_resource_work_based_on_a_counted_quantity(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")

        resource = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class="IfcLaborResource")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=resource, name="EPset_Productivity")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={
            "BaseQuantityConsumed": "PT1H",
            "BaseQuantityProducedName": "Count",
            "BaseQuantityProducedValue": 2,
        })

        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=slab, name="Qto_SlabBaseQuantities")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"GrossVolume": 20})

        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=slab, related_object=resource)

        schedule = ifcopenshell.api.run("sequence.add_work_schedule", self.file)
        task = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=schedule)
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=slab, related_object=task)
        ifcopenshell.api.run("sequence.assign_process", self.file, relating_process=task, related_object=resource)
        ifcopenshell.api.run("resource.calculate_resource_work", self.file, resource=resource)
        assert resource.Usage.ScheduleWork == "PT0.5H"
