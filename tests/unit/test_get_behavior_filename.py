#! /usr/bin/python

import unittest
import os
import parrot

class testget_behavior_filename(unittest.TestCase):
  def test_missing_environ_filename(self):
    filename = "/file/from/some/far/off/place/parrot_behaviors.json"
    os.environ[parrot.env_var_behavior_filename] = filename

    with self.assertRaises(parrot.ParrotMissingBehaviorFile):
      behavior_filename = parrot.get_behavior_filename()

    del os.environ[parrot.env_var_behavior_filename]

  def test_existing_environ_filename(self):
    filename = os.path.join(os.path.dirname(__file__), parrot.local_behavior_filename)
    fp = open(filename, "w")
    fp.close()
    os.environ[parrot.env_var_behavior_filename] = filename
    behavior_filename = parrot.get_behavior_filename()

    self.assertEqual(behavior_filename, filename)

    del os.environ[parrot.env_var_behavior_filename]
    os.remove(filename)


  def test_missing_locale_filename(self):
    with self.assertRaises(parrot.ParrotMissingBehaviorFile):
      behavior_filename = parrot.get_behavior_filename()

  def test_existing_locale_filename(self):
    # """Note: This test modifies the root directory of the parrot repo since the logic
    #    for local filenames is to have it be in the same dir as the parrot.py tool. The
    #    test does clean this up, but it does mean that unforseen circumstances could 
    #    leave a file in that directory.
    # """
    filename = os.path.join(os.path.dirname(parrot.__file__), parrot.local_behavior_filename)
    fp = open(filename, "w")
    fp.close()

    behavior_filename = parrot.get_behavior_filename()

    os.remove(filename)


if __name__ == "__main__":
  unitest.main();
