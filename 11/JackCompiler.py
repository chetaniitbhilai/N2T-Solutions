import sys
import os
import JackTokenizer
import CompilationEngine

def compile_file(file_path):
    '''Compile a single Jack file and save the compiled output as a VM file.'''
    
    # Open the input file for reading
    with open(file_path, 'r') as ifile:
        # Extract the file name and path without extensions
        file_name = os.path.basename(file_path)
        file_path_no_ext, _ = os.path.splitext(file_path)
        file_name_no_ext, _ = os.path.splitext(file_name)

        # Define the output file path with a .vm extension
        ofile_path = file_path_no_ext + '.vm'
        # Open the output file for writing
        with open(ofile_path, 'w') as ofile:
            # Initialize the tokenizer to process the input Jack code
            tokenizer = JackTokenizer.JackTokenizer(ifile.read())
            # Initialize the compilation engine to generate VM code
            compiler = CompilationEngine.CompilationEngine(tokenizer, ofile)
            # Begin compiling the Jack class
            compiler.compile_class()

def compile_dir(dir_path):
    '''Compile all Jack files within a specified directory.'''
    for file in os.listdir(dir_path):
        # Construct the full path of each file in the directory
        file_path = os.path.join(dir_path, file)
        _, file_ext = os.path.splitext(file_path)
        # Process only files with a .jack extension
        if os.path.isfile(file_path) and file_ext.lower() == '.jack':
            compile_file(file_path)

def main():
    """The main function to handle file or directory input and initiate compilation."""
    if len(sys.argv) < 2:
        # Print usage instructions if no input is provided
        print(f'usage: {sys.argv[0]} (file|dir)')
        sys.exit(1)

    # Get the input file or directory path from command-line arguments
    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        # If the input is a directory, compile all Jack files in it
        compile_dir(input_path)
    elif os.path.isfile(input_path):
        # If the input is a single file, compile it
        compile_file(input_path)
    else:
        # Handle invalid input paths
        print("Invalid file/directory, compilation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
