#! /usr/bin/env bash

#defining commands that are needed so we can avoid conflicts with potential
#parrot definitions.
system_grep=$(which grep)
system_rm=$(which rm)
system_cp=$(which cp)
system_ln=$(which ln)
system_which=$(which which)

test_num=0
failure_count=0
expected_stdout=""
expected_stderr=""
expected_return_code=0

function clean_up_old_files(){
  $system_rm -f stdout.test_*
  $system_rm -f stderr.test_*
  $system_rm -f parrot_behaviors
}

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
  pass_fail=$1
  expected_stdout=""
  expected_stderr=""
  expected_return_code=0

  if [[ $pass_fail != 0 ]]; then
    $system_cp stdout stdout.test_$test_num
    $system_cp stderr stderr.test_$test_num
  fi

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
    echo "PASS: $test_num ($command $args)"
  else
    echo "FAIL: $test_num ($command $args)[$stdout_return, $stderr_return, $return_val]"
  fi

  tear_down $pass_fail

  let failure_count=$failure_count+$pass_fail
  return $pass_fail
}

#set PATH to only the current directory to avoid accidentally running the actual commands.
old_path=$PATH
export PATH=.

clean_up_old_files
setup_behaviors_file 1

####################################################################
expected_stdout=""
expected_stderr="ls: cannot access 'fred.cc': No such file or directory"
expected_return_code=2
run_test ls fred.cc
####################################################################

####################################################################
expected_stdout="ls  parrot_behaviors.1  run_tests.sh"
expected_stderr=""
expected_return_code=0
run_test ls
####################################################################

####################################################################
expected_stdout=""
expected_stderr="grep: test: No such file or directory"
expected_return_code=2
run_test grep -ni hi test
####################################################################

####################################################################
expected_stdout="^12:   \"return_code\": 0$"
expected_stderr=""
expected_return_code=0
run_test grep -ni return parrot_behaviors

expected_stdout="^24:   \"return_code\": 2$"
expected_stderr=""
expected_return_code=0
run_test grep -ni return parrot_behaviors
####################################################################

####################################################################
expected_stdout="test:1:hi"
expected_stderr="grep: test2: No such file or directory"
expected_return_code=2
run_test grep -ni hi "test*"
####################################################################

tear_down_behaviors_file

echo "$test_num tests run."
echo "$failure_count tests failed"

#restore PATH
export PATH=$old_path

exit $failure_count
