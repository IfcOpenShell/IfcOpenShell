# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


class Data:
    is_loaded = False
    connections = {}
    boundary_conditions = {}
    connects_structural_members = {}
    members = {}
    structural_activities = {}
    structural_loads = {}
    connects_structural_activities = {}

    load_cases = {}
    load_case_combinations = {}
    load_groups = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.connections = {}
        cls.boundary_conditions = {}
        cls.connects_structural_members = {}
        cls.members = {}
        cls.structural_activities = {}
        cls.structural_loads = {}
        cls.connects_structural_activities = {}

        cls.load_cases = {}
        cls.load_case_combinations = {}
        cls.load_groups = {}

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if not cls._file:
            return
        if product_id:
            product = cls._file.by_id(product_id)
            if product.is_a("IfcStructuralConnection"):
                return cls.load_structural_connection(product_id)
            if product.is_a("IfcStructuralMember"):
                return cls.load_structural_member(product_id)
            # if product.is_a("IfcStructuralAction"):
            #     return cls.load_structural_action(product_id)
        cls.load_structural_load_cases()
        cls.load_structural_load_case_combinations()
        cls.load_structural_load_groups()
        cls.load_structural_activities()
        cls.load_structural_loads()
        cls.load_boundary_conditions()
        cls.is_loaded = True

    @classmethod
    def load_structural_load_cases(cls):
        cls.load_cases = {}

        for case in cls._file.by_type("IfcStructuralLoadCase"):
            data = case.get_info()
            del data["OwnerHistory"]
            is_grouped_by = []
            for rel in case.IsGroupedBy or []:
                is_grouped_by.extend([o.id() for o in rel.RelatedObjects])
            data["IsGroupedBy"] = is_grouped_by
            cls.load_cases[case.id()] = data

    @classmethod
    def load_structural_load_case_combinations(cls):
        cls.load_case_combinations = {}

        for case in cls._file.by_type("IfcStructuralLoadGroup", include_subtypes=False):
            if case.PredefinedType != "LOAD_COMBINATION":
                continue
            data = case.get_info()
            del data["OwnerHistory"]

            is_grouped_by = []
            for load_group in case.IsGroupedBy or []:
                is_grouped_by.append(load_group.id())
            data["IsGroupedBy"] = is_grouped_by

            cls.load_case_combinations[case.id()] = data

    @classmethod
    def load_structural_load_groups(cls):
        cls.load_groups = {}

        for case in cls._file.by_type("IfcStructuralLoadGroup", include_subtypes=False):
            if case.PredefinedType == "LOAD_COMBINATION":
                continue
            data = case.get_info()
            del data["OwnerHistory"]

            is_grouped_by = []
            for rel in case.IsGroupedBy or []:
                is_grouped_by.extend([o.id() for o in rel.RelatedObjects])
            data["IsGroupedBy"] = is_grouped_by

            cls.load_groups[case.id()] = data

    @classmethod
    def load_structural_activities(cls):
        cls.structural_activities = {}
        for activity in cls._file.by_type("IfcStructuralActivity"):
            data = activity.get_info()
            del data["OwnerHistory"]
            del data["ObjectPlacement"]
            del data["Representation"]
            data["AppliedLoad"] = data["AppliedLoad"].id() if data["AppliedLoad"] else None
            data["AssignedToStructuralItem"] = None
            if activity.AssignedToStructuralItem:
                data["AssignedToStructuralItem"] = activity.AssignedToStructuralItem[0].RelatingElement.id()
            cls.structural_activities[activity.id()] = data

    @classmethod
    def load_structural_connection(cls, product_id):
        connection = cls._file.by_id(product_id)
        data = connection.get_info()
        del data["OwnerHistory"]

        data["ObjectPlacement"] = data["ObjectPlacement"].id() if data["ObjectPlacement"] is not None else None
        data["Representation"] = data["Representation"].id() if data["Representation"] is not None else None
        if connection.is_a("IfcStructuralCurveConnection"):
            data["Axis"] = data["Axis"].id() if data["Axis"] is not None else None
        if connection.is_a("IfcStructuralPointConnection"):
            data["ConditionCoordinateSystem"] = (
                data["ConditionCoordinateSystem"].id() if data["ConditionCoordinateSystem"] is not None else None
            )

        data["ConnectsStructuralMembers"] = []

        if connection.AppliedCondition:
            cls.load_boundary_condition(connection.AppliedCondition)
            data["AppliedCondition"] = connection.AppliedCondition.id()

        for rel in connection.ConnectsStructuralMembers or []:
            cls.load_connects_structural_member(rel)
            data["ConnectsStructuralMembers"].append(rel.id())

        cls.connections[connection.id()] = data

    @classmethod
    def load_boundary_condition(cls, boundary_condition):
        data = boundary_condition.get_info()
        for key, value in data.items():
            if not value or key in ["Name", "type", "id"]:
                continue
            data[key] = value.wrappedValue
        cls.boundary_conditions[boundary_condition.id()] = data

    @classmethod
    def load_connects_structural_member(cls, rel):
        rel_data = rel.get_info()
        del rel_data["OwnerHistory"]
        rel_data["RelatingStructuralMember"] = rel.RelatingStructuralMember.id()
        rel_data["RelatedStructuralConnection"] = rel.RelatedStructuralConnection.id()
        rel_data["ConditionCoordinateSystem"] = (
            rel_data["ConditionCoordinateSystem"].id() if rel_data["ConditionCoordinateSystem"] is not None else None
        )  # TODO: consider orientation

        if rel.is_a("IfcRelConnectsWithEccentricity"):
            rel_data["ConnectionConstraint"] = rel.ConnectionConstraint.id()  # TODO

        if rel.AppliedCondition:
            cls.load_boundary_condition(rel.AppliedCondition)
            rel_data["AppliedCondition"] = rel.AppliedCondition.id()

        cls.connects_structural_members[rel.id()] = rel_data

    @classmethod
    def load_structural_loads(cls):
        cls.structural_loads = {}
        for load in cls._file.by_type("IfcStructuralLoad"):
            cls.load_structural_load(load)

    @classmethod
    def load_structural_load(cls, load):
        cls.structural_loads[load.id()] = load.get_info()

    @classmethod
    def load_boundary_conditions(cls):
        cls.boundary_conditions = {}
        for bc in cls._file.by_type("IfcBoundaryCondition"):
            cls.load_boundary_condition(bc)

    @classmethod
    def load_connects_structural_activity(cls, rel):
        rel_data = rel.get_info()
        del rel_data["OwnerHistory"]
        rel_data["RelatingElement"] = rel.RelatingElement.id()
        rel_data["RelatedStructuralActivity"] = rel.RelatedStructuralActivity.id()

        if rel.RelatedStructuralActivity.AppliedLoad:
            cls.load_structural_load(rel.RelatedStructuralActivity.AppliedLoad)
            # rel_data["AppliedCondition"] = rel.RelatedStructuralActivity.AppliedLoad.id()

        cls.connects_structural_activities[rel.id()] = rel_data

    @classmethod
    def load_structural_member(cls, product_id):
        member = cls._file.by_id(product_id)
        data = member.get_info()

        del data["OwnerHistory"]

        data["ObjectPlacement"] = data["ObjectPlacement"].id() if data["ObjectPlacement"] is not None else None
        data["Representation"] = data["Representation"].id() if data["Representation"] is not None else None
        if member.is_a("IfcStructuralCurveMember"):
            data["Axis"] = data["Axis"].id() if data["Axis"] is not None else None

        data["ConnectsStructuralActivities"] = []
        data["ConnectedBy"] = []

        for activity in member.AssignedStructuralActivity or []:
            cls.load_connects_structural_activity(activity)
            data["ConnectsStructuralActivities"].append(activity.id())

        for rel in member.ConnectedBy or []:
            cls.load_connects_structural_member(rel)
            data["ConnectedBy"].append(rel.id())

        cls.members[member.id()] = data
