def enable_editing_aggregate(aggregator, obj=None):
    aggregator.enable_editing(obj)


def disable_editing_aggregate(aggregator, obj=None):
    aggregator.disable_editing(obj)


def assign_object(ifc, aggregator, collector, relating_obj=None, related_obj=None):
    if not aggregator.can_aggregate(relating_obj, related_obj):
        return
    rel = ifc.run(
        "aggregate.assign_object", product=ifc.get_entity(related_obj), relating_object=ifc.get_entity(relating_obj)
    )
    collector.assign(relating_obj)
    collector.assign(related_obj)
    aggregator.disable_editing(related_obj)
    return rel
