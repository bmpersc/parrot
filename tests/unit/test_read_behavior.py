#! /usr/bin/python

import unittest
import io
import parrot

class testobject_to_behavior_hook(unittest.TestCase):
  def test_hook_no_behavior(self):
    dct = {"Todo": "list",
           "shopping": True,
          }

    with self.assertRaises(parrot.ParrotMalformedBehaviorFile):
      behavior = parrot.object_to_behavior_hook(dct)

  def test_hook_simple_behavior(self):
    dct = {"command": "echo",
           "args": ["Hello", "world!"],
           "stdout": "Hello world!",
           "stderr": "",
           "return_code": 0
          }

    behavior = parrot.object_to_behavior_hook(dct)

    self.assertEqual(behavior.command,       dct["command"])
    self.assertEqual(behavior.args,          dct["args"])
    self.assertEqual(behavior.stdout_output, dct["stdout"])
    self.assertEqual(behavior.stderr_output, dct["stderr"])
    self.assertEqual(behavior.return_code,   dct["return_code"])


class testread_behavior(unittest.TestCase):
  def setUp(self):
    self.json_fp = io.StringIO()

  def tearDown(self):
    self.json_fp.close()

  def populate_json_fp(self, str):
    self.json_fp.write(str)
    self.json_fp.seek(0)

  def test_single_behavior(self):
    json_str = """[
                    {"command": "echo",
                     "args": ["Hello", "world!"],
                     "stdout": "Hello world!",
                     "stderr": "",
                     "return_code": 0
                    }
                  ]"""
    self.populate_json_fp(json_str)
    behaviors = parrot.read_behaviors(self.json_fp)

    key = parrot.create_behavior_id(["echo", "Hello", "world!"])
    self.assertEqual(len(behaviors), 1)
    self.assertEqual(behaviors[key].command, "echo")
    self.assertEqual(behaviors[key].args, ["Hello", "world!"])
    self.assertEqual(behaviors[key].stdout_output, "Hello world!")
    self.assertEqual(behaviors[key].stderr_output, "")
    self.assertEqual(behaviors[key].return_code, 0)

  def test_multiple_behaviors(self):
    json_str = """[
                    {"command": "echo",
                     "args": ["Hello", "world!"],
                     "stdout": "Hello world!",
                     "stderr": "",
                     "return_code": 0
                    },
                    {"command": "ls",
                     "args": ["*.cc"],
                     "stdout": "",
                     "stderr": "ls: cannot access '*.cc': No such file or directory",
                     "return_code": 2
                    },
                    {"command": "grep",
                     "args": ["-niRI", "hi"],
                     "stdout": "test:1:hi there!",
                     "stderr": "grep: test2: No such file or directory",
                     "return_code": 2
                    }
                  ]"""
    self.populate_json_fp(json_str)
    behaviors = parrot.read_behaviors(self.json_fp)

    self.assertEqual(len(behaviors), 3)

    key1 = parrot.create_behavior_id(["echo", "Hello", "world!"])
    self.assertEqual(behaviors[key1].command, "echo")
    self.assertEqual(behaviors[key1].args, ["Hello", "world!"])
    self.assertEqual(behaviors[key1].stdout_output, "Hello world!")
    self.assertEqual(behaviors[key1].stderr_output, "")
    self.assertEqual(behaviors[key1].return_code, 0)

    key2 = parrot.create_behavior_id(["ls", "*.cc"])
    self.assertEqual(behaviors[key2].command, "ls")
    self.assertEqual(behaviors[key2].args, ["*.cc"])
    self.assertEqual(behaviors[key2].stdout_output, "")
    self.assertEqual(behaviors[key2].stderr_output, "ls: cannot access '*.cc': No such file or directory")
    self.assertEqual(behaviors[key2].return_code, 2)

    key3 = parrot.create_behavior_id(["grep", "-niRI", "hi"])
    self.assertEqual(behaviors[key3].command, "grep")
    self.assertEqual(behaviors[key3].args, ["-niRI", "hi"])
    self.assertEqual(behaviors[key3].stdout_output, "test:1:hi there!")
    self.assertEqual(behaviors[key3].stderr_output, "grep: test2: No such file or directory")
    self.assertEqual(behaviors[key3].return_code, 2)

  def test_malformed_json(self):
    json_str = """[
                    {"pickle": "echo",
                     "relish": ["Hello", "world!"],
                     "beet": "Hello world!",
                     "banana": "",
                     "bar_code": 0
                    }
                  ]"""
    self.populate_json_fp(json_str)
    with self.assertRaises(parrot.ParrotMalformedBehaviorFile):
      behaviors = parrot.read_behaviors(self.json_fp)

  def test_empty_json(self):
    with self.assertRaises(parrot.ParrotMalformedBehaviorFile):
      behaviors = parrot.read_behaviors(self.json_fp)

if __name__ == "__main__":
  unitest.main();
