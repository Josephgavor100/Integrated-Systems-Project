import unittest
from models import User, InvalidIDError, WeakPasswordError, HealthTask


class TestPasswordStrength(unittest.TestCase):
    """Per brief: 'Password strength... testing' is an explicit Week 4 requirement."""

    def test_short_password_rejected(self):
        with self.assertRaises(WeakPasswordError):
            User("Test", "12345678", "ab")


class TestNonDiagnosticScopeCompliance(unittest.TestCase):
    """
    Per brief: ClinicCare-Lite 'must remain strictly administrative/logistic;
    no automated diagnostic... functions permitted.' This test checks that
    HealthTask categories are administrative labels only, never medical ones.
    """

    def test_categories_are_administrative_not_medical(self):
        medical_sounding_terms = {"diagnosed", "prescribed", "treatment_plan"}
        overlap = medical_sounding_terms & HealthTask.VALID_CATEGORIES
        self.assertEqual(overlap, set(),
            "Category set must not contain medical/diagnostic language")


class TestIDValidation(unittest.TestCase):

    def test_valid_id_accepted(self):
        user = User("Test", "12345678", "password123")
        self.assertEqual(user.id_number, "12345678")

    def test_short_id_rejected(self):
        with self.assertRaises(InvalidIDError):
            User("Test", "123", "password123")

    def test_non_numeric_id_rejected(self):
        with self.assertRaises(InvalidIDError):
            User("Test", "ABCD1234", "password123")


class TestTaskCategoryTransitions(unittest.TestCase):
    """Per brief: 'invalid status transitions' testing (borrowed language
    from the GridCare side of the brief, but the same principle applies here)."""

    def test_invalid_category_rejected(self):
        task = HealthTask(1, "12345678", "Sample request")
        with self.assertRaises(ValueError):
            task.update_category("diagnosed_with_flu")  # not a valid category

    def test_resolving_stamps_timestamp(self):
        task = HealthTask(1, "12345678", "Sample request")
        self.assertIsNone(task.resolved_at)
        task.update_category("resolved")
        self.assertIsNotNone(task.resolved_at)


if __name__ == '__main__':
    unittest.main()