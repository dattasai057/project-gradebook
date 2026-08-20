"""
utils.py — Student Gradebook Helper / Logic Module
====================================================
All reusable logic lives here:
  - Constants (file paths, grading scale)
  - Storage   (load/save JSON)
  - Validation
  - Grading
  - Student CRUD
  - Marks CRUD
  - Reports & Analytics

app.py imports everything from this module and only handles user I/O.
"""

import json
import os
import re

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# Paths to the JSON data files (stored in a data/ sub-folder).
# os.path.dirname(__file__) gives the directory of this file so the paths
# work regardless of which directory the user runs the script from.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_BASE_DIR, "data")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
MARKS_FILE = os.path.join(DATA_DIR, "marks.json")

# Grading scale: list of (minimum_marks, grade) tuples, checked top-down.
# A mark qualifies for the FIRST entry whose minimum it meets or exceeds.
GRADING_SCALE = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0,  "Fail"),
]

# Maximum and minimum allowed mark values.
MARKS_MIN = 0
MARKS_MAX = 100

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — STORAGE (load / save JSON)
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_data_dir():
    """Create the data/ directory if it does not already exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_students():
    """
    Load and return the list of student records from disk.

    Returns:
        list[dict]: Each dict has keys 'student_id' (str) and 'name' (str).
                    Returns an empty list if the file does not exist yet.
    """
    _ensure_data_dir()
    if not os.path.exists(STUDENTS_FILE):
        return []
    with open(STUDENTS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_students(students):
    """
    Persist the given list of student records to disk.

    Args:
        students (list[dict]): The full list to write.
    """
    _ensure_data_dir()
    with open(STUDENTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(students, fh, indent=2, ensure_ascii=False)


def load_marks():
    """
    Load and return the list of mark records from disk.

    Returns:
        list[dict]: Each dict has keys 'student_id', 'subject', 'marks' (float).
                    Returns an empty list if the file does not exist yet.
    """
    _ensure_data_dir()
    if not os.path.exists(MARKS_FILE):
        return []
    with open(MARKS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_marks(marks):
    """
    Persist the given list of mark records to disk.

    Args:
        marks (list[dict]): The full list to write.
    """
    _ensure_data_dir()
    with open(MARKS_FILE, "w", encoding="utf-8") as fh:
        json.dump(marks, fh, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_student_id(student_id):
    """
    Validate that a student ID is a non-empty alphanumeric string
    (letters and digits only, no spaces or special characters).

    Args:
        student_id (str): The ID to validate.

    Returns:
        (bool, str): (True, "") on success; (False, error_message) on failure.
    """
    if not student_id or not student_id.strip():
        return False, "Student ID cannot be empty."
    sid = student_id.strip()
    if not sid.isalnum():
        return False, f"Student ID '{sid}' must contain only letters and digits (no spaces or symbols)."
    return True, ""


def validate_name(name):
    """
    Validate that a student name is non-empty and contains only letters and spaces.

    Args:
        name (str): The name to validate.

    Returns:
        (bool, str): (True, "") on success; (False, error_message) on failure.
    """
    if not name or not name.strip():
        return False, "Student name cannot be empty."
    # Allow letters (including accented), spaces, hyphens and apostrophes.
    if not re.match(r"^[A-Za-z\u00C0-\u024F '\-]+$", name.strip()):
        return False, f"Student name '{name.strip()}' must contain only letters, spaces, hyphens, or apostrophes."
    return True, ""


def validate_subject(subject):
    """
    Validate that a subject name is non-empty and contains only letters,
    digits, and spaces (e.g. 'Python', 'Data Science 101').

    Args:
        subject (str): The subject name to validate.

    Returns:
        (bool, str): (True, "") on success; (False, error_message) on failure.
    """
    if not subject or not subject.strip():
        return False, "Subject name cannot be empty."
    if not re.match(r"^[A-Za-z0-9 ]+$", subject.strip()):
        return False, f"Subject '{subject.strip()}' must contain only letters, digits, and spaces."
    return True, ""


def validate_marks(marks_input):
    """
    Validate that a marks value is numeric and within [0, 100].

    Args:
        marks_input (str | int | float): The raw value to validate.

    Returns:
        (bool, float | None, str): (True, float_value, "") on success;
                                   (False, None, error_message) on failure.
    """
    try:
        value = float(marks_input)
    except (ValueError, TypeError):
        return False, None, f"Marks must be a number, got '{marks_input}'."

    if value < MARKS_MIN or value > MARKS_MAX:
        return False, None, (
            f"Marks {value} is out of range. "
            f"Allowed range is {MARKS_MIN} to {MARKS_MAX}."
        )
    return True, value, ""


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — GRADING
# ─────────────────────────────────────────────────────────────────────────────

def compute_grade(marks):
    """
    Compute and return the letter grade for a given numeric mark.

    Uses the module-level GRADING_SCALE constant (checked top-down):
        90–100  → A+
        80–89   → A
        70–79   → B
        60–69   → C
        50–59   → D
        0–49    → Fail

    Args:
        marks (float): A validated numeric mark in [0, 100].

    Returns:
        str: The letter grade string (e.g. 'A', 'Fail').
    """
    for threshold, grade in GRADING_SCALE:
        if marks >= threshold:
            return grade
    # Fallback — should never be reached for validated marks.
    return "Fail"


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — STUDENT CRUD
# ─────────────────────────────────────────────────────────────────────────────

def add_student(student_id, name):
    """
    Add a new student to the store.

    Validates the ID and name. Rejects duplicate IDs.

    Args:
        student_id (str): Desired student ID.
        name (str): Student's full name.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    ok, err = validate_student_id(student_id)
    if not ok:
        return False, err

    ok, err = validate_name(name)
    if not ok:
        return False, err

    sid = student_id.strip().upper()
    name = name.strip()

    students = load_students()
    # Check for duplicate ID (case-insensitive).
    if any(s["student_id"].upper() == sid for s in students):
        return False, f"Student ID '{sid}' already exists. Use a different ID or update the record."

    students.append({"student_id": sid, "name": name})
    save_students(students)
    return True, f"Student '{name}' (ID: {sid}) added successfully."


