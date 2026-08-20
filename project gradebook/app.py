"""
app.py -- Student Gradebook CLI Entry Point
==========================================
Running `python app.py` launches an interactive menu-driven application.

This file handles ONLY user input/output and the main menu loop.
All business logic (validation, storage, grading, reports) lives in utils.py.
"""

import sys
import os

# Ensure stdout uses UTF-8 on Windows so Unicode characters display correctly.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from tabulate import tabulate
    _TABULATE_AVAILABLE = True
except ImportError:
    _TABULATE_AVAILABLE = False

import utils

# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _print_table(headers, rows):
    """Print a formatted table, falling back to plain text if tabulate is missing."""
    if _TABULATE_AVAILABLE and rows:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        # Plain-text fallback
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
        print(separator)
        print(header_line)
        print(separator)
        for row in rows:
            line = "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
            print(line)
        print(separator)


def _success(msg):
    print(f"\n  [OK] {msg}\n")


def _error(msg):
    print(f"\n  [ERROR] {msg}\n")


def _info(msg):
    print(f"\n  {msg}\n")


def _divider(title=""):
    width = 60
    if title:
        pad = (width - len(title) - 2) // 2
        print("\n" + "─" * pad + f" {title} " + "─" * pad)
    else:
        print("\n" + "─" * width)


