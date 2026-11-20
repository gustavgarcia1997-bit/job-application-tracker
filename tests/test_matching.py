"""Run with: python -m unittest discover -s tests -v"""
import json
import unittest

from matching import job_match, read_json, required_skills, split_skills


class TestMatching(unittest.TestCase):
    def test_75_percent(self):
        req = json.dumps({"skills": ["Python", "SQL", "Flask", "Linux"]})
        result = job_match(["Python", "SQL", "Linux"], req)
        self.assertEqual(result["score"], 75)
        self.assertEqual(result["missing"], ["Flask"])

    def test_case_insensitive_and_extra_whitespace(self):
        result = job_match(["  PYTHON ", "mySQL"], {"skills": ["python", "MYSQL"]})
        self.assertEqual(result["score"], 100)

    def test_no_required_skills(self):
        result = job_match(["Python"], {"skills": []})
        self.assertIsNone(result["score"])

    def test_zero_match(self):
        result = job_match(["Java"], {"skills": ["Python", "SQL"]})
        self.assertEqual(result["score"], 0)

    def test_no_duplicates(self):
        skills = split_skills("Python, python,  SQL, SQL, ")
        self.assertEqual(skills, ["Python", "SQL"])
        self.assertEqual(required_skills({"skills": ["Python", "PYTHON", "SQL"]}), ["Python", "SQL"])

    def test_bad_json_fails_safely(self):
        self.assertEqual(read_json("not json"), {})
        self.assertIsNone(job_match(["Python"], "not json")["score"])

    def test_skills_string_in_json(self):
        result = job_match(["SQL"], {"skills": "SQL, Python"})
        self.assertEqual(result["score"], 50)


if __name__ == "__main__":
    unittest.main()
