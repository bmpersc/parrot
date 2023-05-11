#! /usr/bin/python

"""
  parrot is a tool for faking command line tools for testing scripts
  that depend on command line tools to do their work, but don't want
  to, or can't rely on proper behavior during testing.

  This is accomplished by placing parrot, renamed or symlinked to 
  the command you want to fake, ahead of the real command in the PATH.
  Parrot will then compare how it is called to a specified list of
  behaviors and will report to stderr and stdout what is defined in the
  proper behavior.

  Parrot will look for the file that contains the behaviors it can fake 
  first if the environment variable "PARROT_BEHAVIORS_FILE" is set it
  will use the file given. If the environment variable is not set then
  parrot will look in the directory where parrot is located for a file
  named: "parrot_behaviors" If either file doesn't exist parrot will 
  throw a "MissingBehaviorFile" exception. Parrot will not fall back to
  the parrot_behaviors file if PARROT_BEHAVIORS_FILE is not set. This is
  because parrot cannot properly report any issues since stdout and stderr
  are used by behaviors. Any error reporting done there could be mistaken
  as output for the expected behavior.
"""

import sys
import json

class behavior:
  def __init__(self):
    self.command = ""
    self.args = []
    self.stdout_output = "Default stdout."
    self.stderr_output = "Default stderr."
    self.return_code = 0
    self.id = "Unidentified"

  def __init__(self, _command, _args, _stdout, _stderr="", _return_code=0):
    self.command = _command
    self.args = _args
    self.stdout_output = _stdout
    self.stderr_output = _stderr
    self.return_code = _return_code
    self.id = create_behavior_id([self.command] + self.args)

  def execute(self, stdout_fp=sys.stdout, stderr_fp=sys.stderr, exit_call=sys.exit):
    stdout_fp.write(self.stdout_output)
    stderr_fp.write(self.stderr_output)
    exit_call(self.return_code)

def create_behavior_id(argv):
  return " ".join(argv)

def parrot_main():
  import argparse
  parser = argparse.ArgumentParser(description=__doc__, usage="Do not use parrot.py directly",
                                   formatter_class=argparse.RawDescriptionHelpFormatter)

  options = parser.parse_args()
  
  sys.exit(0)

def behavior_main():
  id = create_behavior_id(sys.argv)
  print(f"\"{id}\"")

if __name__ == "__main__":
  if sys.argv[0].endswith("parrot.py"):
    parrot_main()
  else:
    behavior_main()

