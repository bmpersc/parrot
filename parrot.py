#! /usr/bin/python

"""
  parrot is a tool for faking command line tools for testing scripts
  that depend on command line tools to do their work, but don't want
  to execute, or can't rely on proper behavior during testing.

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
  throw a "ParrotMissingBehaviorFile" exception. Parrot will not fall
  back to the parrot_behaviors file if PARROT_BEHAVIORS_FILE is not set.
  This is because parrot cannot properly report any issues since stdout
  and stderr are used by behaviors. Any error reporting done there could
  be mistaken as output for the expected behavior.
"""

import sys
import os
import json

env_var_behavior_filename = "PARROT_BEHAVIORS_FILE"
local_behavior_filename = "parrot_behaviors"

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

class ParrotException(Exception):
  pass

class ParrotMissingBehaviorFile(ParrotException):
  pass

class ParrotMalformedBehaviorFile(ParrotException):
  pass

class ParrotUnknownBehavior(ParrotException):
  pass

def object_to_behavior_hook(dct):
  try:
    new_behavior = behavior(dct["command"], dct["args"], dct["stdout"], dct["stderr"], dct["return_code"])
  except KeyError:
    raise ParrotMalformedBehaviorFile("Malformed behavior dictionary.")
  return new_behavior

def read_behaviors(behavior_fp):
  try:
    behavior_list = json.loads(behavior_fp.read(), object_hook=object_to_behavior_hook)
  except:
    raise ParrotMalformedBehaviorFile("Failed to read behaviors file")

  behavior_dict = {}
  for behavior in behavior_list:
    command_line = [behavior.command] + behavior.args
    identity = create_behavior_id(command_line)
    behavior_dict[identity] = behavior

  return behavior_dict

def get_behavior_filename():
  behavior_file = None
  if env_var_behavior_filename in os.environ:
    behavior_filename = os.environ[env_var_behavior_filename]
  else:
    behavior_filename = os.path.join(os.path.dirname(__file__), local_behavior_filename)

  if not os.path.exists(behavior_filename):
    raise ParrotMissingBehaviorFile(f"{behavior_filename} does not exist.")

  return behavior_filename

def create_behavior_id(argv):
  command = argv[0]
  if command.startswith("./"):
    command = command[2:]
  return " ".join([command] + argv[1:])

def parrot_main():
  import argparse
  parser = argparse.ArgumentParser(description=__doc__, usage="Do not use parrot.py directly",
                                   formatter_class=argparse.RawDescriptionHelpFormatter)

  options = parser.parse_args()
  
  sys.exit(0)

def behavior_main():
  id = create_behavior_id(sys.argv)
  behavior_filename = get_behavior_filename()
  behavior_file = open(behavior_filename, "r")
  behaviors = read_behaviors(behavior_file)

  if id not in behaviors:
    raise ParrotUnknownBehavior("No known behavior \"" + id + "\"")

  behavior = behaviors[id]
  behavior.execute()

if __name__ == "__main__":
  if sys.argv[0].endswith("parrot.py"):
    parrot_main()
  else:
    behavior_main()

