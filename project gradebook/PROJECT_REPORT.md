# Project Report — Student Gradebook System

**Course/Subject:** _(fill in as appropriate)_
**Student Name:** _(fill in as appropriate)_
**Date:** August 2026

---

## 1. Problem Understanding

### Problem Statement
Students and instructors need a reliable way to store, retrieve, and analyse academic marks without resorting to error-prone manual spreadsheets. Specifically:
- There is no central store for student–subject–marks triples.
- Grades must be derived automatically from marks to reduce human error.
- Analytics (averages, rankings, pass/fail counts) must be generated on demand.
- Data must survive between sessions; nothing can be lost when the program exits.

### Key User Stories
| As a… | I want to… | So that… |
|---|---|---|
| Instructor | Register students with unique IDs | Records can be referenced unambiguously |
| Instructor | Enter marks per subject per student | Marks are stored centrally |
| Instructor | See a student's full performance summary | I can identify students needing support |
| Instructor | See class-wide analytics by subject | I can evaluate the difficulty of a subject |
| Student | View my marks and grades | I know where I stand |

---

## 2. Proposed Approach

### Design Philosophy
- **Separation of concerns** — all I/O lives in `app.py`; all logic lives in `utils.py`.
- **Clarity over cleverness** — every function does one thing; names are self-documenting.
- **Fail loudly but gracefully** — every error returns a clear English message; no raw tracebacks ever reach the user.
- **Zero external cost** — only free, standard-library-or-PyPI libraries used.

### Architecture
```
User
  │ input / output
  ▼
app.py (CLI menu handlers)
  │ calls functions
  ▼
utils.py (all logic: validation → grading → CRUD → reports)
  │ reads/writes
  ▼
data/students.json   data/marks.json
```

---

## 3. Implementation Details

### 3.1 Data Model

**Student record** (stored in `data/students.json`)
```json
{ "student_id": "S01", "name": "Ravi Kumar" }
```

**Mark record** (stored in `data/marks.json`)
```json
{ "student_id": "S01", "subject": "Python", "marks": 82.0 }
```

Grades are **not stored** — they are computed on every read using `compute_grade()`. This ensures the grade is always consistent with the marks value, even if the grading scale is updated later.

### 3.2 Module Breakdown

**`utils.py`** — divided into 7 clearly-commented sections:
1. **Constants** — file paths (`DATA_DIR`, `STUDENTS_FILE`, `MARKS_FILE`) and `GRADING_SCALE` list.
2. **Storage** — `load_students()`, `save_students()`, `load_marks()`, `save_marks()` — all thin JSON wrappers.
3. **Validation** — `validate_student_id()`, `validate_name()`, `validate_subject()`, `validate_marks()` — each returns a `(bool, error_message)` tuple for consistent error propagation.
4. **Grading** — `compute_grade(marks)` — iterates the `GRADING_SCALE` list top-down; returns first matching grade.
5. **Student CRUD** — `add_student()`, `get_student()`, `get_all_students()`, `update_student_name()`, `delete_student()`.
6. **Marks CRUD** — `add_or_update_mark()`, `get_marks_for_student()`, `get_marks_for_subject()`, `delete_mark()`.
7. **Reports** — `student_summary()`, `class_analytics()`.

**`app.py`** — a menu loop (`main()`) that reads user choice and dispatches to one of 10 handler functions. Handlers call `utils` functions, then format and print the result. No business logic in `app.py`.

### 3.3 CLI Flow Example

```
python app.py
→ prints menu
→ user enters "1" (Add Student)
→ handle_add_student() prompts for ID and name
→ calls utils.add_student(id, name)
→ utils validates ID (alphanumeric, unique), validates name
→ appends record to students list → saves to students.json
→ returns (True, "Student 'Ravi Kumar' (ID: S01) added successfully.")
→ app.py prints [OK] message
```

---

## 4. Important Technical Decisions

### 4.1 Storage: JSON over SQLite or CSV

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **JSON** | Human-readable, stdlib, easy explain in viva | Not for concurrent access | ✅ Chosen |
| SQLite | SQL queries, concurrent | Requires SQL knowledge in viva | Rejected for simplicity |
| CSV | Simplest | No natural structure for two entity types | Rejected |

JSON was chosen because it maps naturally to Python dicts/lists, is fully human-readable, and requires no SQL knowledge to explain.

### 4.2 Duplicate Marks: Update not Reject

When a student already has a mark for a subject:
- **Reject** would force the instructor to delete first, then re-add — needlessly complex.
- **Update** is the intuitive behavior; the system shows the old and new value for transparency.

