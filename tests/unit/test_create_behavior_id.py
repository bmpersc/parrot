#! /usr/bin/python

import unittest
import parrot

class testcreate_behavior_id(unittest.TestCase):
  def test_simple(self):
    args=["ls"]
    id = parrot.create_behavior_id(args)
    self.assertEqual(id, args[0])

  def test_arg_list(self):
    args=["ls", "-lhs", ".."]
    id = parrot.create_behavior_id(args)
    self.assertEqual(id, "ls -lhs ..")

  def test_arg_list_reordering(self):
    args1=["echo", "hello", "world"]
    args2=["echo", "world", "hello"]
    id1 = parrot.create_behavior_id(args1)
    id2 = parrot.create_behavior_id(args2)
    self.assertNotEqual(id1, id2)


if __name__ == "__main__":
  unitest.main();
