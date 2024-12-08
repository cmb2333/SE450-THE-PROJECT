from todo_manager import TodoManager

# Initialize manager
manager = TodoManager()

# Add a task
manager.add_task("Test Task", "2024-12-31", "Medium", "Test Category", None)

# List tasks
tasks = manager.list_tasks()
print("Tasks:", tasks)
