#!/usr/bin/env bash

if [ -z "$GITHUB_OUTPUT" ]; then
  GITHUB_OUTPUT="/tmp/masha.out"
fi

function on_err() {
  echo "::set-output name=exit_code::$1"
  echo "::set-output name=exit_message::$2"
  exit $1
}

# Use INPUT_<INPUT_NAME> to get the value of an input
cmd="/app/bin/masha"
if [ -z "$INPUT_VARIABLES" ]; then on_err 1 "INPUT_VARIABLES is not set"; fi 
variables=$(echo "-v $INPUT_VARIABLES" | sed 's/,/ -v /g')
cmd="$cmd $variables"

if [ ! -z "$INPUT_MODEL_FILE" ]; then 
  cmd="$cmd -m $INPUT_MODEL_FILE"
fi

if [ ! -z "$INPUT_CLASS_MODEL" ]; then 
  cmd="$cmd -c $INPUT_CLASS_MODEL"
fi

if [ ! -z "$INPUT_TEMPLATE_FILTERS_DIRECTORY" ]; then 
  cmd="$cmd -f $INPUT_TEMPLATE_FILTERS_DIRECTORY"
fi

if [ ! -z "$INPUT_TEMPLATE_TESTS_DIRECTORY" ]; then 
  cmd="$cmd -t $INPUT_TEMPLATE_TESTS_DIRECTORY"
fi

if [ -z "$INPUT_OUTPUT" ]; then on_err 1 "INPUT_OUTPUT is not set"; fi 
cmd="$cmd -o $INPUT_OUTPUT"

if [ -z "$INPUT_INPUT_FILE" ]; then on_err 1 "INPUT_INPUT_FILE is not set"; fi 
cmd="$cmd $INPUT_INPUT_FILE"

# Use workflow commands to do things like set debug messages
echo "Running: $cmd"

eval "$cmd" 2>&1 | tee /tmp/test.txt
retval=${PIPESTATUS[0]}
if [ $retval -ne 0 ]; then
  on_err $retval "ERROR Occurred: $(tail -1 /tmp/test.txt)"
else
  on_err 0 "Completed Successfully"
fi

