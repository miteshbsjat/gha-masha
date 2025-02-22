#!/usr/bin/env python3
import os
import sys
import subprocess

def on_err(exit_code, exit_message):
    with open(os.getenv('GITHUB_OUTPUT', '/tmp/masha.out'), 'a') as f:
        f.write(f"::set-output name=exit_code::{exit_code}\n")
        f.write(f"::set-output name=exit_message::{exit_message}\n")
    sys.exit(exit_code)

def get_parent_directory(file_path):
    # Get the parent directory using os.path.dirname
    parent_dir = os.path.dirname(file_path)
    
    # If the parent directory is an empty string, return the current working directory
    if parent_dir == '':
        return os.getcwd()
    
    return parent_dir

def get_related_output_file(input_file, output_dir):
    # Determine the relative path of the input file
    base_input_path = os.getenv('INPUT_INPUT_FILE')
    if base_input_path == input_file:
        return output_dir     # input is file, so output is file
    relative_path = get_parent_directory(input_file[len(base_input_path)+1:])
    # relative_path = "" if relative_path == "/" else relative_path
    # print(f"rel {input_file} : {relative_path}")
    
    # Construct the full output directory path
    full_output_dir = os.path.join(output_dir, relative_path)
    # print(f"full {full_output_dir} : {output_dir}")
    os.makedirs(full_output_dir, exist_ok=True)
    
    # Determine the output file path (remove .j2 extension)
    input_filename = os.path.basename(input_file)
    output_filename = os.path.splitext(input_filename)[0]
    output_file = os.path.join(full_output_dir, output_filename)
    # print(f"output_file = {output_file}")
    
    return output_file

def process_file(input_file, output_dir, cmd_base):
    output_file = get_related_output_file(input_file, output_dir)
    
    # Construct the full command for this file
    cmd = cmd_base + ["-o", output_file] + [input_file]
    
    # Print the command to be run
    print(f"Running: {' '.join(cmd)}")
    
    # Execute the command and capture output
    with open('/tmp/test.txt', 'w') as f:
        process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
        retval = process.wait()
    
    if retval != 0:
        with open('/tmp/test.txt', 'r') as f:
            last_line = f.readlines()[-1]
        on_err(retval, f"ERROR Occurred for {input_file}: {last_line.strip()}")
    else:
        # Copy the output from /tmp/test.txt to the actual output file
        return 0

def process_directory(input_dir, output_dir, cmd_base):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.j2'):
                input_file = os.path.join(root, file)
                process_file(input_file, output_dir, cmd_base)

# Define the base command
cmd_base = ["/app/bin/masha"]

# Check and append variables
input_variables = os.environ.get('INPUT_VARIABLES', None)
if not input_variables:
    on_err(1, "INPUT_VARIABLES is not set")

variables = ['-v', *input_variables.replace(',', " -v ").split(" ")]
cmd_base.extend(variables)

# Optionally append model file
model_file = os.environ.get('INPUT_MODEL_FILE', None)
if model_file:
    cmd_base.extend(['-m', model_file])

# Optionally append class model
class_model = os.getenv('INPUT_CLASS_MODEL')
if class_model:
    cmd_base.extend(['-c', class_model])

# Optionally append template filters directory
template_filters_directory = os.getenv('INPUT_TEMPLATE_FILTERS_DIRECTORY')
if template_filters_directory:
    cmd_base.extend(['-f', template_filters_directory])

# Optionally append template tests directory
template_tests_directory = os.getenv('INPUT_TEMPLATE_TESTS_DIRECTORY')
if template_tests_directory:
    cmd_base.extend(['-t', template_tests_directory])

# Check and set output directory
output_dir = os.getenv('INPUT_OUTPUT')
if not output_dir:
    on_err(1, "INPUT_OUTPUT is not set")

# Check if input file is a directory
input_file = os.getenv('INPUT_INPUT_FILE')
if not input_file:
    on_err(1, "INPUT_INPUT_FILE is not set")

if os.path.isdir(input_file):
    process_directory(input_file, output_dir, cmd_base)
else:
    process_file(input_file, output_dir, cmd_base)

on_err(0, "Completed Successfully")
