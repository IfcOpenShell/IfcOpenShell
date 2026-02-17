# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


import bpy
from bonsai.bim.module.sequence.data import SequenceData
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING

# ============================================================================
# FILTER CALLBACK FUNCTIONS
# ============================================================================

def get_operator_items(self, context):
    """
    Genera dinámicamente la lista de operadores según el tipo de dato de la columna seleccionada.
    Dynamically generates the operator list based on the data type of the selected column.
    """
    data_type = getattr(self, 'data_type', 'string')

    common_ops = [
        ('EQUALS', "Equals", "The value is exactly the same"),
        ('NOT_EQUALS', "Does not equal", "The value is different"),
        ('EMPTY', "Is empty", "The field has no value"),
        ('NOT_EMPTY', "Is not empty", "The field has a value"),
    ]

    if data_type in ('integer', 'real', 'float'):
        return [
            ('GREATER', "Greater than", ">"),
            ('LESS', "Less than", "<"),
            ('GTE', "Greater or Equal", ">="),
            ('LTE', "Less or Equal", "<="),
        ] + common_ops
    elif data_type == 'date':
        return [
            ('BEFORE', "Before", "Date is earlier than the specified value"),
            ('AFTER', "After", "Date is later than the specified value"),
            ('ON', "On", "Date is exactly the specified value"),
        ] + common_ops
    elif data_type == 'boolean':
        return [
            ('IS_TRUE', "Is True", "Boolean value is True"),
            ('IS_FALSE', "Is False", "Boolean value is False"),
        ] + common_ops
    else:  # string and others
        return [
            ('CONTAINS', "Contains", "Text contains the specified value"),
            ('NOT_CONTAINS', "Does not contain", "Text does not contain the specified value"),
            ('STARTS_WITH', "Starts with", "Text begins with the specified value"),
            ('ENDS_WITH', "Ends with", "Text ends with the specified value"),
        ] + common_ops

def update_filter_column(self, context):
    """
    Callback que se ejecuta al cambiar la columna del filtro.
    Identifica el tipo de dato y resetea los valores para evitar inconsistencias.
    Callback that runs when changing the filter column.
    It identifies the data type and resets the values to avoid inconsistencies.
    """
    try:
        # The identifier is now 'IfcTask.Name||string'. We extract the data type.
        parts = (self.column or "").split('||')
        if len(parts) == 2:
            self.data_type = parts[1]
        else:
            self.data_type = 'string'  # Safe default type

        # Reset all value fields to start from scratch
        self.value_string = ""
        self.value_integer = 0
        self.value_float = 0.0
        self.value_boolean = False
    except Exception as e:
        print(f"Error in update_filter_column: {e}")
        self.data_type = 'string'

def get_all_task_columns_enum(self, context):
    """
    Genera una lista EnumProperty con TODAS las columnas filtrables,
    incluyendo el tipo de dato en el identificador para uso interno.
    Generates an EnumProperty list with ALL filterable columns,
    including the data type in the identifier for internal use.
    """
    if not SequenceData.is_loaded:
        SequenceData.load()

    items = []
    
    # 1. Special columns (manually defined)
    # The format is: "InternalName||data_type", "UI Label", "Description"
    items.append(("Special.OutputsCount||integer", "Outputs 3D", "Number of elements assigned as task outputs."))
    items.append(("Special.VarianceStatus||string", "Variance Status", "Task variance status (Delayed, Ahead, On Time)"))
    items.append(("Special.VarianceDays||integer", "Variance (Days)", "Task variance in days"))

    # 2. IfcTask columns
    for name_type, label, desc in SequenceData.data.get("task_columns_enum", []):
        try:
            name, data_type = name_type.split('/')
            # Reformat to the new standard: "IfcTask.PropertyName||data_type"
            internal_id = f"IfcTask.{name}||{data_type}"
            items.append((internal_id, label, desc))
        except ValueError:
            # If the format is unexpected, use a safe default
            internal_id = f"IfcTask.{name_type}||string"
            items.append((internal_id, label, desc))

    # 3. IfcTaskTime columns  
    for name_type, label, desc in SequenceData.data.get("task_time_columns_enum", []):
        try:
            name, data_type = name_type.split('/')
            # Reformat to the new standard: "IfcTaskTime.PropertyName||data_type"
            internal_id = f"IfcTaskTime.{name}||{data_type}"
            items.append((internal_id, label, desc))
        except ValueError:
            # If the format is unexpected, use a safe default
            internal_id = f"IfcTaskTime.{name_type}||string"
            items.append((internal_id, label, desc))

    # 4. Fallback if no data is available
    if not items:
        items = [("IfcTask.Name||string", "Task Name", "Name of the task")]

    return items

