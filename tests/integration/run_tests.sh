#! /usr/bin/env bash

#defining commands that are needed so we can avoid conflicts with potential
#parrot definitions.
system_grep=$(which grep)
system_rm=$(which rm)
system_ln=$(which ln)
system_which=$(which which)

test_num=0
failure_count=0
expected_stdout=""
expected_stderr=""
expected_return_code=0

function setup_behaviors_file(){
  version=$1
  $system_rm -f parrot_behaviors
  $system_ln -s parrot_behaviors.$1 parrot_behaviors
}

function tear_down_behaviors_file(){
  $system_rm -f parrot_behaviors
}

function setup(){
  let test_num=$test_num+1
}

function tear_down(){
  expected_stdout=""
  expected_stderr=""
  expected_return_code=0
  $system_rm -f stdout
  $system_rm -f stderr
}

function check_file(){
  filename=$1
  expected_value=$2

  if [ -n "$expected_value" ]; then
    #expected_value is not empty so check the file for its contents
    $system_grep -q "$expected_value" $filename
    return_value=$?
  else
    #expected_value is the empty string so the file should be empty for success.
    if [[ ! -s $filename ]]; then
      return_value=0
    else
      return_value=1
    fi
  fi

  return $return_value
}

function run_test(){
  local command=$1
  shift
  local args=$@
  local pass_fail=1

  setup

  $command $args 1>stdout 2>stderr
  return_val=$?

  check_file stdout "$expected_stdout"
  stdout_return=$?
  check_file stderr "$expected_stderr"
  stderr_return=$?

  if [[ $stdout_return == 0 && $stderr_return == 0 && $return_val == $expected_return_code ]]; then
    pass_fail=0
    echo "PASS: $test_num"
  else
    echo "FAIL: $test_num ($command $args)[$stdout_return, $stderr_return, $return_val]"
  fi

  tear_down

  let failure_count=$failure_count+$pass_fail
  return $pass_fail
}

#set PATH to only the current directory to avoid accidentally running the actual commands.
old_path=$PATH
export PATH=.

setup_behaviors_file 1

####################################################################
expected_stdout=""
expected_stderr="ls: cannot access 'fred.cc': No such file or directory"
expected_return_code=2
run_test ls fred.cc
####################################################################


tear_down_behaviors_file

echo "$test_num tests run."
echo "$failure_count tests failed"

#restore PATH
export PATH=$old_path

exit $failure_count
