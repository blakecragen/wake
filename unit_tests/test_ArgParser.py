import unittest
import os
import sys

# Ensure parent directory is in path so ArgParser can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ArgParser import ArgParser


class TestArgParser(unittest.TestCase):

    def setUp(self):
        # Locate the args.json file relative to project root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        json_path = os.path.join(base_dir, "args.json")
        self.parser = ArgParser(json_path).build()

    def test_Host_Only(self):
        args = self.parser.parse_args(["myhost"])
        self.assertEqual(args.name, "myhost")
        self.assertFalse(args.list)

    def test_List_Flag(self):
        args = self.parser.parse_args(["--list"])
        self.assertTrue(args.list)
        self.assertIsNone(args.name)
        args = self.parser.parse_args(["--l"])
        self.assertTrue(args.list)
        self.assertIsNone(args.name)

    def test_Post_Flag(self):
        args = self.parser.parse_args(["myhost", "--port", "1234"])
        self.assertEqual(args.name, "myhost")
        self.assertEqual(args.port, 1234)

    def test_Multiple_Input_Orders(self):
        args1 = self.parser.parse_args(["boulder01", "--ssh", "HomePi", "--port", "1234"])
        args2 = self.parser.parse_args(["--port", "1234", "boulder01", "--ssh", "HomePi"])
        args3 = self.parser.parse_args(["--port", "1234", "--ssh", "HomePi", "boulder01"])
        # Matches args2
        self.assertEqual(args1.ssh, args2.ssh)
        self.assertEqual(args1.port, args2.port)
        self.assertEqual(args1.name, args2.name)
        # Matches args 3
        self.assertEqual(args1.ssh, args3.ssh)
        self.assertEqual(args1.port, args3.port)
        self.assertEqual(args1.name, args3.name)

if __name__ == "__main__":
    unittest.main()
