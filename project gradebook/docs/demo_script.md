# Demo Script — Student Gradebook CLI

This guide lists the exact menu choices and inputs to enter when demonstrating the application. Run each step in order and take a screenshot after each expected output.

---

## Setup (run once)

```bash
cd "project gradebook"
pip install -r requirements.txt
python app.py
```

---

## Demo Step 1 — Add Students

At the main menu, enter `1` (Add Student).

| Prompt | Input |
|---|---|
| Student ID | `S01` |
| Student Name | `Ravi Kumar` |

**Expected output:**
```
  [OK] Student 'Ravi Kumar' (ID: S01) added successfully.
```

Repeat for a second student — enter `1` again:

| Prompt | Input |
|---|---|
| Student ID | `S02` |
| Student Name | `Priya Sharma` |

And a third:

| Prompt | Input |
|---|---|
| Student ID | `S03` |
| Student Name | `Ali Hassan` |

---

## Demo Step 2 — Add Marks (and see Grades)

Enter `5` (Add / Update Marks).

| Prompt | Input | Expected grade in output |
|---|---|---|
| Student ID | `S01` | — |
| Subject | `Python` | — |
| Marks | `82` | **A** |

Repeat `5` for more marks:

| Student ID | Subject | Marks | Grade |
|---|---|---|---|
| S01 | Mathematics | 73 | B |
| S01 | English | 91 | A+ |
| S02 | Python | 55 | D |
| S02 | Mathematics | 88 | A |
| S03 | Python | 44 | Fail |
| S03 | Mathematics | 66 | C |

Screenshot each `[OK]` confirmation showing the grade.

---

## Demo Step 3 — View Student Record

Enter `7` (View Student Record).

| Prompt | Input |
|---|---|
| Student ID | `S01` |

**Expected output (table + summary):**
```
╭──────────────┬───────┬───────╮
│ Subject      │ Marks │ Grade │
├──────────────┼───────┼───────┤
│ Python       │  82.0 │ A     │
│ Mathematics  │  73.0 │ B     │
│ English      │  91.0 │ A+    │
╰──────────────┴───────┴───────╯

  Overall Average : 82.0
  Overall Grade   : A
```

---

## Demo Step 4 — Invalid Input Demonstration

Enter `5` (Add / Update Marks).

**Test 1 — Out-of-range marks:**

| Prompt | Input |
|---|---|
| Student ID | `S01` |
| Subject | `Science` |
| Marks | `150` |

**Expected output:**
```
  [ERROR] Marks 150.0 is out of range. Allowed range is 0 to 100.
```

**Test 2 — Non-numeric marks:**

| Prompt | Input |
|---|---|
| Student ID | `S01` |
| Subject | `Science` |
| Marks | `abc` |

**Expected output:**
```
  [ERROR] Marks must be a number, got 'abc'.
```

**Test 3 — Non-existent student:**

| Prompt | Input |
|---|---|
| Student ID | `S99` |
| Subject | `Python` |
| Marks | `75` |

**Expected output:**
```
  [ERROR] Student ID 'S99' not found. Add the student first.
```

---

## Demo Step 5 — Duplicate Entry (Update)

Enter `5` (Add / Update Marks) again for a subject already entered:

| Prompt | Input |
|---|---|
| Student ID | `S01` |
| Subject | `Python` |
| Marks | `95` |

**Expected output:**
```
  [OK] Updated Python marks for 'S01': 82.0 → 95.0 (Grade: A+).
```

---

## Demo Step 6 — Student Performance Report

Enter `9` (Student Performance Report).

| Prompt | Input |
|---|---|
| Student ID | `S01` |

**Expected output:** Full report box with all subjects, marks, grades, overall average and overall grade.

---

## Demo Step 7 — Class Analytics

Enter `10` (Class Analytics).

**Expected output:**
- Total students, total mark entries, pass/fail counts
- Subject-wise statistics table (average, highest, lowest, pass/fail per subject)
- Student rankings table ordered by overall average

---

## Demo Step 8 — Delete a Mark Entry

Enter `6` (Delete a Mark Entry).

| Prompt | Input |
|---|---|
| Student ID | `S03` |
| Subject | `Mathematics` |

**Expected output:**
```
  [OK] Mark for 'S03' in 'Mathematics' deleted successfully.
```

---

## Demo Step 9 — View All Students

Enter `4` (View All Students).

**Expected output:** Table listing S01, S02, S03 with their names.

---

## Demo Step 10 — Exit

Enter `0`.

**Expected output:**
```
  Goodbye! Gradebook saved.
```

---

## Notes for Evaluator

- The `data/` folder (containing `students.json` and `marks.json`) is auto-created on first run — you do not need to create it manually.
- If you want a fresh start, delete `data/students.json` and `data/marks.json`.
- All data persists between runs — exit and restart `python app.py` at any point; data will still be there.