Decision: **update**, with a clear message showing the change.

### 4.3 Grade Computed, Not Stored

Grades are derived from marks at read-time. Storing grades would introduce a risk of the stored grade becoming inconsistent with the marks if a bug or scale change occurs. Deriving them is both simpler and more reliable.

### 4.4 Validation Return Pattern

Every validation function returns `(bool, message)` so callers can uniformly check the result:
```python
ok, err = validate_marks(input_value)
if not ok:
    return False, err
```
This avoids raising exceptions for expected user input errors, keeping the code easier to follow.

### 4.5 Grading Scale as a Constant List

`GRADING_SCALE` is a module-level list of `(threshold, grade)` tuples. This makes the scale easy to read, easy to change, and the grading logic (`compute_grade`) reads naturally: "check top-down, return first match".

---

## 5. Testing Performed

### Automated Tests (10 test classes, 25+ assertions)

Tests are in `tests/test_gradebook.py` and use Python's `unittest` framework. Each test class patches `utils.DATA_DIR` to a temporary directory so tests are fully isolated and do not touch real data.

| Class | Cases |
|---|---|
| `TC01_ValidInput` | Add student, add marks, correct grade, persistence |
| `TC02_InvalidMarksOutOfRange` | 150 rejected, -5 rejected, not stored |
| `TC03_InvalidMarksNonNumeric` | "abc", "", "8O" all rejected |
| `TC04_BoundaryMarks` | 12 boundary values (0 → Fail, 50 → D, … 100 → A+) |
| `TC05_DuplicateEntry` | Update on duplicate, only one record kept, duplicate ID rejected |
| `TC06_MissingStudent` | get, summary, add marks, delete on non-existent ID |
| `TC07_MissingSubject` | Query and delete for subject not in records |
| `TC08_ValidationEdgeCases` | Empty/whitespace/special-char inputs for all fields |
| `TC09_DeletionCascade` | Deleting student removes all their marks |
| `TC10_ClassAnalytics` | Exact numeric check of averages, counts, rankings |

### Manual Testing

The application was manually exercised through the CLI for all menu options:
- Adding and viewing students
- Adding marks with valid and invalid inputs
- Viewing subject-level and student-level reports
- Generating class analytics
- Deleting students and marks
- Testing error messages for all invalid input types

---

## 6. Challenges Encountered

### 6.1 Case-Insensitive ID Matching
**Challenge:** A user might enter `s01`, `S01`, or `S01` — these should all refer to the same student.
**Solution:** All student IDs are normalized to uppercase on storage and comparison. All lookups use `.upper()` on both sides.

### 6.2 Subject Name Matching
**Challenge:** `"python"` and `"Python"` could create duplicate entries.
**Solution:** Subject comparisons use `.lower()` on both sides; the stored value preserves the original casing as entered.

### 6.3 Test Isolation
**Challenge:** Tests that write to the filesystem could interfere with each other or with the user's real data.
**Solution:** Each test class patches `utils.DATA_DIR`, `utils.STUDENTS_FILE`, and `utils.MARKS_FILE` to point to a temporary directory created by `tempfile.mkdtemp()`, which is deleted after the test.

### 6.4 tabulate Dependency
**Challenge:** `tabulate` is not in the standard library; the app should still work without it.
**Solution:** `app.py` catches an `ImportError` on `from tabulate import tabulate` and falls back to a hand-written plain-text table printer. The app is fully usable without installing `tabulate`.

---

## 7. Solutions Implemented

| Challenge | Solution |
|---|---|
| Case-insensitive IDs | Normalize to uppercase on store + compare |
| Case-insensitive subjects | Compare with `.lower()`, preserve original case in storage |
| Test data isolation | Patch module-level file paths to temp dir in `setUp` |
| Optional tabulate | Try/except at import, plain-text fallback table printer |
| Graceful error handling | All functions return `(bool, message)`, never raise to the CLI |

---

## 8. Future Scope

1. **SQLite backend** — for multi-user environments and more complex queries.
2. **Export to CSV/PDF** — for printing or sharing reports.
3. **Weighted marks** — e.g., internal assessment 40%, final exam 60%.
4. **Streamlit GUI** — browser-based interface accessible to non-technical users.
5. **Attendance tracking** — add attendance % per student per subject.
6. **Grade thresholds configuration** — allow the grading scale to be edited via a settings file rather than changing source code.
7. **Authentication** — separate instructor and student logins.
8. **Audit log** — record every add/update/delete with a timestamp for accountability.