# ============================================================================
# FILTER PROPERTY GROUP CLASSES
# ============================================================================

class TaskFilterRule(PropertyGroup):
    """Define una regla de filtrado con soporte para múltiples tipos de datos."""
    
    is_active: BoolProperty(
        name="Active", 
        default=True, 
        description="Enable or disable this filter rule"
    )

    column: EnumProperty(
        name="Column",
        description="The column to apply the filter on",
        items=get_all_task_columns_enum,
        update=update_filter_column
    )
    
    operator: EnumProperty(
        name="Operator",
        description="The comparison operation to perform",
        items=get_operator_items
    )

    # Data type (automatically set by update_filter_column)
    data_type: StringProperty(
        name="Data Type",
        default="string",
        description="Internal field to store the data type of the selected column"
    )

    # Multiple value fields for different data types
    value_string: StringProperty(
        name="Text Value",
        description="String value for text-based filters"
    )
    
    value_integer: IntProperty(
        name="Integer Value",
        description="Integer value for numeric filters"
    )
    
    value_float: FloatProperty(
        name="Float Value",
        description="Float value for decimal numeric filters",
        precision=2
    )
    
    value_boolean: BoolProperty(
        name="Boolean Value",
        description="Boolean value for true/false filters"
    )
    
    value_date: StringProperty(
        name="Date Value",
        description="Date value in ISO format (YYYY-MM-DD) for date filters"
    )

    # Case sensitivity for string operations
    case_sensitive: BoolProperty(
        name="Case Sensitive",
        description="Whether string comparisons should be case sensitive",
        default=False
    )

    if TYPE_CHECKING:
        is_active: bool
        column: str
        operator: str
        data_type: str
        value_string: str
        value_integer: int
        value_float: float
        value_boolean: bool
        value_date: str
        case_sensitive: bool

class BIMTaskFilterProperties(PropertyGroup):
    """Stores the complete configuration of the filter system."""
    
    rules: CollectionProperty(
        name="Filter Rules",
        type=TaskFilterRule,
    )
    
    active_rule_index: IntProperty(
        name="Active Filter Rule Index",
    )
    
    logic: EnumProperty(
        name="Filter Logic",
        description="How multiple filter rules are combined",
        items=[
            ('AND', "Match All (AND)", "Show tasks that meet ALL active rules"),
            ('OR', "Match Any (OR)", "Show tasks that meet AT LEAST ONE active rule"),
        ],
        default='AND'
    )

    # Quick filter options for common use cases
    show_only_active_tasks: BoolProperty(
        name="Show Only Active Tasks",
        description="Filter to show only tasks that are currently in progress",
        default=False
    )

    show_only_delayed_tasks: BoolProperty(
        name="Show Only Delayed Tasks", 
        description="Filter to show only tasks that are behind schedule",
        default=False
    )

    show_only_tasks_with_outputs: BoolProperty(
        name="Show Only Tasks with 3D Outputs",
        description="Filter to show only tasks that have 3D elements assigned",
        default=False
    )

    # Search functionality
    quick_search: StringProperty(
        name="Quick Search",
        description="Search tasks by name or identification",
        default=""
    )

    search_in_columns: EnumProperty(
        name="Search In",
        description="Which columns to search in for quick search",
        items=[
            ('NAME', "Name", "Search in task names only"),
            ('ID', "Identification", "Search in task identification only"), 
            ('BOTH', "Name & ID", "Search in both name and identification"),
            ('ALL', "All Text Columns", "Search in all text-based columns"),
        ],
        default='BOTH'
    )

    # Filter performance settings
    enable_live_filtering: BoolProperty(
        name="Live Filtering",
        description="Update filter results in real-time as you type",
        default=True
    )

    # Filter result statistics
    total_tasks: IntProperty(
        name="Total Tasks",
        description="Total number of tasks in the schedule",
        default=0
    )

    filtered_tasks: IntProperty(
        name="Filtered Tasks",
        description="Number of tasks after applying filters",
        default=0
    )

    if TYPE_CHECKING:
        rules: bpy.types.bpy_prop_collection_idprop[TaskFilterRule]
        active_rule_index: int
        logic: str
        show_only_active_tasks: bool
        show_only_delayed_tasks: bool
        show_only_tasks_with_outputs: bool
        quick_search: str
        search_in_columns: str
        enable_live_filtering: bool
        total_tasks: int
        filtered_tasks: int

