from collections import defaultdict


class TableModel:
    """This class represents a table of data"""

    def __init__(self, key_name=None, value_name=None):
        self.rows = defaultdict(list)
        self.key_name = key_name
        self.value_name = value_name

    def add_row(self, related, relating):
        self.rows[related].append(relating)

    def get_count(self):
        return len(self.rows)

    def get_count_distinct_values(self):
        return len(set(item for sublist in self.rows.values() for item in sublist))