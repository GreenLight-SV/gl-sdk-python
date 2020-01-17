#!/bin/bash
set -e
PYTHON="/usr/local/bin/python3"

export GL_STAGE=staging
# export GL_APIKEY={yourapikey}

for f in [0-9]*.py
do
  $PYTHON $f
done
