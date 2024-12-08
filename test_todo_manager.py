import unittest
from todo_manager import TodoManager, Task

class TestTodoManager(unittest.TestCase):

    def setUp(self):
        """Set up a fresh TodoManager instance for each test."""
        self.manager = TodoManager()
        self.manager.tasks = []

    def test_add_task(self):
        self.manager.add_task("Test Task", "2024-12-31", "Medium", "Test Category", None)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Test Task")

    def test_add_task_edge_case(self):
        """Test adding a task with empty fields."""
        self.manager.add_task("", "2024-01-01", "", "", None)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "")

    def test_update_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.update_task(1, name="Updated Task", priority="High")
        task = self.manager.get_task(1)
        self.assertEqual(task.name, "Updated Task")
        self.assertEqual(task.priority, "High")

    def test_update_nonexistent_task(self):
        result = self.manager.update_task(999, name="Nonexistent Task")
        self.assertFalse(result)

    def test_delete_task(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.delete_task(1)
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_delete_nonexistent_task(self):
        result = self.manager.delete_task(999)
        self.assertFalse(result)

    def test_mark_all_completed(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        self.manager.mark_all_completed()
        tasks = self.manager.list_tasks()
        self.assertTrue(all(task.completed for task in tasks))

    def test_archive_completed_tasks(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        
        # Mark the second task as completed
        self.manager.update_task(2, completed=True)

        self.manager.archive_completed_tasks()
        tasks = self.manager.list_tasks()

        # Verify that only one task remains and it is not completed
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0].completed)

    def test_search_tasks(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.add_task("Another Task", "2024-12-31")
        results = self.manager.search_tasks("Task")
        self.assertEqual(len(results), 2)

    def test_search_tasks_no_match(self):
        self.manager.add_task("Task 1", "2024-12-31")
        results = self.manager.search_tasks("Nonexistent")
        self.assertEqual(len(results), 0)

    def test_list_tasks_sorted(self):
        self.manager.add_task("Task A", "2024-01-01", "Low")
        self.manager.add_task("Task B", "2023-12-31", "High")
        tasks = self.manager.list_tasks(sort_by="priority")
        # High priority comes first
        self.assertEqual(tasks[0].name, "Task B")

    def test_undo_last_action(self):
        self.manager.add_task("Task 1", "2024-12-31")
        self.manager.undo_last_action()
        tasks = self.manager.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_undo_last_action_no_history(self):
        result = self.manager.undo_last_action()
        self.assertFalse(result)

    def test_get_overdue_tasks(self):
        self.manager.add_task("Task 1", "2020-12-31")
        self.manager.add_task("Task 2", "2024-12-31")
        overdue_tasks = self.manager.get_overdue_tasks()
        self.assertEqual(len(overdue_tasks), 1)
        self.assertEqual(overdue_tasks[0].name, "Task 1")

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

if __name__ == "__main__":
    unittest.main()


