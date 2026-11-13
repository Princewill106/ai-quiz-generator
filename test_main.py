import unittest
from pathlib import Path

import main


class QuizTests(unittest.TestCase):
    def test_facts_and_questions(self):
        fs = main.facts(Path("sample_notes.txt").read_text())
        self.assertGreaterEqual(len(fs), 7)
        self.assertEqual(fs[0]["term"], "Automation")
        qs = main.build(fs, 6)
        self.assertEqual(len(qs), 6)
        mcq = qs[0]
        self.assertIn(mcq["answer"], mcq["options"])
        self.assertEqual(len(set(mcq["options"])), 4)


if __name__ == "__main__":
    unittest.main()