class SavedFilterSet(PropertyGroup):
    """Almacena un conjunto de reglas de filtro con un nombre."""
    
    name: StringProperty(
        name="Set Name",
        description="Name for this saved filter set"
    )
    
    rules: CollectionProperty(
        name="Filter Rules",
        type=TaskFilterRule,
        description="Collection of filter rules in this set"
    )

    # Metadata for saved filter sets
    description: StringProperty(
        name="Description",
        description="Optional description of what this filter set does",
        default=""
    )

    created_date: StringProperty(
        name="Created Date",
        description="Date when this filter set was created",
        default=""
    )

    last_used_date: StringProperty(
        name="Last Used Date", 
        description="Date when this filter set was last used",
        default=""
    )

    use_count: IntProperty(
        name="Use Count",
        description="Number of times this filter set has been applied",
        default=0
    )

    is_favorite: BoolProperty(
        name="Favorite",
        description="Mark this filter set as a favorite for quick access",
        default=False
    )

    if TYPE_CHECKING:
        name: str
        rules: bpy.types.bpy_prop_collection_idprop[TaskFilterRule]
        description: str
        created_date: str
        last_used_date: str
        use_count: int
        is_favorite: bool

# ============================================================================
# FILTER HELPER FUNCTIONS
# ============================================================================

def apply_task_filters(context, task_list, filter_props):
    """
    Apply the configured filters to a list of tasks and return the filtered results.
    
    Args:
        context: Blender context
        task_list: List of task objects to filter
        filter_props: BIMTaskFilterProperties with filter configuration
        
    Returns:
        List of tasks that match the filter criteria
    """
    if not filter_props.rules:
        return task_list
    
    filtered_tasks = []
    
    for task in task_list:
        task_matches = False
        active_rules = [rule for rule in filter_props.rules if rule.is_active]
        
        if not active_rules:
            # No active rules means no filtering
            filtered_tasks.append(task)
            continue
        
        if filter_props.logic == 'AND':
            # All rules must match
            task_matches = all(evaluate_filter_rule(task, rule) for rule in active_rules)
        else:  # OR logic
            # At least one rule must match
            task_matches = any(evaluate_filter_rule(task, rule) for rule in active_rules)
        
        if task_matches:
            filtered_tasks.append(task)
    
    return filtered_tasks

def evaluate_filter_rule(task, rule):
    """
    Evaluate a single filter rule against a task.
    
    Args:
        task: Task object to evaluate
        rule: TaskFilterRule to apply
        
    Returns:
        bool: True if the task matches the rule, False otherwise
    """
    try:
        # Extract column information
        column_parts = rule.column.split('||')
        if len(column_parts) != 2:
            return False
        
        column_path, data_type = column_parts
        
        # Get the actual value from the task
        task_value = get_task_column_value(task, column_path, data_type)
        
        # Get the comparison value from the rule
        if data_type == 'string':
            compare_value = rule.value_string
        elif data_type in ('integer', 'int'):
            compare_value = rule.value_integer
        elif data_type in ('float', 'real'):
            compare_value = rule.value_float
        elif data_type == 'boolean':
            compare_value = rule.value_boolean
        elif data_type == 'date':
            compare_value = rule.value_date
        else:
            compare_value = rule.value_string
        
        # Apply the operator
        return apply_filter_operator(task_value, rule.operator, compare_value, data_type, rule.case_sensitive)
        
    except Exception as e:
        print(f"Error evaluating filter rule: {e}")
        return False

