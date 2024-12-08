import json
import csv
from datetime import datetime, timedelta


class Task:
    def __init__(self, task_id, name, due_date, priority="Medium", category="General", completed=False, recurrence=None):
        self.task_id = task_id
        self.name = name
        self.due_date = due_date
        self.priority = priority
        self.category = category
        self.completed = completed
        self.recurrence = recurrence  # None, "daily", "weekly", "monthly"

    def to_dict(self):
        return {
            "id": self.task_id,
            "name": self.name,
            "due_date": self.due_date,
            "priority": self.priority,
            "category": self.category,
            "completed": self.completed,
            "recurrence": self.recurrence,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            task_id=data["id"],
            name=data["name"],
            due_date=data["due_date"],
            priority=data["priority"],
            category=data["category"],
            completed=data["completed"],
            recurrence=data["recurrence"],
        )

    def calculate_next_due_date(self):
        if self.recurrence == "daily":
            return (datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        elif self.recurrence == "weekly":
            return (datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(weeks=1)).strftime("%Y-%m-%d")
        elif self.recurrence == "monthly":
            new_date = datetime.strptime(self.due_date, "%Y-%m-%d").replace(day=28) + timedelta(days=4)
            return new_date.replace(day=1).strftime("%Y-%m-%d")
        return None


class TodoManager:
    def __init__(self, filename="tasks.json", archive_filename="archive.json"):
        self.filename = filename
        self.archive_filename = archive_filename
        self.tasks = []
        self.history = []
        self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                self.tasks = [Task.from_dict(task) for task in data]
        except FileNotFoundError:
            self.tasks = []

    def save_tasks(self):
        with open(self.filename, "w") as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    def add_task(self, name, due_date, priority="Medium", category="General", recurrence=None):
        task_id = len(self.tasks) + 1
        task = Task(task_id, name, due_date, priority, category, recurrence=recurrence)
        self.tasks.append(task)
        self.history.append(("add", task))
        self.save_tasks()

    def get_task(self, task_id):
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(self, task_id, name=None, due_date=None, priority=None, category=None, completed=None, recurrence=None):
        task = self.get_task(task_id)
        if task:
            old_task = task.to_dict()
            if name is not None:
                task.name = name
            if due_date is not None:
                task.due_date = due_date
            if priority is not None:
                task.priority = priority
            if category is not None:
                task.category = category
            if completed is not None:
                task.completed = completed
            if recurrence is not None:
                task.recurrence = recurrence
            self.history.append(("update", old_task))
            self.save_tasks()
            return True
        return False

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.history.append(("delete", task))
            self.save_tasks()
            return True
        return False

    def mark_all_completed(self):
        for task in self.tasks:
            if not task.completed:
                task.completed = True
        self.history.append(("bulk_complete", None))
        self.save_tasks()

    def archive_completed_tasks(self):
        completed_tasks = [task for task in self.tasks if task.completed]
        with open(self.archive_filename, "w") as file:
            json.dump([task.to_dict() for task in completed_tasks], file, indent=4)
        self.tasks = [task for task in self.tasks if not task.completed]
        self.save_tasks()

    def export_tasks_to_csv(self, filename="tasks.csv"):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Due Date", "Priority", "Category", "Completed", "Recurrence"])
            for task in self.tasks:
                writer.writerow([
                    task.task_id,
                    task.name,
                    task.due_date,
                    task.priority,
                    task.category,
                    task.completed,
                    task.recurrence,
                ])

    def list_tasks(self, sort_by=None, filter_by_category=None, include_completed=True):
        tasks = self.tasks

        if filter_by_category:
            tasks = [task for task in tasks if task.category.lower() == filter_by_category.lower()]

        if not include_completed:
            tasks = [task for task in tasks if not task.completed]

        if sort_by == "due_date":
            tasks.sort(key=lambda x: datetime.strptime(x.due_date, "%Y-%m-%d"))
        elif sort_by == "priority":
            priority_order = {"High": 1, "Medium": 2, "Low": 3}
            tasks.sort(key=lambda x: priority_order.get(x.priority, 99))
        elif sort_by == "name":
            tasks.sort(key=lambda x: x.name.lower())
        elif sort_by == "status":
            tasks.sort(key=lambda x: x.completed)

        return tasks

    def search_tasks(self, keyword):
        return [task for task in self.tasks if keyword.lower() in task.name.lower()]

    def undo_last_action(self):
        if not self.history:
            return False
        action, data = self.history.pop()
        if action == "add":
            self.tasks.remove(data)
        elif action == "update":
            task = self.get_task(data["id"])
            if task:
                task.name = data["name"]
                task.due_date = data["due_date"]
                task.priority = data["priority"]
                task.category = data["category"]
                task.completed = data["completed"]
                task.recurrence = data["recurrence"]
        elif action == "delete":
            self.tasks.append(data)
        elif action == "bulk_complete":
            for task in self.tasks:
                task.completed = False
        self.save_tasks()
        return True

    def get_overdue_tasks(self):
        today = datetime.now().date()
        return [task for task in self.tasks if datetime.strptime(task.due_date, "%Y-%m-%d").date() < today and not task.completed]


class CLI:
    def __init__(self):
        self.manager = TodoManager()

    def display_reminders(self):
        overdue_tasks = self.manager.get_overdue_tasks()
        if overdue_tasks:
            print("\n--- Reminder: Overdue Tasks ---")
            for task in overdue_tasks:
                print(f"{task.task_id}: {task.name} (Due: {task.due_date})")
            print("-------------------------------")

    def run(self):
        self.display_reminders()
        while True:
            print("\n--- Todo List Manager ---")
            print("1. List all tasks")
            print("2. Add a new task")
            print("3. Update an existing task")
            print("4. Delete a task")
            print("5. Mark all tasks as completed")
            print("6. Archive completed tasks")
            print("7. Export tasks to CSV")
            print("8. Search tasks by keyword")
            print("9. Undo last action")
            print("10. Quit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.display_tasks()
            elif choice == "2":
                self.add_task()
            elif choice == "3":
                self.update_task()
            elif choice == "4":
                self.delete_task()
            elif choice == "5":
                self.mark_all_completed()
            elif choice == "6":
                self.archive_tasks()
            elif choice == "7":
                self.export_tasks()
            elif choice == "8":
                self.search_tasks()
            elif choice == "9":
                self.undo_action()
            elif choice == "10":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def display_tasks(self):
        sort_by = input("Sort by (due_date/priority/name/status): ").strip()
        tasks = self.manager.list_tasks(sort_by=sort_by)
        for task in tasks:
            status = "Completed" if task.completed else "Pending"
            print(
                f"{task.task_id}: {task.name} | Due: {task.due_date} | Priority: {task.priority} | Category: {task.category} | Status: {status} | Recurrence: {task.recurrence}"
            )

    def add_task(self):
        name = input("Task name: ")
        due_date = input("Due date (YYYY-MM-DD): ")
        priority = input("Priority (High/Medium/Low): ") or "Medium"
        category = input("Category: ") or "General"
        recurrence = input("Recurrence (daily/weekly/monthly/none): ").lower()
        recurrence = recurrence if recurrence != "none" else None
        self.manager.add_task(name, due_date, priority, category, recurrence)
        print("Task added.")

    def update_task(self):
        task_id = int(input("Task ID to update: "))
        name = input("New name (leave blank to skip): ")
        self.manager.update_task(task_id, name=name)
        print("Task updated.")

    def delete_task(self):
        task_id = int(input("Task ID to delete: "))
        self.manager.delete_task(task_id)
        print("Task deleted.")

    def mark_all_completed(self):
        self.manager.mark_all_completed()
        print("All tasks marked as completed.")

    def archive_tasks(self):
        self.manager.archive_completed_tasks()
        print("Archived completed tasks.")

    def export_tasks(self):
        self.manager.export_tasks_to_csv()
        print("Tasks exported to tasks.csv.")

    def search_tasks(self):
        keyword = input("Enter keyword to search: ")
        results = self.manager.search_tasks(keyword)
        if not results:
            print("No tasks match the keyword.")
        else:
            for task in results:
                print(f"{task.task_id}: {task.name} (Due: {task.due_date})")

    def undo_action(self):
        if self.manager.undo_last_action():
            print("Last action undone.")
        else:
            print("No action to undo.")


if __name__ == "__main__":
    CLI().run()
