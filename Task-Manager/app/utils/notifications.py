import time
from datetime import datetime

def log_activity(user_id: int, action: str):
    """Logs the activity of a user to a log file."""
    print(f"[LOGS] being recorded for user {user_id}")
    print(f"[LOGS] for user {user_id} are complete!")


    with open("activity_log.txt", "a") as f:
        f.write(f"{datetime.now()} | User_id: {user_id} | Action: {action}\n")

def send_notification(email: str, message: str):
    """Sends a notification to the user (slow operation)"""
    print(f"[NOTIF] Sending notification to {email}")
    time.sleep(2)    # Simulate network delay
    print(f"[NOTIF] Complete: Notification sent to {email}")

    with open("notification_log.txt", "a") as f:
        f.write(f"{datetime.now()} | Email: {email} | Message: {message}\n")