def get_task_column_value(task, column_path, data_type):
    """
    Extract a value from a task based on the column path.
    
    Args:
        task: Task object
        column_path: String like "IfcTask.Name" or "Special.OutputsCount" 
        data_type: Expected data type
        
    Returns:
        The extracted value, converted to the appropriate type
    """
    try:
        if column_path.startswith("Special."):
            # Handle special columns
            special_field = column_path.split('.')[1]
            if special_field == "OutputsCount":
                return getattr(task, 'outputs_count', 0)
            elif special_field == "VarianceStatus":
                return getattr(task, 'variance_status', '')
            elif special_field == "VarianceDays":
                return getattr(task, 'variance_days', 0)
        elif column_path.startswith("IfcTask."):
            # Handle regular IFC task properties
            field_name = column_path.split('.')[1].lower()
            return getattr(task, field_name, None)
        elif column_path.startswith("IfcTaskTime."):
            # Handle task time properties  
            field_name = column_path.split('.')[1].lower()
            # These would typically come from the derived fields
            return getattr(task, f"derived_{field_name}", None)
    except Exception as e:
        print(f"Error getting task column value for {column_path}: {e}")
    
    return None

def apply_filter_operator(task_value, operator, compare_value, data_type, case_sensitive=False):
    """
    Apply a filter operator to compare task_value with compare_value.
    
    Args:
        task_value: Value from the task
        operator: Comparison operator
        compare_value: Value to compare against
        data_type: Type of data being compared
        case_sensitive: Whether string comparisons should be case sensitive
        
    Returns:
        bool: Result of the comparison
    """
    # Handle None/empty values
    if operator == 'EMPTY':
        return task_value is None or task_value == '' or task_value == 0
    elif operator == 'NOT_EMPTY':
        return task_value is not None and task_value != '' and task_value != 0
    
    if task_value is None:
        return False
    
    # String operations
    if data_type == 'string':
        task_str = str(task_value)
        compare_str = str(compare_value)
        
        if not case_sensitive:
            task_str = task_str.lower()
            compare_str = compare_str.lower()
        
        if operator == 'EQUALS':
            return task_str == compare_str
        elif operator == 'NOT_EQUALS':
            return task_str != compare_str
        elif operator == 'CONTAINS':
            return compare_str in task_str
        elif operator == 'NOT_CONTAINS':
            return compare_str not in task_str
        elif operator == 'STARTS_WITH':
            return task_str.startswith(compare_str)
        elif operator == 'ENDS_WITH':
            return task_str.endswith(compare_str)
    
    # Numeric operations
    elif data_type in ('integer', 'int', 'float', 'real'):
        try:
            task_num = float(task_value) if data_type in ('float', 'real') else int(task_value)
            compare_num = float(compare_value) if data_type in ('float', 'real') else int(compare_value)
            
            if operator == 'EQUALS':
                return task_num == compare_num
            elif operator == 'NOT_EQUALS':
                return task_num != compare_num
            elif operator == 'GREATER':
                return task_num > compare_num
            elif operator == 'LESS':
                return task_num < compare_num
            elif operator == 'GTE':
                return task_num >= compare_num
            elif operator == 'LTE':
                return task_num <= compare_num
        except (ValueError, TypeError):
            return False
    
    # Boolean operations
    elif data_type == 'boolean':
        if operator == 'IS_TRUE':
            return bool(task_value) is True
        elif operator == 'IS_FALSE':
            return bool(task_value) is False
        elif operator == 'EQUALS':
            return bool(task_value) == bool(compare_value)
        elif operator == 'NOT_EQUALS':
            return bool(task_value) != bool(compare_value)
    
    # Date operations (would need proper date parsing)
    elif data_type == 'date':
        # This would need proper implementation with date parsing
        # For now, treat as string comparison
        return apply_filter_operator(task_value, operator, compare_value, 'string', case_sensitive)
    
    return False