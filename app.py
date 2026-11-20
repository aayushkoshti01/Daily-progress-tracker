
import streamlit as st
from datetime import date, timedelta
from auth_ui import show_auth_page

from database.db import (
    init_db,
    add_task,
    get_tasks_for_date,
    set_completion,
    get_weekly_progress,
    get_daily_weekly_progress,
    get_daily_monthly_progress,
    get_monthly_yearly_progress,
    reset_all_data
)

# Initialize database
init_db()

st.set_page_config(
    page_title="Daily Progress Tracker",
    page_icon="📅",
    layout="wide"
)
# Authentication check
if not show_auth_page():
    st.stop()

# Update task completion
def update_task(task_id, selected_date, widget_key):
    set_completion(
        task_id,
        selected_date,
        st.session_state[widget_key]
    )


# Website title
st.title("📅 Daily Progress Tracker")
st.write("Track your daily tasks and monitor your progress.")

# Select date
selected_date = st.date_input(
    "Select Date",
    value=date.today()
)

st.divider()

# Sidebar: Add task
st.sidebar.header("➕ Add New Task")

with st.sidebar.form("task_form"):

    title = st.text_input("Task Name")
    description = st.text_area("Description")

    task_type = st.selectbox(
        "Task Type",
        ["Recurring", "One-time"]
    )

    recurrence = None
    weekdays = None
    due_date = None

    if task_type == "Recurring":

        recurrence_option = st.selectbox(
            "Repeat",
            ["Daily", "Custom"]
        )

        if recurrence_option == "Custom":

            days = st.multiselect(
                "Select Days",
                ["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]
            )

            day_numbers = {
                "Monday": "0",
                "Tuesday": "1",
                "Wednesday": "2",
                "Thursday": "3",
                "Friday": "4",
                "Saturday": "5",
                "Sunday": "6"
            }

            weekdays = ",".join(
                day_numbers[day] for day in days
            )

            recurrence = "custom"

        else:
            recurrence = "daily"

    else:
        due_date = st.date_input(
            "Deadline",
            value=date.today(),
            key="deadline"
        ).isoformat()

    submitted = st.form_submit_button("Add Task")

    if submitted:

        if title.strip():

            if task_type == "Recurring" and recurrence == "custom" and not weekdays:
                st.error("Please select at least one day.")

            else:
                db_task_type = (
                    "recurring"
                    if task_type == "Recurring"
                    else "one_time"
                )

                add_task(
                    title,
                    description,
                    db_task_type,
                    recurrence,
                    weekdays,
                    due_date
                )

                st.success("Task added successfully!")
                st.rerun()

        else:
            st.error("Please enter a task name.")


# Reset Everything Button
if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

st.sidebar.divider()

if st.sidebar.button("🗑️ Reset Everything", use_container_width=True):
    st.session_state.confirm_reset = True

if st.session_state.confirm_reset:

    st.sidebar.warning(
        "Are you sure? This will permanently delete ALL tasks "
        "and completion history."
    )

    if st.sidebar.button(
        "Yes, Delete Everything",
        type="primary",
        use_container_width=True
    ):

        reset_all_data()

        st.session_state.confirm_reset = False

        st.sidebar.success("All data has been reset!")

        st.rerun()

    if st.sidebar.button(
        "Cancel",
        use_container_width=True
    ):

        st.session_state.confirm_reset = False

        st.rerun()

# Get tasks
tasks = get_tasks_for_date(selected_date)

# Calculate daily progress
total_tasks = len(tasks)
completed_tasks = sum(
    bool(task["completed"]) for task in tasks
)

progress = (
    completed_tasks / total_tasks
    if total_tasks > 0 else 0
)

# Daily Progress
st.subheader("📊 Daily Progress")

col1, col2, col3 = st.columns(3)

col1.metric("Total Tasks", total_tasks)
col2.metric("Completed", completed_tasks)
col3.metric("Pending", total_tasks - completed_tasks)

st.progress(progress)

st.write(f"**{progress * 100:.1f}% completed**")

st.divider()

# Task list
st.subheader(f"📝 Tasks for {selected_date}")

if tasks:

    for task in tasks:

        task_id = task["id"]
        task_label = task["title"]

        if task["description"]:
            task_label += f" — {task['description']}"

        widget_key = (
            f"task_{task_id}_{selected_date.isoformat()}"
        )

        st.checkbox(
            task_label,
            value=bool(task["completed"]),
            key=widget_key,
            on_change=update_task,
            args=(task_id, selected_date, widget_key)
        )

else:
    st.info("No tasks for this date. Add a task using the sidebar.")

st.divider()

# WEEKLY PROGRESS
st.subheader("📅 Weekly Progress")

week_start = selected_date - timedelta(days=selected_date.weekday())
week_end = week_start + timedelta(days=6)

weekly_total, weekly_completed = get_weekly_progress(
    week_start.isoformat(),
    week_end.isoformat()
)

weekly_progress = (
    weekly_completed / weekly_total
    if weekly_total > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Weekly Tasks", weekly_total)
col2.metric("Completed", weekly_completed)
col3.metric("Pending", weekly_total - weekly_completed)

st.progress(weekly_progress)

st.write(f"**Weekly Progress: {weekly_progress * 100:.1f}%**")

st.caption(
    f"Week: {week_start.strftime('%d %b %Y')} - "
    f"{week_end.strftime('%d %b %Y')}"
)

# Weekly chart
st.subheader("📈 Daily Progress This Week")

daily_data = get_daily_weekly_progress(
    week_start.isoformat(),
    week_end.isoformat()
)

weekly_chart = {
    "Day": [item["day"] for item in daily_data],
    "Progress (%)": [item["percentage"] for item in daily_data]
}

st.bar_chart(
    weekly_chart,
    x="Day",
    y="Progress (%)"
)

st.divider()

# MONTHLY PROGRESS
st.header("📅 Monthly Progress")

today = date.today()

monthly_data = get_daily_monthly_progress(
    today.year,
    today.month
)

monthly_total = sum(item["total"] for item in monthly_data)
monthly_completed = sum(item["completed"] for item in monthly_data)

monthly_progress = (
    monthly_completed / monthly_total
    if monthly_total > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Monthly Tasks", monthly_total)
col2.metric("Completed", monthly_completed)
col3.metric("Pending", monthly_total - monthly_completed)

st.progress(monthly_progress)

st.write(f"**Monthly Progress: {monthly_progress * 100:.1f}%**")

st.caption(today.strftime("Month: %B %Y"))

# Monthly chart
st.subheader("📈 Daily Progress This Month")

monthly_chart = {
    "Day": [str(item["day"]) for item in monthly_data],
    "Progress (%)": [item["percentage"] for item in monthly_data]
}

st.bar_chart(
    monthly_chart,
    x="Day",
    y="Progress (%)"
)

st.divider()

# YEARLY PROGRESS
st.header("🗓️ Yearly Progress")

yearly_data = get_monthly_yearly_progress(today.year)

yearly_total = sum(item["total"] for item in yearly_data)
yearly_completed = sum(item["completed"] for item in yearly_data)

yearly_progress = (
    yearly_completed / yearly_total
    if yearly_total > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Yearly Tasks", yearly_total)
col2.metric("Completed", yearly_completed)
col3.metric("Pending", yearly_total - yearly_completed)

st.progress(yearly_progress)

st.write(f"**Yearly Progress: {yearly_progress * 100:.1f}%**")

# Yearly chart
st.subheader("📈 Monthly Progress This Year")

yearly_chart = {
    "Month": [item["month"] for item in yearly_data],
    "Progress (%)": [item["percentage"] for item in yearly_data]
}

st.bar_chart(
    yearly_chart,
    x="Month",
    y="Progress (%)"
)

st.divider()

st.caption("Daily Progress Tracker | Keep moving forward!")
st.markdown(
    """
    <hr>
    <div style="text-align: center; color: gray; padding: 15px;">
        Website made by <b>Aayush Koshti</b>
    </div>
    """,
    unsafe_allow_html=True
)