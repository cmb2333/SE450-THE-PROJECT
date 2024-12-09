import unittest
import os
import json
import csv
from datetime import datetime, timedelta
from todo_manager import Task, TodoManager, CLI

# Trying to cover as many edge cases as possible... 

class TestTask(unittest.TestCase):

    def test_task_creation(self):
        task = Task(1, "Test Task", "2024-12-10", "High", "Work", False, "daily")
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.due_date, "2024-12-10")
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.category, "Work")
        self.assertEqual(task.completed, False)
        self.assertEqual(task.recurrence, "daily")

    def test_task_creation_defaults(self):
        task = Task(2, "Default Task", "2024-12-11")
        self.assertEqual(task.priority, "Medium")
        self.assertEqual(task.category, "General")
        self.assertEqual(task.completed, False)
        self.assertIsNone(task.recurrence)

    def test_to_dict(self):
        task = Task(1, "Test Task", "2024-12-10", "High", "Work", False, "daily")
        expected = {
            "id": 1,
            "name": "Test Task",
            "due_date": "2024-12-10",
            "priority": "High",
            "category": "Work",
            "completed": False,
            "recurrence": "daily",
        }
        self.assertEqual(task.to_dict(), expected)

    def test_from_dict_valid(self):
        data = {
            "id": 1,
            "name": "Test Task",
            "due_date": "2024-12-10",
            "priority": "High",
            "category": "Work",
            "completed": False,
            "recurrence": "daily",
        }
        task = Task.from_dict(data)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.priority, "High")

    def test_from_dict_invalid(self):
        data = {"id": 1, "name": "Test Task"}
        with self.assertRaises(ValueError):
            Task.from_dict(data)

    def test_calculate_next_due_date(self):
        task_daily = Task(1, "Daily Task", "2024-12-09", recurrence="daily")
        task_weekly = Task(2, "Weekly Task", "2024-12-09", recurrence="weekly")
        task_monthly = Task(3, "Monthly Task", "2024-11-30", recurrence="monthly")
        self.assertEqual(task_daily.calculate_next_due_date(), "2024-12-10")
        self.assertEqual(task_weekly.calculate_next_due_date(), "2024-12-16")
        self.assertEqual(task_monthly.calculate_next_due_date(), "2024-12-01")
        task_no_recurrence = Task(4, "No Recurrence Task", "2024-12-09")
        self.assertIsNone(task_no_recurrence.calculate_next_due_date())


class TestTodoManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_file = "test_tasks.json"
        cls.archive_file = "test_archive.json"
        cls.csv_file = "test_tasks.csv"

    def setUp(self):
        # Clean setup for every test
        self._cleanup_files()
        self.manager = TodoManager(filename=self.test_file, archive_filename=self.archive_file)

    def tearDown(self):
        # Clean up after every test
        self._cleanup_files()

    def _cleanup_files(self):
        for file in [self.test_file, self.archive_file, self.csv_file]:
            if os.path.exists(file):
                os.remove(file)

    # Task Management Tests
    def test_add_task(self):
        self.manager.add_task("Task 1", "2024-12-10", "High", "Work", "daily")
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Task 1")
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.recurrence, "daily")

    def test_update_task(self):
        self.manager.add_task("Task 1", "2024-12-10")
        self.manager.update_task(1, name="Updated Task", priority="Low")
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Updated Task")
        self.assertEqual(task.priority, "Low")

    def test_delete_task(self):
        self.manager.add_task("Task 1", "2024-12-10")
        self.assertTrue(self.manager.delete_task(1))
        self.assertIsNone(self.manager.get_task(1))

    def test_mark_all_completed(self):
        self.manager.add_task("Task 1", "2024-12-10")
        self.manager.add_task("Task 2", "2024-12-11")
        self.manager.mark_all_completed()
        self.assertTrue(all(task.completed for task in self.manager.tasks))

    def test_archive_completed_tasks(self):
        self.manager.add_task("Completed Task", "2024-12-10", completed=True)
        self.manager.add_task("Incomplete Task", "2024-12-11")
        self.manager.archive_completed_tasks()
        self.assertEqual(len(self.manager.tasks), 1)
        with open(self.archive_file, "r") as file:
            archived = json.load(file)
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["name"], "Completed Task")

    # Persistence Tests
    def test_load_and_save_tasks(self):
        self.manager.add_task("Persistent Task", "2024-12-10")
        self.manager.save_tasks()
        new_manager = TodoManager(filename=self.test_file, archive_filename=self.archive_file)
        self.assertEqual(len(new_manager.tasks), 1)
        self.assertEqual(new_manager.tasks[0].name, "Persistent Task")

    # Filtering and Sorting
    def test_filter_by_category(self):
        self.manager.add_task("Work Task", "2024-12-10", category="Work")
        self.manager.add_task("Home Task", "2024-12-11", category="Home")
        filtered = self.manager.list_tasks(filter_by_category="Work")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].category, "Work")

    def test_sort_by_priority(self):
        self.manager.add_task("Low Task", "2024-12-10", "Low")
        self.manager.add_task("High Task", "2024-12-11", "High")
        sorted_tasks = self.manager.list_tasks(sort_by="priority")
        self.assertEqual(sorted_tasks[0].priority, "High")

    # Search
    def test_search_tasks(self):
        self.manager.add_task("Buy milk", "2024-12-10")
        results = self.manager.search_tasks("milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Buy milk")

    # Export
    def test_export_to_csv(self):
        self.manager.add_task("CSV Task", "2024-12-10", "High", "Work")
        self.manager.export_tasks_to_csv(filename=self.csv_file)
        with open(self.csv_file, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
        self.assertEqual(len(rows), 2)

    # Undo Last Action
    def test_undo_last_action(self):
        self.manager.add_task("Undo Task", "2024-12-10")
        self.manager.undo_last_action()
        self.assertEqual(len(self.manager.tasks), 0)

    # Overdue Tasks
    def test_get_overdue_tasks(self):
        self.manager.add_task("Overdue Task", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
        self.manager.add_task("Future Task", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        overdue = self.manager.get_overdue_tasks()
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].name, "Overdue Task")


if __name__ == "__main__":
    unittest.main()
