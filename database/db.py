
from datetime import date, timedelta
import calendar

from database.supabase_client import get_supabase_client
from database.auth import get_current_user


def get_user_id():
    user = get_current_user()

    if not user:
        raise ValueError("Please log in first.")

    return user["id"]


def init_db():
    # Tables are managed through Supabase.
    # No SQLite initialization is required.
    pass


def add_task(title, description, task_type,
             recurrence=None, weekdays=None, due_date=None):

    supabase = get_supabase_client()

    supabase.table("tasks").insert({
        "user_id": get_user_id(),
        "title": title,
        "description": description,
        "task_type": task_type,
        "recurrence": recurrence,
        "weekdays": weekdays,
        "due_date": str(due_date) if due_date else None,
        "created_at": date.today().isoformat(),
        "active": True
    }).execute()


def get_tasks_for_date(selected_date):

    supabase = get_supabase_client()
    user_id = get_user_id()

    response = supabase.table("tasks").select("*").eq(
        "user_id", user_id
    ).eq("active", True).execute()

    all_tasks = response.data

    completion_response = supabase.table(
        "completions"
    ).select("task_id, completed").eq(
        "user_id", user_id
    ).eq(
        "completion_date", selected_date.isoformat()
    ).execute()

    completion_records = {
        row["task_id"]: row["completed"]
        for row in completion_response.data
    }

    completed_response = supabase.table(
        "completions"
    ).select("task_id").eq(
        "user_id", user_id
    ).eq("completed", True).execute()

    completed_once = {
        row["task_id"]
        for row in completed_response.data
    }

    tasks = []

    for task in all_tasks:

        if task["task_type"] == "recurring":

            if task["recurrence"] == "daily":
                tasks.append(task)

            elif task["recurrence"] == "custom":

                weekdays = (task["weekdays"] or "").split(",")

                if str(selected_date.weekday()) in weekdays:
                    tasks.append(task)

        elif task["task_type"] == "one_time":

            if task["id"] not in completed_once:
                tasks.append(task)

    for task in tasks:
        task["completed"] = completion_records.get(
            task["id"], False
        )

    return tasks


def set_completion(task_id, selected_date, completed):

    supabase = get_supabase_client()
    user_id = get_user_id()

    existing = supabase.table("completions").select("id").eq(
        "user_id", user_id
    ).eq(
        "task_id", task_id
    ).eq(
        "completion_date", selected_date.isoformat()
    ).execute()

    data = {
        "user_id": user_id,
        "task_id": task_id,
        "completion_date": selected_date.isoformat(),
        "completed": bool(completed)
    }

    if existing.data:
        supabase.table("completions").update(data).eq(
            "id", existing.data[0]["id"]
        ).eq("user_id", user_id).execute()

    else:
        supabase.table("completions").insert(data).execute()


def get_weekly_progress(start_date, end_date):

    supabase = get_supabase_client()

    response = supabase.table("completions").select(
        "completed"
    ).eq(
        "user_id", get_user_id()
    ).gte(
        "completion_date", str(start_date)
    ).lte(
        "completion_date", str(end_date)
    ).execute()

    total = len(response.data)

    completed = sum(
        1 for row in response.data if row["completed"]
    )

    return total, completed


def get_daily_weekly_progress(start_date, end_date):

    weekly_data = []

    current_date = date.fromisoformat(start_date)
    last_date = date.fromisoformat(end_date)

    while current_date <= last_date:

        tasks = get_tasks_for_date(current_date)

        total = len(tasks)
        completed = sum(
            bool(task["completed"]) for task in tasks
        )

        percentage = (
            completed / total * 100 if total > 0 else 0
        )

        weekly_data.append({
            "day": current_date.strftime("%a"),
            "date": current_date.isoformat(),
            "total": total,
            "completed": completed,
            "percentage": percentage
        })

        current_date += timedelta(days=1)

    return weekly_data


def get_daily_monthly_progress(year, month):

    monthly_data = []

    total_days = calendar.monthrange(year, month)[1]

    for day in range(1, total_days + 1):

        current_date = date(year, month, day)

        tasks = get_tasks_for_date(current_date)

        total = len(tasks)

        completed = sum(
            bool(task["completed"]) for task in tasks
        )

        percentage = (
            completed / total * 100 if total > 0 else 0
        )

        monthly_data.append({
            "day": day,
            "total": total,
            "completed": completed,
            "percentage": percentage
        })

    return monthly_data


def get_monthly_yearly_progress(year):

    yearly_data = []

    for month in range(1, 13):

        total = 0
        completed = 0

        total_days = calendar.monthrange(year, month)[1]

        for day in range(1, total_days + 1):

            current_date = date(year, month, day)

            tasks = get_tasks_for_date(current_date)

            total += len(tasks)

            completed += sum(
                bool(task["completed"]) for task in tasks
            )

        percentage = (
            completed / total * 100 if total > 0 else 0
        )

        yearly_data.append({
            "month": calendar.month_abbr[month],
            "total": total,
            "completed": completed,
            "percentage": percentage
        })

    return yearly_data


def reset_all_data():

    supabase = get_supabase_client()
    user_id = get_user_id()

    # Get this user's task IDs
    response = supabase.table("tasks").select("id").eq(
        "user_id", user_id
    ).execute()

    task_ids = [task["id"] for task in response.data]

    if task_ids:

        supabase.table("completions").delete().eq(
            "user_id", user_id
        ).in_("task_id", task_ids).execute()

        supabase.table("tasks").delete().eq(
            "user_id", user_id
        ).execute()