def get_student(student_id):
    """
    Retrieve a single student record by ID.

    Args:
        student_id (str): The student ID to look up.

    Returns:
        dict | None: The student record dict, or None if not found.
    """
    sid = student_id.strip().upper()
    students = load_students()
    for s in students:
        if s["student_id"].upper() == sid:
            return s
    return None


def get_all_students():
    """
    Return all student records.

    Returns:
        list[dict]: All student records (may be empty).
    """
    return load_students()


def update_student_name(student_id, new_name):
    """
    Update the name of an existing student.

    Args:
        student_id (str): The ID of the student to update.
        new_name (str): The new name.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    ok, err = validate_name(new_name)
    if not ok:
        return False, err

    sid = student_id.strip().upper()
    students = load_students()
    for s in students:
        if s["student_id"].upper() == sid:
            old_name = s["name"]
            s["name"] = new_name.strip()
            save_students(students)
            return True, f"Student '{old_name}' (ID: {sid}) renamed to '{new_name.strip()}'."
    return False, f"Student ID '{sid}' not found."


def delete_student(student_id):
    """
    Delete a student and all their associated marks.

    Args:
        student_id (str): The student ID to delete.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    sid = student_id.strip().upper()

    students = load_students()
    new_students = [s for s in students if s["student_id"].upper() != sid]
    if len(new_students) == len(students):
        return False, f"Student ID '{sid}' not found."

    save_students(new_students)

    # Also remove all marks belonging to this student.
    marks = load_marks()
    new_marks = [m for m in marks if m["student_id"].upper() != sid]
    save_marks(new_marks)

    removed_marks = len(marks) - len(new_marks)
    return True, (
        f"Student ID '{sid}' deleted along with "
        f"{removed_marks} mark record(s)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — MARKS CRUD
# ─────────────────────────────────────────────────────────────────────────────

def add_or_update_mark(student_id, subject, marks_input):
    """
    Add a mark for a student in a subject, or update it if one already exists.

    Design decision: duplicate (student_id + subject) entries are updated,
    not rejected, so instructors can easily correct mistakes without having
    to delete first.

    Args:
        student_id (str): The student's ID.
        subject (str): The subject name.
        marks_input (str | float): The numeric mark.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    sid = student_id.strip().upper()

    # Student must exist.
    if get_student(sid) is None:
        return False, f"Student ID '{sid}' not found. Add the student first."

    ok, err = validate_subject(subject)
    if not ok:
        return False, err

    ok, marks_value, err = validate_marks(marks_input)
    if not ok:
        return False, err

    subj = subject.strip()
    grade = compute_grade(marks_value)

    marks = load_marks()
    for m in marks:
        if m["student_id"].upper() == sid and m["subject"].lower() == subj.lower():
            old_marks = m["marks"]
            m["marks"] = marks_value
            save_marks(marks)
            return True, (
                f"Updated {subj} marks for '{sid}': "
                f"{old_marks} → {marks_value} (Grade: {grade})."
            )

    # No existing entry — insert new.
    marks.append({"student_id": sid, "subject": subj, "marks": marks_value})
    save_marks(marks)
    return True, f"Marks added for '{sid}' in {subj}: {marks_value} (Grade: {grade})."


def get_marks_for_student(student_id):
    """
    Return all mark records for a given student, each enriched with a grade.

    Args:
        student_id (str): The student ID.

    Returns:
        list[dict]: Each dict has 'subject', 'marks', 'grade'.
                    Empty list if no marks exist.
    """
    sid = student_id.strip().upper()
    marks = load_marks()
    result = []
    for m in marks:
        if m["student_id"].upper() == sid:
            result.append({
                "subject": m["subject"],
                "marks": m["marks"],
                "grade": compute_grade(m["marks"]),
            })
    return result


def get_marks_for_subject(subject):
    """
    Return all mark records for a given subject across all students.

    Args:
        subject (str): The subject name.

    Returns:
        list[dict]: Each dict has 'student_id', 'name', 'marks', 'grade'.
                    Empty list if no entries found.
    """
    subj = subject.strip().lower()
    marks = load_marks()
    students = load_students()

    # Build a quick lookup: student_id → name
    name_map = {s["student_id"].upper(): s["name"] for s in students}

    result = []
    for m in marks:
        if m["subject"].lower() == subj:
            sid = m["student_id"].upper()
            result.append({
                "student_id": sid,
                "name": name_map.get(sid, "Unknown"),
                "marks": m["marks"],
                "grade": compute_grade(m["marks"]),
            })
    return result


def delete_mark(student_id, subject):
    """
    Delete a specific subject-mark entry for a student.

    Args:
        student_id (str): The student's ID.
        subject (str): The subject name.

    Returns:
        (bool, str): (True, success_message) or (False, error_message).
    """
    sid = student_id.strip().upper()
    subj = subject.strip().lower()

    marks = load_marks()
    new_marks = [
        m for m in marks
        if not (m["student_id"].upper() == sid and m["subject"].lower() == subj)
    ]

    if len(new_marks) == len(marks):
        return False, f"No mark found for student '{sid}' in subject '{subject.strip()}'."

    save_marks(new_marks)
    return True, f"Mark for '{sid}' in '{subject.strip()}' deleted successfully."


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — REPORTS & ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

def student_summary(student_id):
    """
    Build a per-student summary report.

    Args:
        student_id (str): The student's ID.

    Returns:
        (bool, dict | str): (True, summary_dict) or (False, error_message).

    The summary_dict contains:
        'student_id', 'name', 'marks_list' (list of dicts with subject/marks/grade),
        'overall_average' (float | None), 'overall_grade' (str | None).
    """
    sid = student_id.strip().upper()
    student = get_student(sid)
    if student is None:
        return False, f"Student ID '{sid}' not found."

    marks_list = get_marks_for_student(sid)

    if marks_list:
        avg = sum(m["marks"] for m in marks_list) / len(marks_list)
        overall_grade = compute_grade(avg)
    else:
        avg = None
        overall_grade = None

    return True, {
        "student_id": sid,
        "name": student["name"],
        "marks_list": marks_list,
        "overall_average": round(avg, 2) if avg is not None else None,
        "overall_grade": overall_grade,
    }


def class_analytics():
    """
    Compute class-level analytics across all students and subjects.

    Returns:
        dict with keys:
            'total_students'   (int)
            'total_marks'      (int)
            'subject_stats'    (dict: subject → {average, highest, lowest, pass_count, fail_count})
            'top_performers'   (list of dicts: student_id, name, average, grade)
            'class_pass_count' (int)
            'class_fail_count' (int)
    """
    students = load_students()
    marks = load_marks()

    # Build subject → list of (student_id, marks_value) mapping.
    subject_map = {}
    for m in marks:
        subj = m["subject"]
        if subj not in subject_map:
            subject_map[subj] = []
        subject_map[subj].append((m["student_id"], m["marks"]))

    # Per-subject statistics.
    subject_stats = {}
    for subj, entries in subject_map.items():
        values = [e[1] for e in entries]
        pass_count = sum(1 for v in values if compute_grade(v) != "Fail")
        fail_count = len(values) - pass_count
        subject_stats[subj] = {
            "average": round(sum(values) / len(values), 2),
            "highest": max(values),
            "lowest": min(values),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "entry_count": len(values),
        }

    # Per-student overall average for top-performer ranking.
    name_map = {s["student_id"].upper(): s["name"] for s in students}
    student_averages = {}
    for m in marks:
        sid = m["student_id"].upper()
        student_averages.setdefault(sid, []).append(m["marks"])

    top_performers = []
    class_pass = 0
    class_fail = 0
    for sid, mark_values in student_averages.items():
        avg = sum(mark_values) / len(mark_values)
        grade = compute_grade(avg)
        top_performers.append({
            "student_id": sid,
            "name": name_map.get(sid, "Unknown"),
            "average": round(avg, 2),
            "grade": grade,
        })
        if grade == "Fail":
            class_fail += 1
        else:
            class_pass += 1

    # Sort by average descending.
    top_performers.sort(key=lambda x: x["average"], reverse=True)

    return {
        "total_students": len(students),
        "total_marks_entries": len(marks),
        "subject_stats": subject_stats,
        "top_performers": top_performers,
        "class_pass_count": class_pass,
        "class_fail_count": class_fail,
    }
