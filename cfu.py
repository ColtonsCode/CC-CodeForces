# Filename: cf_util.py
# Author: Colton Roe
# Created: 6/29/2025
# Description: Codeforces utility, a console utility for managing Codeforces problem solutions.

from io import TextIOWrapper
import subprocess
import argparse
import os

COMPILER_COMMAND = "gcc"
COMPILER_FLAGS = ""

PROBLEMS_PATH = r".\\problems"
LIBRARY_PATH = r".\\lib"
INCLUDE_PATH = os.path.join(LIBRARY_PATH, "include")
BUILD_PATH = r".\\build"

def main() -> None:
    """
    Utility entry point.
    """
    parser = argparse.ArgumentParser(
        description="Codeforces problem management utility",
        epilog="Use cf_util.py <command> --help for detailed help on each command")

    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
        required=True,
        help="Available commands")

    new_parser = subparsers.add_parser("new", help="Create a new problem folder")
    new_parser.add_argument("problem_name", help="Name of the new problem folder")

    build_parser = subparsers.add_parser("build", help="Build the problem file")
    build_parser.add_argument("problem_file_path", help="Path to the file to build")

    args = parser.parse_args()

    if args.command == "new":
        new_problem_command(args.problem_name)
    elif args.command == "build":
        build_problem_command(args.problem_file_path)

def new_problem_command(problem_name: str) -> None:
    """
    Creates a new problem folder with the specified name.
    """
    # Ensure the problems directory exists
    if not os.path.exists(PROBLEMS_PATH):
        os.makedirs(PROBLEMS_PATH)
        print(f"Created problems directory: {PROBLEMS_PATH}")

    os.makedirs(os.path.join(PROBLEMS_PATH, problem_name), exist_ok=True)
    print(f"Created new problem folder: {problem_name}")

def build_problem_command(problem_file_path: str) -> None:
    """
    Builds the specified problem file by merging custom headers and compiling it.
    """
    # If its not already an absolute path, convert it to one
    if not os.path.isabs(problem_file_path):
        problem_file_path = os.path.abspath(problem_file_path)

    # Ensure the file exists
    if not os.path.isfile(problem_file_path):
        print(f"Error: The file {problem_file_path} does not exist.")
        return

    # Ensure the lib directory exists
    if not os.path.exists(LIBRARY_PATH):
        os.makedirs(LIBRARY_PATH)
        print(f"Created library directory: {LIBRARY_PATH}")

    # Ensure the build directory exists
    if not os.path.exists(BUILD_PATH):
        os.makedirs(BUILD_PATH)
        print(f"Created build directory: {BUILD_PATH}")

    # Create a string to store the name of the file without the extension
    problem_name: str = os.path.splitext(os.path.basename(problem_file_path))[0]
    executable_path: str = os.path.join(BUILD_PATH, problem_name + ".exe")

    print(f"Building file: {problem_file_path}")

    # Now we actually need to "merge" the custom header files into the single problem c file.
    merged_file_path: str = os.path.join(BUILD_PATH, problem_name + "_merged.c")
    merge_include_files(problem_file_path, merged_file_path)

    # Run the compiler command
    # Note: This assumes the compiler is gcc and the file is a C source file.
    result = subprocess.run(
        [COMPILER_COMMAND, merged_file_path, "-o", executable_path, "-I", INCLUDE_PATH],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"Build successful: {executable_path}")
    else:
        print(f"Build failed with error:\n{result.stderr}")

def merge_include_files(problem_file_path: str, output_file_path: str) -> None:
    """
    Merges custom header files and their corresponding C files into a single output file.
    """
    # Open both files at the top level to avoid double indentation
    with open(problem_file_path, 'r') as problem_file, open(output_file_path, 'w') as output_file:
        output_file.write(f"//BEGIN MAIN FILE: {problem_file_path}\n")
        merge_include_files_helper(problem_file, output_file, [])
        output_file.write(f"\n//END MAIN FILE: {problem_file_path}")

    print(f"Merged include files into: {output_file_path}")

def merge_include_files_helper(file_to_merge : TextIOWrapper, 
                               output_file : TextIOWrapper, 
                               seen_headers : list[str]) -> None:
    """
    Helper function to recursively merge headers, avoiding infinite loops.
    """
    for line in file_to_merge:
        # If the line is only whitespace, skip it
        if not line.strip():
            continue

        if not line.startswith('#include "'):
            output_file.write(line)
            continue

        header_name = line.strip().split('"')[1]
        if header_name in seen_headers:
            continue
        
        seen_headers.append(header_name)
        header_path = os.path.join(INCLUDE_PATH, header_name)

        if not os.path.isfile(header_path):
            print(f"Warning: Header file {header_path} not found in {INCLUDE_PATH}.")
            continue

        with open(header_path, 'r') as header_file:
            output_file.write(f"//BEGIN HEADER: {header_path}\n")
            merge_include_files_helper(header_file, output_file, seen_headers)
            output_file.write(f"\n//END HEADER: {header_path}\n")
                
            # Now that the header is written we can write the C file.
            c_file_path = os.path.join (LIBRARY_PATH, header_name.replace('.h', '.c'))

            if not os.path.exists(c_file_path):
                print(f"Warning: C file {c_file_path} not found in {LIBRARY_PATH}.")
                continue

            with open(c_file_path, 'r') as c_file:
                output_file.write(f"//BEGIN C FILE: {c_file_path}\n")
                merge_include_files_helper(c_file, output_file, seen_headers)
                output_file.write(f"\n//END C FILE: {c_file_path}\n")

if __name__ == "__main__":
    main()