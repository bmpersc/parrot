#! /usr/bin/env bash

parrot_dir=$(dirname $(dirname $(pwd)))
export PYTHONPATH=$parrot_dir:$PYTHONPATH

python test.py -v
