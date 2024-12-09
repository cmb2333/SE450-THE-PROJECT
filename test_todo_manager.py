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
        updated = self.manager.update_task(1, name="Updated Task", priority="High")
        self.manager.update_task(1, completed=True)
        self.assertTrue(updated)
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Updated Task")
        self.assertEqual(task.priority, "High")
        self.assertTrue(task.completed)

    def test_update_task_no_change(self):
        self.manager.add_task("Task 1", "2024-12-31")
        updated = self.manager.update_task(1, name="Task 1")  # No change
        self.assertTrue(updated)
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Task 1")

    def test_delete_invalid_task_id(self):
        self.assertFalse(self.manager.delete_task(-1))
        self.assertFalse(self.manager.delete_task(999))

    def test_update_task_invalid_values(self):
        self.manager.add_task("Task 1", "2024-12-31")
        with self.assertRaises(ValueError):
            self.manager.update_task(1, due_date="INVALID_DATE")

    def test_delete_last_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-30")
        self.manager.delete_task(2)  # Delete last task
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, 1)

    def test_delete_all_tasks(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-30")
        self.manager.delete_task(1)
        self.manager.delete_task(2)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_task_twice(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.delete_task(1)
        deleted_again = self.manager.delete_task(1)  # Try deleting again
        self.assertFalse(deleted_again)

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
    def test_list_tasks_sorting_edge_cases(self):
        self.manager.add_task("Task A", "2024-12-31", "Low")
        self.manager.add_task("Task B", "2024-12-30", "High")
        self.manager.add_task("Task C", "2024-12-29", "Medium")
        tasks = self.manager.list_tasks(sort_by="due_date")
        self.assertEqual(tasks[0].name, "Task C")
        tasks = self.manager.list_tasks(sort_by="priority")
        self.assertEqual(tasks[0].name, "Task B")

    def test_mark_all_completed_no_tasks(self):
        self.manager.mark_all_completed()  # Should handle gracefully
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

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

    def test_archive_completed_tasks_mixed(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        self.manager.update_task(1, completed=True)
        self.manager.archive_completed_tasks()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0].completed)

    # File Handling and Edge Cases
    def test_load_tasks_corrupted_file(self):
        with open("test_tasks.json", "w") as file:
            file.write('{"id": 1, "name": "Task Without Closing Bracket"')
        with self.assertRaises(json.JSONDecodeError):
            self.manager.load_tasks()

    def test_load_tasks_empty_file(self):
        with open("test_tasks.json", "w") as file:
            pass
        self.manager.load_tasks()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_load_tasks_unexpected_json_structure(self):
        with open("test_tasks.json", "w") as file:
            file.write('[{"unexpected_key": "unexpected_value"}]')
        with self.assertRaises(ValueError) as context:
            self.manager.load_tasks()
        self.assertIn("Missing required key in task data", str(context.exception))


if __name__ == "__main__":
    unittest.main()

