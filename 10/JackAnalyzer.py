import sys  # Used to handle command-line arguments
import re  # Used for regular expression operations
from os import listdir  # Used to list directory contents
from os.path import isfile, isdir  # Used to check if paths are files or directories
from CompilationEngine import CompilationEngine  # Imports CompilationEngine module

# Constants
INVALID_ARGS = "The file given as input is invalid..."  # Error message for invalid input
NUMBER_OF_ARGS = 2  # Expected number of command-line arguments
XML_SUFFIX = ".xml"  # Output file extension
VM_SUFFIX = ".vm"  # (Unused here; might be part of future implementation)
JACK_SUFFIX = ".jack$"  # Pattern for .jack files
VALID_INPUT_SUFFIX = ".*\.jack$"  # Regular expression for matching .jack files
JACK_SUFFIX_PATTERN = re.compile(VALID_INPUT_SUFFIX)  # Compiled regex pattern for .jack files
COMMENT = "//.*$"  # Pattern for comments (unused in this script)

def get_files(args):

    list_of_files_path = []
    if len(args) == NUMBER_OF_ARGS:  # Check for correct number of arguments
        if isfile(args[1]) and JACK_SUFFIX_PATTERN.match(args[1]):  # If argument is a file
            list_of_files_path.append(args[1])  # Add file to list if it matches .jack extension
        elif isdir(args[1]):  # If argument is a directory
            for file in listdir(args[1]):  # Iterate over files in the directory
                if JACK_SUFFIX_PATTERN.match(file):  # Check if file is a .jack file
                    list_of_files_path.append(args[1] + "/" + file)  # Add file to list
        return list_of_files_path  # Return list of .jack file paths
    else:
        print(INVALID_ARGS)  # Print error if argument count is invalid
        exit()  # Terminate program

def file_output_path(file_path):

    temp_path = re.sub(JACK_SUFFIX, XML_SUFFIX, file_path)  # Replace .jack with .xml
    return temp_path

# The main program:
if __name__ == "__main__":
    list_of_files_path = get_files(sys.argv)  # Get list of .jack files from input arguments
    for file_path in list_of_files_path:  # Iterate over all .jack file paths
        current_code = CompilationEngine(file_path, file_output_path(file_path))  # Create CompilationEngine instance
        current_code.compileClass()  # Call compileClass() to process and generate output
