import unittest
import os
import csv
from todo_manager import TodoManager, Task

class TestTodoManager(unittest.TestCase):

    def setUp(self):
        """Set up a fresh TodoManager instance for each test."""
        self.manager = TodoManager(filename="test_tasks.json", archive_filename="test_archive.json")
        self.manager.tasks = []

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists("test_tasks.json"):
            os.remove("test_tasks.json")
        if os.path.exists("test_archive.json"):
            os.remove("test_archive.json")
        if os.path.exists("test_export.csv"):
            os.remove("test_export.csv")

    # Test for adding tasks
    def test_add_task(self):
        self.manager.add_task("Test Task", "2024-12-31", "Medium", "Test Category", None)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Test Task")
        self.assertEqual(tasks[0].priority, "Medium")

    def test_add_multiple_tasks(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-30")
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].name, "Task 1")
        self.assertEqual(tasks[1].name, "Task 2")

    # Test for updating tasks
    def test_update_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        updated = self.manager.update_task(1, name="Updated Task", priority="High", completed=True)
        task = self.manager.get_task(1)
        self.assertTrue(updated)
        self.assertEqual(task.name, "Updated Task")
        self.assertEqual(task.priority, "High")
        self.assertTrue(task.completed)

    def test_update_nonexistent_task(self):
        updated = self.manager.update_task(999, name="Nonexistent Task")
        self.assertFalse(updated)

    # Test for deleting tasks
    def test_delete_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        deleted = self.manager.delete_task(1)
        tasks = self.manager.list_tasks()
        self.assertTrue(deleted)
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent_task(self):
        deleted = self.manager.delete_task(999)
        self.assertFalse(deleted)

    # Test for listing tasks
    def test_list_tasks_sorted(self):
        self.manager.add_task("Task A", "2024-01-01", "Low")
        self.manager.add_task("Task B", "2023-12-31", "High")
        tasks = self.manager.list_tasks(sort_by="priority")
        self.assertEqual(tasks[0].name, "Task B")

    def test_list_tasks_filter_by_category(self):
        self.manager.add_task("Work Task", "2024-01-01", category="Work")
        self.manager.add_task("Personal Task", "2023-12-31", category="Personal")
        tasks = self.manager.list_tasks(filter_by_category="Work")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].category, "Work")

    def test_list_tasks_no_completed(self):
        self.manager.add_task("Completed Task", "2024-01-01")
        self.manager.add_task("Pending Task", "2024-01-01")
        self.manager.update_task(1, completed=True)
        tasks = self.manager.list_tasks(include_completed=False)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Pending Task")

    # Test for overdue tasks
    def test_get_overdue_tasks(self):
        self.manager.add_task("Overdue Task", "2020-12-31")
        self.manager.add_task("Future Task", "2024-12-31")
        overdue_tasks = self.manager.get_overdue_tasks()
        self.assertEqual(len(overdue_tasks), 1)
        self.assertEqual(overdue_tasks[0].name, "Overdue Task")

    # Test for marking all tasks completed
    def test_mark_all_completed(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        self.manager.mark_all_completed()
        tasks = self.manager.list_tasks()
        self.assertTrue(all(task.completed for task in tasks))

    # Test for archiving tasks
    def test_archive_completed_tasks(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        self.manager.update_task(1, completed=True)
        self.manager.archive_completed_tasks()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0].completed)

    def test_archive_completed_tasks_empty(self):
        self.manager.archive_completed_tasks()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    # Test for undoing actions
    def test_undo_add_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.undo_last_action()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_undo_delete_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.delete_task(1)
        self.manager.undo_last_action()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)

    def test_undo_update_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.update_task(1, name="Updated Task")
        self.manager.undo_last_action()
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Task 1")

    # Test for exporting tasks
    def test_export_tasks_to_csv(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.export_tasks_to_csv(filename="test_export.csv")
        with open("test_export.csv", "r") as file:
            lines = file.readlines()
        self.assertEqual(len(lines), 2)

    # Test for recurrence
    def test_recurring_task_daily(self):
        self.manager.add_task("Daily Task", "2024-01-01", recurrence="daily")
        task = self.manager.get_task(1)
        self.assertEqual(task.calculate_next_due_date(), "2024-01-02")

    def test_recurring_task_weekly(self):
        self.manager.add_task("Weekly Task", "2024-01-01", recurrence="weekly")
        task = self.manager.get_task(1)
        self.assertEqual(task.calculate_next_due_date(), "2024-01-08")

    def test_recurring_task_monthly(self):
        self.manager.add_task("Monthly Task", "2024-01-31", recurrence="monthly")
        task = self.manager.get_task(1)
        self.assertTrue(task.calculate_next_due_date().startswith("2024-02"))

    # Test error handling for invalid JSON
    def test_load_invalid_json(self):
        with open("test_tasks.json", "w") as file:
            file.write("INVALID JSON")
        manager = TodoManager(filename="test_tasks.json")
        self.assertEqual(len(manager.list_tasks()), 0)

if __name__ == "__main__":
    unittest.main()
