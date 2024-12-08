import unittest
from todo_manager import TodoManager

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

if __name__ == "__main__":
    unittest.main()

