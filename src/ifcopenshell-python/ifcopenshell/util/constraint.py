# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult, Yassine Oualid <dion@thinkmoult.com>
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
#
#

def get_constraints(product):
    constraints = []
    for rel in product.HasAssociations or []:
        if rel.is_a("IfcRelAssociatesConstraint"):
            constraints.append(rel.RelatingConstraint)
    return constraints

def get_metrics(constraint):
    metrics = []
    for metric in constraint.BenchmarkValues or []:
        metrics.append(metric)
    return metrics

def get_metric_reference(metric, is_deep=True):
    def get_reference_Attribute(ref, path):
        if ref:
            if is_deep:
                if not path:
                    path = ref.AttributeIdentifier
                else:
                    path += ".{}".format(ref.AttributeIdentifier) if ref.AttributeIdentifier else ""
                return get_reference_Attribute(ref.InnerReference, path)
            else:
                return ref.AttributeIdentifier
        return path

    reference = metric.ReferencePath
    return get_reference_Attribute(reference, "")

def get_metric_constraints(resource, attribute):
    metrics = []
    for constraint in get_constraints(resource) or []:
        for metric in get_metrics(constraint) or []:
            if bool(
                get_metric_reference(metric, is_deep=False) == attribute
                or get_metric_reference(metric, is_deep=True) == attribute
            ):
                metrics.append(metric)
    if metrics:
        return metrics
    return None

def is_hard_constraint(metric):
    if metric.ConstraintGrade == "HARD" and metric.Benchmark == "EQUALTO":
        return True

def is_attribute_locked(product, attribute):
    is_locked = False
    metrics = get_metric_constraints(
        product, attribute
    )
    for metric in metrics or []:
        if is_hard_constraint(metric):
            is_locked = True
    return is_locked