def _prompt(label):
    """Read a line of input from the user, stripping surrounding whitespace."""
    try:
        return input(f"  {label}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# MENU HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

def handle_add_student():
    """Prompt the user and add a new student."""
    _divider("Add Student")
    student_id = _prompt("Student ID (e.g. S01)")
    name = _prompt("Student Name (e.g. Ravi Kumar)")
    ok, msg = utils.add_student(student_id, name)
    if ok:
        _success(msg)
    else:
        _error(msg)


def handle_update_student():
    """Prompt the user and update an existing student's name."""
    _divider("Update Student Name")
    student_id = _prompt("Student ID to update")
    new_name = _prompt("New name")
    ok, msg = utils.update_student_name(student_id, new_name)
    if ok:
        _success(msg)
    else:
        _error(msg)


def handle_add_marks():
    """Prompt the user and add or update a student's mark for a subject."""
    _divider("Add / Update Marks")
    student_id = _prompt("Student ID")
    subject = _prompt("Subject (e.g. Python)")
    marks_input = _prompt("Marks (0-100)")
    ok, msg = utils.add_or_update_mark(student_id, subject, marks_input)
    if ok:
        _success(msg)
    else:
        _error(msg)


def handle_view_student():
    """Display a single student's full record and marks."""
    _divider("View Student Record")
    student_id = _prompt("Student ID")
    ok, result = utils.student_summary(student_id)
    if not ok:
        _error(result)
        return

    print(f"\n  Student ID : {result['student_id']}")
    print(f"  Name       : {result['name']}")

    if not result["marks_list"]:
        _info("No marks recorded yet for this student.")
        return

    rows = [
        (m["subject"], m["marks"], m["grade"])
        for m in result["marks_list"]
    ]
    _print_table(["Subject", "Marks", "Grade"], rows)
    print(f"\n  Overall Average : {result['overall_average']}")
    print(f"  Overall Grade   : {result['overall_grade']}\n")


def handle_view_all():
    """Display all students currently in the system."""
    _divider("All Students")
    students = utils.get_all_students()
    if not students:
        _info("No students found. Add some students first.")
        return

    rows = [(s["student_id"], s["name"]) for s in students]
    _print_table(["Student ID", "Name"], rows)


def handle_view_subject():
    """Display all marks for a particular subject."""
    _divider("View Subject Marks")
    subject = _prompt("Subject name")
    ok, err = utils.validate_subject(subject)
    if not ok:
        _error(err)
        return

    records = utils.get_marks_for_subject(subject)
    if not records:
        _info(f"No marks found for subject '{subject.strip()}'.")
        return

    rows = [
        (r["student_id"], r["name"], r["marks"], r["grade"])
        for r in records
    ]
    _print_table(["Student ID", "Name", "Marks", "Grade"], rows)


def handle_delete_student():
    """Prompt the user and delete a student (and all their marks)."""
    _divider("Delete Student")
    student_id = _prompt("Student ID to delete")
    confirm = _prompt(f"Type YES to confirm deletion of student '{student_id.strip().upper()}'")
    if confirm.upper() != "YES":
        _info("Deletion cancelled.")
        return
    ok, msg = utils.delete_student(student_id)
    if ok:
        _success(msg)
    else:
        _error(msg)


def handle_delete_mark():
    """Prompt the user and delete a specific subject-mark entry."""
    _divider("Delete Mark Entry")
    student_id = _prompt("Student ID")
    subject = _prompt("Subject to remove")
    ok, msg = utils.delete_mark(student_id, subject)
    if ok:
        _success(msg)
    else:
        _error(msg)


def handle_student_report():
    """Print a detailed performance report for one student."""
    _divider("Student Performance Report")
    student_id = _prompt("Student ID")
    ok, result = utils.student_summary(student_id)
    if not ok:
        _error(result)
        return

    print(f"\n  +-- STUDENT REPORT ----------------------------------------+")
    print(f"  |  ID   : {result['student_id']}")
    print(f"  |  Name : {result['name']}")
    print(f"  +----------------------------------------------------------+\n")

    if not result["marks_list"]:
        _info("No marks recorded yet for this student.")
        return

    rows = [
        (m["subject"], m["marks"], m["grade"])
        for m in result["marks_list"]
    ]
    _print_table(["Subject", "Marks", "Grade"], rows)

    print(f"\n  Overall Average : {result['overall_average']}")
    print(f"  Overall Grade   : {result['overall_grade']}\n")


def handle_class_analytics():
    """Print class-level analytics across all students and subjects."""
    _divider("Class Analytics")
    data = utils.class_analytics()

    print(f"\n  Total Students  : {data['total_students']}")
    print(f"  Total Mark Entries : {data['total_marks_entries']}")
    print(f"  Overall Pass (by avg) : {data['class_pass_count']}")
    print(f"  Overall Fail (by avg) : {data['class_fail_count']}")

    if not data["subject_stats"]:
        _info("No marks data available yet.")
        return

    # Subject statistics table
    _divider("Subject-wise Statistics")
    subj_rows = []
    for subj, stats in sorted(data["subject_stats"].items()):
        subj_rows.append((
            subj,
            stats["entry_count"],
            stats["average"],
            stats["highest"],
            stats["lowest"],
            stats["pass_count"],
            stats["fail_count"],
        ))
    _print_table(
        ["Subject", "Entries", "Avg", "Highest", "Lowest", "Pass", "Fail"],
        subj_rows,
    )

    # Top performers table
    if data["top_performers"]:
        _divider("Student Rankings (by Overall Average)")
        perf_rows = [
            (i + 1, p["student_id"], p["name"], p["average"], p["grade"])
            for i, p in enumerate(data["top_performers"])
        ]
        _print_table(["Rank", "ID", "Name", "Avg", "Grade"], perf_rows)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────

MENU = """
+================================================+
|        STUDENT GRADEBOOK SYSTEM               |
+================================================+
|  STUDENT MANAGEMENT                           |
|   1. Add Student                              |
|   2. Update Student Name                      |
|   3. Delete Student                           |
|   4. View All Students                        |
+------------------------------------------------+
|  MARKS MANAGEMENT                             |
|   5. Add / Update Marks                       |
|   6. Delete a Mark Entry                      |
|   7. View Student Record (with marks)         |
|   8. View Marks by Subject                    |
+------------------------------------------------+
|  REPORTS                                      |
|   9. Student Performance Report               |
|  10. Class Analytics                          |
+------------------------------------------------+
|   0. Exit                                     |
+================================================+
"""

HANDLERS = {
    "1": handle_add_student,
    "2": handle_update_student,
    "3": handle_delete_student,
    "4": handle_view_all,
    "5": handle_add_marks,
    "6": handle_delete_mark,
    "7": handle_view_student,
    "8": handle_view_subject,
    "9": handle_student_report,
    "10": handle_class_analytics,
}


def main():
    """Main application loop — display menu and dispatch user choices."""
    # Ensure the data directory and files exist before first use.
    utils._ensure_data_dir()

    print("\n  Welcome to the Student Gradebook System!")
    if not _TABULATE_AVAILABLE:
        print("  (Tip: run 'pip install tabulate' for prettier table output.)")

    while True:
        print(MENU)
        choice = _prompt("Enter your choice")

        if choice == "0":
            print("\n  Goodbye! Gradebook saved.\n")
            sys.exit(0)

        handler = HANDLERS.get(choice)
        if handler:
            handler()
        else:
            _error(f"'{choice}' is not a valid option. Please enter a number from 0 to 10.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
