
"""Student Attendance Tracker for Lab 5: Static Code Analysis."""

import csv
import glob
import os
import ssl
import tarfile
from datetime import datetime

import requests

# Global attendance register and configuration.
students = {}
attendance_register = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = os.getenv("ERP_API_KEY")
MIN_ATTENDANCE = 75
VALID_STATUSES = {"P", "A", "L", "H"}


def add_student(roll_no, name, section="A"):
    """Add a student to the attendance tracker."""
    if roll_no in students:
        raise ValueError(f"Student already exists: {roll_no}")

    students[roll_no] = {
        "name": name,
        "section": section,
        "records": [],
    }


def mark_attendance(roll_no, date, status, register=None):
    """Record attendance once per student per valid date."""
    if register is None:
        register = attendance_register

    if roll_no not in students:
        raise ValueError(f"Unknown student: {roll_no}")

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        if parsed_date.strftime("%Y-%m-%d") != date:
            raise ValueError
    except ValueError as exc:
        raise ValueError(
            "Date must be valid and use YYYY-MM-DD format"
        ) from exc

    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid attendance status: {status}")

    records = students[roll_no]["records"]

    if any(record_date == date for record_date, _ in records):
        raise ValueError(
            f"Attendance already recorded for {roll_no} on {date}"
        )

    register.setdefault(date, []).append(roll_no)
    records.append((date, status))
    return register


def attendance_percentage(roll_no):
    """Calculate the percentage of recorded days marked present."""
    if roll_no not in students:
        raise ValueError(f"Unknown student: {roll_no}")

    records = students[roll_no]["records"]
    if not records:
        return 0

    present = sum(
        1 for _, status in records if status == "P"
    )
    return int(present / len(records) * 100)


def is_eligible(percentage):
    """Check whether attendance meets the minimum percentage."""
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    """Return students below the minimum attendance percentage."""
    return [
        roll_no
        for roll_no in students
        if not is_eligible(attendance_percentage(roll_no))
    ]


def has_long_absence(roll_no, days=3):
    """Check for the specified number of consecutive absent records."""
    if roll_no not in students:
        raise ValueError(f"Unknown student: {roll_no}")
    if days < 1:
        raise ValueError("days must be at least 1")

    records = sorted(students[roll_no]["records"])
    absent_dates = {
        datetime.strptime(date, "%Y-%m-%d").date()
        for date, status in records
        if status == "A"
    }

    for date in absent_dates:
        if all(
            datetime.combine(date, datetime.min.time()).date()
            .toordinal() + offset in {
                item.toordinal() for item in absent_dates
            }
            for offset in range(days)
        ):
            return True

    return False


def latest_date(roll_no):
    """Return the latest attendance date, or None if there are no records."""
    if roll_no not in students:
        raise ValueError(f"Unknown student: {roll_no}")

    dates = [
        datetime.strptime(date, "%Y-%m-%d").date()
        for date, _ in students[roll_no]["records"]
    ]
    return max(dates).isoformat() if dates else None


def export_csv(path="attendance.csv"):
    """Export attendance percentages while guarding against CSV formulas."""
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            name = student["name"]
            if name.lstrip().startswith(("=", "+", "-", "@")):
                name = "'" + name

            writer.writerow(
                [roll_no, name, attendance_percentage(roll_no)]
            )

    return path


def sync_to_erp(roll_no):
    """Send a student's attendance percentage to the ERP securely."""
    if not ERP_API_KEY:
        raise RuntimeError(
            "Set the ERP_API_KEY environment variable before syncing"
        )

    payload = {
        "roll_no": roll_no,
        "pct": attendance_percentage(roll_no),
    }
    response = requests.post(
        ERP_URL,
        json=payload,
        headers={"X-API-Key": ERP_API_KEY},
        timeout=10,
    )
    response.raise_for_status()
    return response.status_code


def backup_reports():
    """Create a compressed archive of CSV reports."""
    csv_files = glob.glob("*.csv")
    if not csv_files:
        return None

    with tarfile.open("reports_backup.tgz", "w:gz") as archive:
        for file_path in csv_files:
            archive.add(file_path, arcname=os.path.basename(file_path))

    return "reports_backup.tgz"


def legacy_channel():
    """Create a TLS context with secure default settings."""
    return ssl.create_default_context()


def run_job(command):
    """Describe a job without executing a shell command."""
    if not isinstance(command, list) or not command:
        raise ValueError("Command must be a non-empty list")
    if not all(isinstance(item, str) for item in command):
        raise ValueError("Every command argument must be a string")

    return {"command": command, "shell": False}


def schedule_reminders():
    """Prepare the attendance-shortage reminder job."""
    return run_job(["send_sms", "--shortage"])


def main():
    """Run the demonstration attendance-tracker workflow."""
    add_student("R01", "Aditi")
    add_student("R02", '=HYPERLINK("http://evil.example","Bharat")')

    student_one_records = [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "L"),
        ("2026-09-04", "P"),
        ("2026-09-05", "H"),
    ]
    student_two_records = [
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-09-05", "P"),
    ]

    for date, status in student_one_records:
        mark_attendance("R01", date, status)

    for date, status in student_two_records:
        mark_attendance("R02", date, status)

    # Check the 75% boundary without modifying attendance records.
    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print(
        "Register entries for 2026-09-01:",
        attendance_register["2026-09-01"],
    )
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped (no network)")


if __name__ == "__main__":
    main()
