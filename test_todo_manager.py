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

    # Basic Task Operations
    def test_add_task(self):
        self.manager.add_task("Test Task", "2024-12-31", "Medium", "Test Category", None)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Test Task")
        self.assertEqual(tasks[0].priority, "Medium")

    def test_delete_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        deleted = self.manager.delete_task(1)
        self.assertTrue(deleted)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_update_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        updated = self.manager.update_task(1, name="Updated Task", priority="High", completed=True)
        self.assertTrue(updated)
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Updated Task")
        self.assertEqual(task.priority, "High")
        self.assertTrue(task.completed)

    def test_delete_invalid_task_id(self):
        self.assertFalse(self.manager.delete_task(-1))
        self.assertFalse(self.manager.delete_task(999))

    def test_update_nonexistent_task(self):
        self.assertFalse(self.manager.update_task(999, name="Nonexistent Task"))

    # Undo Operations
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

    def test_undo_bulk_complete(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-30")
        self.manager.mark_all_completed()
        self.manager.undo_last_action()
        tasks = self.manager.list_tasks()
        self.assertTrue(all(not task.completed for task in tasks))

    # Sorting and Filtering
    def test_list_tasks_sort_by_priority(self):
        self.manager.add_task("Task A", "2024-12-31", "Low")
        self.manager.add_task("Task B", "2024-12-30", "High")
        tasks = self.manager.list_tasks(sort_by="priority")
        self.assertEqual(tasks[0].priority, "High")
        self.assertEqual(tasks[1].priority, "Low")

    def test_list_tasks_filter_by_category(self):
        self.manager.add_task("Work Task", "2024-12-31", category="Work")
        self.manager.add_task("Personal Task", "2024-12-30", category="Personal")
        tasks = self.manager.list_tasks(filter_by_category="Work")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].category, "Work")

    def test_list_tasks_no_completed(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        self.manager.update_task(1, completed=True)
        tasks = self.manager.list_tasks(include_completed=False)
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0].completed)

    # Recurring Tasks
    def test_recurring_task_daily(self):
        self.manager.add_task("Daily Task", "2024-01-01", recurrence="daily")
        task = self.manager.get_task(1)
        self.assertEqual(task.calculate_next_due_date(), "2024-01-02")

    def test_recurring_task_monthly(self):
        self.manager.add_task("Monthly Task", "2024-01-31", recurrence="monthly")
        task = self.manager.get_task(1)
        self.assertTrue(task.calculate_next_due_date().startswith("2024-02"))

    def test_recurring_task_edge_cases(self):
        self.manager.add_task("Leap Year Task", "2024-02-28", recurrence="monthly")
        task = self.manager.get_task(1)
        self.assertTrue(task.calculate_next_due_date().startswith("2024-03"))

    # Export and Archive
    def test_export_tasks_to_csv(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2023-12-31", "High", "Work")
        self.manager.update_task(2, completed=True)
        self.manager.export_tasks_to_csv(filename="test_export.csv")
        with open("test_export.csv", "r") as file:
            rows = list(csv.reader(file))
        self.assertEqual(len(rows), 3)  # Header + 2 tasks
        self.assertEqual(rows[1][1], "Task 1")  # Verify task details

    def test_archive_completed_tasks(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        self.manager.update_task(1, completed=True)
        self.manager.archive_completed_tasks()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0].completed)

    # Overdue Tasks
    def test_get_overdue_tasks(self):
        self.manager.add_task("Overdue Task", "2020-12-31")
        self.manager.add_task("Future Task", "2024-12-31")
        overdue_tasks = self.manager.get_overdue_tasks()
        self.assertEqual(len(overdue_tasks), 1)
        self.assertEqual(overdue_tasks[0].name, "Overdue Task")

    # File Handling and Edge Cases
    def test_load_tasks_empty_file(self):
        with open("test_tasks.json", "w") as file:
            file.write("[]")
        self.manager.load_tasks()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_load_tasks_unexpected_json_structure(self):
        with open("test_tasks.json", "w") as file:
            file.write('[{"unexpected_key": "unexpected_value"}]')
        with self.assertRaises(ValueError) as context:
            self.manager.load_tasks()
        self.assertIn("Missing required key in task data", str(context.exception))

    def test_save_tasks_permission_error(self):
        with open("test_tasks.json", "w") as file:
            file.write("")
        os.chmod("test_tasks.json", 0o400)  # Read-only
        with self.assertRaises(PermissionError):
            self.manager.add_task("Test Task", "2024-12-31")
        os.chmod("test_tasks.json", 0o600)  # Restore permissions


if __name__ == "__main__":
    unittest.main()
