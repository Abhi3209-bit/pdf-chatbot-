import json
import os
from datetime import datetime, timedelta

LOG_FILE = "query_log.json"


def log_query(query):
    """Append a question with a timestamp to the log file."""
    entry = {
        "query": query,
        "timestamp": datetime.now().isoformat()
    }

    logs = _read_logs()
    logs.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def _read_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # If the file is empty or corrupted, start fresh rather than crash
        return []


def get_questions_today():
    logs = _read_logs()
    today = datetime.now().date()

    count = 0
    for entry in logs:
        entry_date = datetime.fromisoformat(entry["timestamp"]).date()
        if entry_date == today:
            count += 1

    return count


def get_weekly_counts():
    """Returns a dict of {day_label: count} for the last 7 days, oldest first."""
    logs = _read_logs()
    today = datetime.now().date()

    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    counts = {day.strftime("%a"): 0 for day in days}

    for entry in logs:
        entry_date = datetime.fromisoformat(entry["timestamp"]).date()
        if entry_date in days:
            label = entry_date.strftime("%a")
            counts[label] += 1

    return counts


def get_recent_questions(limit=5):
    """Returns the most recent questions, newest first, with a friendly time label."""
    logs = _read_logs()
    recent = logs[-limit:][::-1]

    results = []
    for entry in recent:
        timestamp = datetime.fromisoformat(entry["timestamp"])
        results.append({
            "query": entry["query"],
            "time_ago": _time_ago(timestamp)
        })

    return results


def _time_ago(timestamp):
    delta = datetime.now() - timestamp
    seconds = delta.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} min ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hr ago"
    else:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"