import blenderbim.core.aggregate as subject
from test.core.bootstrap import ifc, aggregator, collector


class TestEnableEditingAggregate:
    def test_run(self, aggregator):
        aggregator.enable_editing("obj").should_be_called()
        subject.enable_editing_aggregate(aggregator, obj="obj")


class TestDisableEditingAggregate:
    def test_run(self, aggregator):
        aggregator.disable_editing("obj").should_be_called()
        subject.disable_editing_aggregate(aggregator, obj="obj")


class TestAssignObject:
    def test_run(self, ifc, aggregator, collector):
        aggregator.can_aggregate("relating_obj", "related_obj").should_be_called().will_return(True)
        ifc.get_entity("relating_obj").should_be_called().will_return("relating_object")
        ifc.get_entity("related_obj").should_be_called().will_return("related_object")
        ifc.run(
            "aggregate.assign_object", product="related_object", relating_object="relating_object"
        ).should_be_called().will_return("rel")
        aggregator.disable_editing("related_obj").should_be_called()
        collector.assign("relating_obj").should_be_called()
        collector.assign("related_obj").should_be_called()
        assert (
            subject.assign_object(ifc, aggregator, collector, relating_obj="relating_obj", related_obj="related_obj")
            == "rel"
        )
