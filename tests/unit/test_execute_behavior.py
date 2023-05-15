#! /usr/bin/python

import unittest
import io
import parrot

class save_exit_code():
  """class to catch the exit of a behavior without ending the tests prematurely."""
  def __init__(self):
    self.exit_code = None

  def exit(self, val):
    self.exit_code = val

class testexecute_behavior(unittest.TestCase):
  def setUp(self):
    self.str_stdout = io.StringIO()
    self.str_stderr = io.StringIO()
    self.exit_catcher = save_exit_code()

  def tearDown(self):
    self.str_stdout.close()
    self.str_stderr.close()

  def test_ls_no_such_files_fail(self):
    ls_stderr = "ls: cannot access '*.cc': No such file or directory"
    ls_behavior = parrot.behavior("ls", ["*.cc"], "", ls_stderr, 2)
    
    ls_behavior.execute(stdout_fp=self.str_stdout,
                        stderr_fp=self.str_stderr,
                        exit_call=self.exit_catcher.exit)

    self.assertEqual(self.str_stdout.getvalue(), "")
    self.assertEqual(self.str_stderr.getvalue(), ls_stderr)
    self.assertEqual(self.exit_catcher.exit_code, 2)

  def test_ls_empty_success(self):
    ls_behavior = parrot.behavior("ls", [], "", "", 0)
    
    ls_behavior.execute(stdout_fp=self.str_stdout,
                        stderr_fp=self.str_stderr,
                        exit_call=self.exit_catcher.exit)

    self.assertEqual(self.str_stdout.getvalue(), "")
    self.assertEqual(self.str_stderr.getvalue(), "")
    self.assertEqual(self.exit_catcher.exit_code, 0)

  def test_grep_stderr_stdout_fail(self):
    grep_stdout = "test:1:hi there!"
    grep_stderr = "grep: neat_file: No such file or directory"
    ls_behavior = parrot.behavior("grep", ["-niRI", '"hi"'], grep_stdout, grep_stderr, 2)
    
    ls_behavior.execute(stdout_fp=self.str_stdout,
                        stderr_fp=self.str_stderr,
                        exit_call=self.exit_catcher.exit)

    self.assertEqual(self.str_stdout.getvalue(), grep_stdout)
    self.assertEqual(self.str_stderr.getvalue(), grep_stderr)
    self.assertEqual(self.exit_catcher.exit_code, 2)

  def test_grep_multiline_stdout_success(self):
    grep_stdout = """1:hi there!
2:hello joe."""
    grep_stderr = ""
    ls_behavior = parrot.behavior("grep", ["-niRI", '"hi|hello"'], grep_stdout, grep_stderr, 0)
    
    ls_behavior.execute(stdout_fp=self.str_stdout,
                        stderr_fp=self.str_stderr,
                        exit_call=self.exit_catcher.exit)

    self.assertEqual(self.str_stdout.getvalue(), grep_stdout)
    self.assertEqual(self.str_stderr.getvalue(), grep_stderr)
    self.assertEqual(self.exit_catcher.exit_code, 0)

  def test_no_args_success(self):
    true_behavior = parrot.behavior("true", [], "", "", 0)

    true_behavior.execute(stdout_fp=self.str_stdout,
                          stderr_fp=self.str_stderr,
                          exit_call=self.exit_catcher.exit)

    self.assertEqual(self.str_stdout.getvalue(), "")
    self.assertEqual(self.str_stderr.getvalue(), "")
    self.assertEqual(self.exit_catcher.exit_code, 0)

  def test_no_args_fail(self):
    false_behavior = parrot.behavior("false", [], "", "", 1)

    false_behavior.execute(stdout_fp=self.str_stdout,
                           stderr_fp=self.str_stderr,
                           exit_call=self.exit_catcher.exit)

    self.assertEqual(self.str_stdout.getvalue(), "")
    self.assertEqual(self.str_stderr.getvalue(), "")
    self.assertEqual(self.exit_catcher.exit_code, 1)

if __name__ == "__main__":
  unitest.main();
