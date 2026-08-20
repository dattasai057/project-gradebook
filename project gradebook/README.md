# Student Gradebook System

A command-line application built in Python to manage student records, subjects, marks, and performance reports. Designed and implemented as a submission-ready academic project.

---

## Problem Statement

Students and instructors need a simple, reliable way to manage student records, subjects, and marks, and to automatically compute grades and generate performance analytics. Manual tracking in spreadsheets or on paper is error-prone and provides no structured analytics.

---

## Objective

Create a Student Gradebook system that allows a user to:
- Manage students (add, update, remove, view all)
- Manage subjects and marks per student
- Automatically compute grades from marks using a defined grading scale
- Generate per-student performance reports and class-level analytics

---

## Features

| Feature | Description |
|---|---|
| Add Student | Register a new student with a unique ID and name |
| Update Student Name | Rename an existing student |
| Delete Student | Remove a student and all their marks |
| Add / Update Marks | Enter or update marks for a student in a subject |
| Delete Mark Entry | Remove a specific subject-mark record |
| View Student Record | See all marks and grades for one student |
| View All Students | List every registered student |
| View Subject Marks | See all students' marks for a given subject |
| Student Report | Per-student summary with overall average and grade |
| Class Analytics | Subject averages, highest/lowest, pass/fail counts, rankings |

### Grading Scale

| Marks | Grade |
|---|---|
| 90 – 100 | A+ |
| 80 – 89 | A |
| 70 – 79 | B |
| 60 – 69 | C |
| 50 – 59 | D |
| 0 – 49 | Fail |

### Duplicate Marks Handling

If marks are entered for a student-subject pair that already exists, the existing record is **updated** (not duplicated). An update confirmation message is shown with the old and new values.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.8+ | Core programming language |
| `json` (stdlib) | Data persistence (students.json, marks.json) |
| `os` (stdlib) | File path handling |
| `re` (stdlib) | Input validation using regular expressions |
| `unittest` (stdlib) | Automated test framework |
| `tabulate` (PyPI) | Pretty-printed CLI tables |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher installed
- `pip` available

### Steps

1. **Clone or download** the project folder to your machine.

2. **Navigate to the project directory:**
   ```bash
   cd "project gradebook"
   ```

3. **(Recommended) Create a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run the Project

```bash
python app.py
```

This launches the interactive menu. Use number keys (`1`–`10`) to navigate, and `0` to exit.

### Example Interaction

```
Enter your choice: 1        ← Add Student
  Student ID (e.g. S01): S01
  Student Name: Ravi Kumar
  [OK] Student 'Ravi Kumar' (ID: S01) added successfully.

Enter your choice: 5        ← Add / Update Marks
  Student ID: S01
  Subject: Python
  Marks (0-100): 82
  [OK] Marks added for 'S01' in Python: 82.0 (Grade: A).
```

---

## Project Structure

```
project gradebook/
│
├── app.py               ← CLI entry point; main menu loop and all user handlers
├── utils.py             ← All logic: validation, grading, storage, CRUD, reports
├── requirements.txt     ← Python dependencies (tabulate)
├── README.md            ← This file
├── PROJECT_REPORT.md    ← Academic project report
├── .gitignore           ← Files/folders excluded from version control
│
├── data/                ← Auto-created at runtime (gitignored)
│   ├── students.json    ← Persisted student records
│   └── marks.json       ← Persisted mark records
│
├── tests/
│   └── test_gradebook.py ← Automated unittest suite (10 test classes, 25+ cases)
│
└── docs/
    └── demo_script.md   ← Step-by-step demo guide for screenshots/evaluation
```

---

## Testing Details

### Run All Tests

```bash
python -m pytest tests/ -v
```

or without pytest:

```bash
python -m unittest tests/test_gradebook.py -v
```

### Test Coverage Summary

| Test Class | Type | What It Tests |
|---|---|---|
| `TC01_ValidInput` | Normal | Add student + marks → correct grade + persistence |
| `TC02_InvalidMarksOutOfRange` | Invalid | Marks 150 / -5 rejected, not stored |
| `TC03_InvalidMarksNonNumeric` | Invalid | Marks "abc" / "" / "8O" rejected |
| `TC04_BoundaryMarks` | Boundary | All 12 grade cutoff values (0, 49, 50, 59, …, 100) |
| `TC05_DuplicateEntry` | Duplicate | Same student+subject → update, not duplicate; duplicate ID rejected |
| `TC06_MissingStudent` | Missing | Query/add marks/delete for non-existent student |
| `TC07_MissingSubject` | Missing | Query/delete mark for subject not in records |
| `TC08_ValidationEdgeCases` | Edge | Empty ID, whitespace, special chars, numeric name |
| `TC09_DeletionCascade` | Integration | Student delete also removes all their marks |
| `TC10_ClassAnalytics` | Analytics | Subject avg, highest/lowest, pass/fail, rankings |

---

## Limitations

- **No concurrent access** — JSON files are not safe for simultaneous multi-user access.
- **No authentication** — the system has no login; anyone with access to the terminal can modify records.
- **No export** — reports are displayed in-terminal only; there is no PDF/Excel export.
- **Flat subject names** — subjects are stored as plain strings; there is no subject catalogue or syllabus management.
- **No undo** — deleted records cannot be recovered.

---

## Future Improvements

- **SQLite backend** — replace JSON with SQLite for better concurrency and query flexibility.
- **Export reports** — generate PDF or CSV summaries using `fpdf2` or the built-in `csv` module.
- **Role-based access** — separate instructor and student views with a simple login system.
- **Web / GUI interface** — a Streamlit or Flask frontend for non-technical users.
- **Attendance integration** — track attendance alongside marks.
- **Grade weights** — support weighted marks (e.g., assignment 40%, exam 60%).
