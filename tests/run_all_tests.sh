#! /usr/bin/env bash

cd unit
./run_tests.sh
unit_return=$?
cd ..

echo
echo "#############################"
echo

cd integration
./run_tests.sh
integration_return=$?
cd ..

let pass_fail=$unit_return+$integration_return

if [[ $pass_fail != 0 ]]; then
  echo
  echo "#############################"
fi

if [[ $unit_return != 0 ]]; then
  echo "Failure during unit tests."
fi

if [[ $integration_return != 0 ]]; then
  echo "Failure during integration tests."
fi

if [[ $pass_fail != 0 ]]; then
  echo "#############################"
fi

exit $pass_fail
