import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_repository import check


class RepositoryIntegrityTests(unittest.TestCase):
    def test_repository_integrity(self):
        self.assertEqual(check(), [])


if __name__ == '__main__':
    unittest.main()
