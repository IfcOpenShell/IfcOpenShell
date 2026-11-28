# This file was generated with the assistance of an AI coding tool.

import ifc4d.csv4d2ifc


def test_csv_without_optional_columns_does_not_crash(tmp_path):
    csv_path = tmp_path / "schedule.csv"
    csv_path.write_text("Hierarchy,Identification,Name\n1,A,Task A\n2,B,Task B\n", encoding="ISO-8859-1")
    subject = ifc4d.csv4d2ifc.Csv2Ifc()
    subject.csv = str(csv_path)
    subject.parse_csv()
    task = subject.tasks[0]
    assert task["Name"] == "Task A"
    assert task["children"][0]["Name"] == "Task B"
    assert task["ScheduleStart"] is None
