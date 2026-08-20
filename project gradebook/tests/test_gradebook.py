"""
tests/test_gradebook.py — Automated Test Suite for Student Gradebook
======================================================================
Run with:
    python -m pytest tests/ -v
or:
    python -m unittest tests/test_gradebook.py -v

Test cases cover:
  TC01 — Valid input (normal flow)
  TC02 — Invalid marks (out of range)
  TC03 — Invalid marks (non-numeric)
  TC04 — Boundary marks (0, 50, 80, 90, 100)
  TC05 — Duplicate entry (same student + subject added twice)
  TC06 — Missing / non-existent student
  TC07 — Missing / non-existent subject
  TC08 — Student ID validation
  TC09 — Deletion cascade (marks removed with student)
  TC10 — Class analytics accuracy
"""

import sys
import os
import json
import unittest
import tempfile
import shutil

# Make sure the project root is on the path so we can import utils.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils


class GradebookTestCase(unittest.TestCase):
    """Base class that redirects data files to a temporary directory."""

    def setUp(self):
        """Create a fresh temporary data directory before each test."""
        self.test_dir = tempfile.mkdtemp()
        # Patch the module-level path constants so tests don't touch real data.
        utils.DATA_DIR = self.test_dir
        utils.STUDENTS_FILE = os.path.join(self.test_dir, "students.json")
        utils.MARKS_FILE = os.path.join(self.test_dir, "marks.json")

    def tearDown(self):
        """Remove the temporary directory after each test."""
        shutil.rmtree(self.test_dir, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# TC01 — Valid Input (Normal Flow)
# ─────────────────────────────────────────────────────────────────────────────

class TC01_ValidInput(GradebookTestCase):
    """
    Expected behavior:
      Input : ADD S01 Ravi Python 82
      Output: Grade A, success messages at each step, data persisted to JSON.
    """

    def test_add_student_success(self):
        ok, msg = utils.add_student("S01", "Ravi Kumar")
        self.assertTrue(ok, msg)
        self.assertIn("S01", msg)

    def test_add_marks_returns_correct_grade(self):
        utils.add_student("S01", "Ravi Kumar")
        ok, msg = utils.add_or_update_mark("S01", "Python", 82)
        self.assertTrue(ok, msg)
        self.assertIn("Grade: A", msg)

    def test_compute_grade_A(self):
        self.assertEqual(utils.compute_grade(82), "A")

    def test_student_summary_contains_expected_fields(self):
        utils.add_student("S01", "Ravi Kumar")
        utils.add_or_update_mark("S01", "Python", 82)
        ok, summary = utils.student_summary("S01")
        self.assertTrue(ok)
        self.assertEqual(summary["student_id"], "S01")
        self.assertEqual(summary["name"], "Ravi Kumar")
        self.assertEqual(len(summary["marks_list"]), 1)
        self.assertEqual(summary["marks_list"][0]["grade"], "A")
        self.assertEqual(summary["overall_average"], 82.0)
        self.assertEqual(summary["overall_grade"], "A")

    def test_data_persists_across_load_calls(self):
        utils.add_student("S01", "Ravi Kumar")
        utils.add_or_update_mark("S01", "Python", 82)
        # Reload from disk.
        students = utils.load_students()
        marks = utils.load_marks()
        self.assertEqual(len(students), 1)
        self.assertEqual(len(marks), 1)
        self.assertEqual(marks[0]["marks"], 82)


# ─────────────────────────────────────────────────────────────────────────────
# TC02 — Invalid Marks (Out of Range)
# ─────────────────────────────────────────────────────────────────────────────

class TC02_InvalidMarksOutOfRange(GradebookTestCase):
    """
    Expected behavior:
      Input : Marks = 150 (or -5)
      Output: Validation error message, record NOT stored.
    """

    def test_marks_above_100_rejected(self):
        utils.add_student("S02", "Priya")
        ok, msg = utils.add_or_update_mark("S02", "Math", 150)
        self.assertFalse(ok)
        self.assertIn("out of range", msg.lower())

    def test_marks_below_0_rejected(self):
        utils.add_student("S02", "Priya")
        ok, msg = utils.add_or_update_mark("S02", "Math", -5)
        self.assertFalse(ok)
        self.assertIn("out of range", msg.lower())

    def test_invalid_marks_not_stored(self):
        utils.add_student("S02", "Priya")
        utils.add_or_update_mark("S02", "Math", 150)
        marks = utils.load_marks()
        self.assertEqual(len(marks), 0)


# ─────────────────────────────────────────────────────────────────────────────
# TC03 — Invalid Marks (Non-numeric)
# ─────────────────────────────────────────────────────────────────────────────

class TC03_InvalidMarksNonNumeric(GradebookTestCase):
    """
    Expected behavior:
      Input : Marks = "abc" or ""
      Output: Validation error, record NOT stored.
    """

    def test_string_marks_rejected(self):
        utils.add_student("S03", "Ali")
        ok, msg = utils.add_or_update_mark("S03", "Science", "abc")
        self.assertFalse(ok)
        self.assertIn("number", msg.lower())

    def test_empty_marks_rejected(self):
        utils.add_student("S03", "Ali")
        ok, msg = utils.add_or_update_mark("S03", "Science", "")
        self.assertFalse(ok)

    def test_special_char_marks_rejected(self):
        utils.add_student("S03", "Ali")
        ok, msg = utils.add_or_update_mark("S03", "Science", "8O")  # letter O not zero
        self.assertFalse(ok)


# ─────────────────────────────────────────────────────────────────────────────
# TC04 — Boundary Marks
# ─────────────────────────────────────────────────────────────────────────────

class TC04_BoundaryMarks(GradebookTestCase):
    """
    Expected behavior for exact grade cutoff values:
      0   → Fail
      49  → Fail
      50  → D
      59  → D
      60  → C
      70  → B
      80  → A
      90  → A+
      100 → A+
    """

    BOUNDARY_CASES = [
        (0,   "Fail"),
        (49,  "Fail"),
        (50,  "D"),
        (59,  "D"),
        (60,  "C"),
        (69,  "C"),
        (70,  "B"),
        (79,  "B"),
        (80,  "A"),
        (89,  "A"),
        (90,  "A+"),
        (100, "A+"),
    ]

    def test_all_grade_boundaries(self):
        for marks, expected_grade in self.BOUNDARY_CASES:
            with self.subTest(marks=marks, expected=expected_grade):
                self.assertEqual(
                    utils.compute_grade(marks), expected_grade,
                    f"compute_grade({marks}) should be '{expected_grade}'"
                )

    def test_marks_0_accepted(self):
        utils.add_student("S04", "Test Student")
        ok, _ = utils.add_or_update_mark("S04", "History", 0)
        self.assertTrue(ok)

    def test_marks_100_accepted(self):
        utils.add_student("S04", "Test Student")
        ok, _ = utils.add_or_update_mark("S04", "History", 100)
        self.assertTrue(ok)


# ─────────────────────────────────────────────────────────────────────────────
# TC05 — Duplicate Entry (Same Student + Subject Added Twice)
# ─────────────────────────────────────────────────────────────────────────────

class TC05_DuplicateEntry(GradebookTestCase):
    """
    Design decision: duplicate entries are UPDATED not rejected.
    Expected behavior:
      First ADD  S01 Ravi Python 82  → stored, grade A
      Second ADD S01 Ravi Python 95  → updated, grade A+, only 1 record exists
    """

    def test_duplicate_mark_updates_existing(self):
        utils.add_student("S01", "Ravi")
        utils.add_or_update_mark("S01", "Python", 82)
        ok, msg = utils.add_or_update_mark("S01", "Python", 95)
        self.assertTrue(ok)
        self.assertIn("Updated", msg)
        self.assertIn("Grade: A+", msg)

    def test_only_one_record_after_duplicate(self):
        utils.add_student("S01", "Ravi")
        utils.add_or_update_mark("S01", "Python", 82)
        utils.add_or_update_mark("S01", "Python", 95)
        marks = utils.load_marks()
        python_marks = [m for m in marks if m["subject"].lower() == "python"]
        self.assertEqual(len(python_marks), 1)
        self.assertEqual(python_marks[0]["marks"], 95)

    def test_duplicate_student_id_rejected(self):
        utils.add_student("S01", "Ravi")
        ok, msg = utils.add_student("S01", "Different Name")
        self.assertFalse(ok)
        self.assertIn("already exists", msg.lower())


# ─────────────────────────────────────────────────────────────────────────────
# TC06 — Missing / Non-existent Student
# ─────────────────────────────────────────────────────────────────────────────

class TC06_MissingStudent(GradebookTestCase):
    """
    Expected behavior:
      Query or add marks for a student that doesn't exist → clear error message.
    """

    def test_get_nonexistent_student_returns_none(self):
        result = utils.get_student("S99")
        self.assertIsNone(result)

    def test_student_summary_nonexistent_returns_error(self):
        ok, msg = utils.student_summary("S99")
        self.assertFalse(ok)
        self.assertIn("not found", msg.lower())

    def test_add_marks_nonexistent_student_rejected(self):
        ok, msg = utils.add_or_update_mark("S99", "Math", 75)
        self.assertFalse(ok)
        self.assertIn("not found", msg.lower())

    def test_delete_nonexistent_student_returns_error(self):
        ok, msg = utils.delete_student("S99")
        self.assertFalse(ok)
        self.assertIn("not found", msg.lower())


# ─────────────────────────────────────────────────────────────────────────────
# TC07 — Missing / Non-existent Subject
# ─────────────────────────────────────────────────────────────────────────────

class TC07_MissingSubject(GradebookTestCase):
    """
    Expected behavior:
      Query marks for a subject that has no entries → empty result (no crash).
      Delete a mark for a subject not assigned to a student → clear error.
    """

    def test_get_marks_for_nonexistent_subject_returns_empty(self):
        result = utils.get_marks_for_subject("Alchemy")
        self.assertEqual(result, [])

    def test_delete_mark_nonexistent_subject_returns_error(self):
        utils.add_student("S01", "Ravi")
        ok, msg = utils.delete_mark("S01", "Alchemy")
        self.assertFalse(ok)
        self.assertIn("no mark found", msg.lower())


# ─────────────────────────────────────────────────────────────────────────────
# TC08 — Input Validation Edge Cases
# ─────────────────────────────────────────────────────────────────────────────

class TC08_ValidationEdgeCases(GradebookTestCase):
    """Tests for validation helper functions directly."""

    def test_empty_student_id_rejected(self):
        ok, err = utils.validate_student_id("")
        self.assertFalse(ok)

    def test_whitespace_student_id_rejected(self):
        ok, err = utils.validate_student_id("   ")
        self.assertFalse(ok)

    def test_special_char_student_id_rejected(self):
        ok, err = utils.validate_student_id("S-01")
        self.assertFalse(ok)

    def test_empty_name_rejected(self):
        ok, err = utils.validate_name("")
        self.assertFalse(ok)

    def test_numeric_name_rejected(self):
        ok, err = utils.validate_name("123")
        self.assertFalse(ok)

    def test_empty_subject_rejected(self):
        ok, err = utils.validate_subject("")
        self.assertFalse(ok)

    def test_subject_with_special_chars_rejected(self):
        ok, err = utils.validate_subject("Math@101!")
        self.assertFalse(ok)


# ─────────────────────────────────────────────────────────────────────────────
# TC09 — Deletion Cascade
# ─────────────────────────────────────────────────────────────────────────────

class TC09_DeletionCascade(GradebookTestCase):
    """When a student is deleted, all their marks must also be removed."""

    def test_deleting_student_removes_marks(self):
        utils.add_student("S01", "Ravi")
        utils.add_or_update_mark("S01", "Python", 85)
        utils.add_or_update_mark("S01", "Math", 72)
        utils.add_student("S02", "Priya")
        utils.add_or_update_mark("S02", "Python", 90)

        ok, msg = utils.delete_student("S01")
        self.assertTrue(ok)

        # S01's marks should be gone, S02's should remain.
        remaining = utils.load_marks()
        s01_marks = [m for m in remaining if m["student_id"].upper() == "S01"]
        s02_marks = [m for m in remaining if m["student_id"].upper() == "S02"]
        self.assertEqual(len(s01_marks), 0)
        self.assertEqual(len(s02_marks), 1)


# ─────────────────────────────────────────────────────────────────────────────
# TC10 — Class Analytics Accuracy
# ─────────────────────────────────────────────────────────────────────────────

class TC10_ClassAnalytics(GradebookTestCase):
    """Verify that analytics calculations are numerically correct."""

    def setUp(self):
        super().setUp()
        # Seed predictable data.
        utils.add_student("S01", "Ravi")
        utils.add_student("S02", "Priya")
        utils.add_or_update_mark("S01", "Python", 80)  # A
        utils.add_or_update_mark("S01", "Math", 60)    # C  → avg 70 → B
        utils.add_or_update_mark("S02", "Python", 40)  # Fail → avg 40 → Fail
        utils.add_or_update_mark("S02", "Math", 90)    # A+  → avg 65 → C

    def test_subject_average_python(self):
        data = utils.class_analytics()
        python_avg = data["subject_stats"]["Python"]["average"]
        self.assertEqual(python_avg, 60.0)  # (80 + 40) / 2

    def test_subject_highest_lowest(self):
        data = utils.class_analytics()
        self.assertEqual(data["subject_stats"]["Python"]["highest"], 80)
        self.assertEqual(data["subject_stats"]["Python"]["lowest"], 40)

    def test_pass_fail_count(self):
        data = utils.class_analytics()
        # S01 avg=70 → B (pass), S02 avg=65 → C (pass)
        self.assertEqual(data["class_pass_count"], 2)
        self.assertEqual(data["class_fail_count"], 0)

    def test_top_performer_ranked_first(self):
        data = utils.class_analytics()
        # S01 avg=70, S02 avg=65 → S01 should be first
        self.assertEqual(data["top_performers"][0]["student_id"], "S01")

    def test_total_students_count(self):
        data = utils.class_analytics()
        self.assertEqual(data["total_students"], 2)


# ─────────────────────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
