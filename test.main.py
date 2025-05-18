import unittest
import os
import json
from main import read_json, write_json

class TestJSONFunctions(unittest.TestCase):
    def setUp(self):
        self.test_filename = "test.json"
        self.test_data = [{"id": 1, "name": "Example"}]
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def tearDown(self):
        try:
            os.remove(os.path.join(self.data_dir, self.test_filename))
        except FileNotFoundError:
            pass

    def test_write_json_creates_file(self):
        write_json(self.test_filename, self.test_data)
        path = os.path.join(self.data_dir, self.test_filename)
        self.assertTrue(os.path.exists(path))

    def test_read_json_returns_data(self):
        write_json(self.test_filename, self.test_data)
        data = read_json(self.test_filename)
        self.assertEqual(data, self.test_data)

    def test_read_json_nonexistent_returns_empty(self):
        data = read_json("nonexistent.json")
        self.assertEqual(data, [])

if __name__ == "__main__":
    unittest.main()
