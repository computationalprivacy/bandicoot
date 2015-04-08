import bandicoot as bc
import unittest
from testing_tools import parse_dict, file_equality, metric_suite, compare_dict
import tempfile
import os
from collections import OrderedDict as OD

class TestExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestExport._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestExport._dir_changed = True

    def test_different_keys(self):
        tmp_file = tempfile.NamedTemporaryFile()
        dict1 = {"x": 1, "y": 2, "z": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        bc.io.to_csv([dict1, dict2], tmp_file.name)
        self.assertTrue(file_equality(tmp_file.name, "samples/to_csv_different_keys.csv"))

    def test_same_keys(self):
        tmp_file = tempfile.NamedTemporaryFile()
        dict1 = {"a": 1, "b": 2, "c": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        bc.io.to_csv([dict1, dict2], tmp_file.name)
        self.assertTrue(file_equality(tmp_file.name, "samples/to_csv_same_keys.csv"))

    def test_different_json(self):
        tmp_file = tempfile.NamedTemporaryFile()
        dict1 = {"name": "dict1", "x": 1, "y": 2, "z": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"name": "dict2", "a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        bc.io.to_json([dict1, dict2], tmp_file.name)
        self.assertTrue(file_equality(tmp_file.name, "samples/to_json_different_keys.json"))

    def test_different_json(self):
        tmp_file = tempfile.NamedTemporaryFile()
        dict1 = {"name": "dict1", "a": 1, "b": 2, "c": 3}
        dict1 = OD(sorted(dict1.items(), key=lambda t: t[0]))

        dict2 = {"name": "dict2", "a": 4, "b": 5, "c": 6}
        dict2 = OD(sorted(dict2.items(), key=lambda t: t[0]))

        bc.io.to_json([dict1, dict2], tmp_file.name)
        self.assertTrue(file_equality(tmp_file.name, "samples/to_json_same_keys.json"))
