import os

import sys


class Parser:
    def __init__(self, input_file):
        self.file = open(input_file, 'r')  # Opening the file
        self.commands = self.file.readlines()  # Reading the file
        self.current_command = None  # Current command declaration
        self.current_index = 0  # Current index set to 0

    def hasMoreCommands(self):
        return self.current_index < len(self.commands)  # Checking if there are more commands to translate

    def advance(self):
        while self.hasMoreCommands():  # Advance when there are more commands to translate
            line = self.commands[self.current_index].strip()  # Fetching that index line
            self.current_index += 1  # Increasing the index value
            if line and not line.startswith("//"):  # Checking if it is a comment or not
                self.current_command = line.split("//")[0].strip()  # Storing that command in the current command
                break

    def commandType(self):
        if self.current_command.startswith("push"):  # Checking for push
            return "C_PUSH"
        elif self.current_command.startswith("pop"):  # Checking for pop
            return "C_POP"
        elif self.current_command.startswith("if-goto"):
            return "C_IF"
        elif self.current_command.startswith("goto"):
            return "C_GOTO"
        elif self.current_command.startswith("label"):
            return "C_LABEL"
        elif self.current_command.startswith("function"):
            return "C_FUNCTION"
        elif self.current_command.startswith("call"):
            return "C_CALL"
        elif self.current_command.startswith("return"):
            return "C_RETURN"
        elif any(self.current_command.startswith(cmd) for cmd in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]):
            return "C_ARITHMETIC"
        else:
            return None

    def arg1(self):
        if self.commandType() == "C_ARITHMETIC":
            return self.current_command
        return self.current_command.split()[1]

    def arg2(self):
        if self.commandType() in ["C_PUSH", "C_POP", "C_CALL", "C_FUNCTION"]:
            return int(self.current_command.split()[2])

    def close(self):
        self.file.close()  # Closing the file after reading



class CodeWriter:
    """Translates VM commands into Hack assembly code and writes them to an output file."""

    def __init__(self, file_name: str):
        """Initialize the writer with an output file setup."""
        self.file = open(file_name, "w")
        self.file_name = ""
        self.function_name = "OS"
        self.label_counter = 0
        self.symbols = {
            "add": "M=D+M", "sub": "M=M-D", "and": "M=D&M", "or": "M=D|M",
            "neg": "M=-M", "not": "M=!M", "eq": "D;JEQ", "gt": "D;JGT", "lt": "D;JLT",
            "local": "@LCL", "argument": "@ARG", "this": "@THIS", "that": "@THAT",
            "constant": "", "static": "", "pointer": "@3", "temp": "@5"
        }

    def write_init(self):
        """Write the bootstrap code that initializes the VM."""
        self.write_to_file([
            "@256", "D=A", "@SP", "M=D"
        ])
        self.write_function("OS", 0)
        self.write_call("Sys.init", 0)

    def set_file_name(self, file_name: str):
        """Update the current file name for static variable labeling."""
        self.file_name = file_name

    def comment(self, text: str):
        """Write a comment in the output file."""
        self.write_to_file([f"// {text}"], False)

    def write_arithmetic(self, command: str):
        """Translate and write assembly for arithmetic commands."""
        output = []
        if command in {"add", "sub", "and", "or"}:
            output.extend([
                "@SP", "AM=M-1", "D=M", "@SP", "A=M-1", self.symbols[command]
            ])
        elif command in {"neg", "not"}:
            output.extend(["@SP", "A=M-1", self.symbols[command]])
        elif command in {"eq", "gt", "lt"}:
            jump_label = f"CompLabel{self.label_counter}"
            self.label_counter += 1
            output.extend([
                "@SP", "AM=M-1", "D=M", "@SP", "A=M-1", "D=M-D",
                "M=-1", f"@{jump_label}", self.symbols[command],
                "@SP", "A=M-1", "M=0", f"({jump_label})"
            ])
        else:
            raise ValueError("Unsupported Arithmetic Command")

        self.write_to_file(output)

    def write_push_pop(self, command: str, segment: str, index: int):
        """Writes the push and pop code for a given vm command."""
        output = []
        if command == "C_PUSH":
            if segment == "constant":
                output.append("@" + str(index))
                output.append("D=A")
                output.append("@SP")
                output.append("AM=M+1")
                output.append("A=A-1")
                output.append("M=D")
            elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
                # Put the index value into D.
                output.append("@" + str(index))
                output.append("D=A")
                # Put the base value into A.
                if segment == "temp" or segment == "pointer":
                    output.append(self.symbols[segment])
                else:
                    # Resolve where the segment refers to.
                    output.append(self.symbols[segment])
                    output.append("A=M")
                # Calculate the source address into A.
                output.append("A=D+A")
                # Put the source value into D.
                output.append("D=M")
                # Put D value into where SP points to.
                output.append("@SP")
                output.append("A=M")
                output.append("M=D")
                # Increment the stack pointer.
                output.append("@SP")
                output.append("M=M+1")
            elif segment == "static":
                # Calculate the source address into A.
                output.append("@" + self.file_name + "." + str(index))
                # Put the source value into D.
                output.append("D=M")
                # Put D value into where SP points to.
                output.append("@SP")
                output.append("A=M")
                output.append("M=D")
                # Increment the stack pointer.
                output.append("@SP")
                output.append("M=M+1")
            else:
                raise NameError("Unexpected Push Segment")
        elif command == "C_POP":
            if segment == "constant":
                # Not a valid command.
                raise NameError("Cannot Pop Constant Segment")
            elif segment in ["local", "argument", "this", "that", "temp", "pointer"]:
                # Put the index value into D.
                output.append("@" + str(index))
                output.append("D=A")
                # Put the base value into A.
                if segment == "temp" or segment == "pointer":
                    output.append(self.symbols[segment])
                else:
                    # Resolve where the segment refers to.
                    output.append(self.symbols[segment])
                    output.append("A=M")
                # Calculate the source address into D.
                output.append("D=D+A")
                # Put D value into R13 for future use.
                output.append("@R13")
                output.append("M=D")
                # Pop stack value into D.
                output.append("@SP")
                output.append("AM=M-1")
                output.append("D=M")
                # Put D value into where R13 points to.
                output.append("@R13")
                output.append("A=M")
                output.append("M=D")
            elif segment == "static":
                # Pop stack value into D.
                output.append("@SP")
                output.append("AM=M-1")
                output.append("D=M")
                # Put the source address into A.
                output.append("@" + self.file_name + "." + str(index))
                # Put D value into static address.
                output.append("M=D")
            else:
                raise NameError("Unexpected Pop Segment")
        else:
            raise NameError("Unexpected Command Type")

        # Print assembly commands.
        self.write_to_file(output)

    def write_label(self, label: str):
        """Writes the aseembly label."""
        label_name = self.function_name + "$" + label
        output = []
        output.append("(" + label_name + ")")
        self.write_to_file(output)

    def write_goto(self, label: str):
        """Writes unconditional jump to the given label."""
        label_name = self.function_name + "$" + label
        output = []
        output.append("@" + label_name)
        output.append("0;JMP")
        self.write_to_file(output)

    def write_if(self, label: str):
        """Write assembly for a conditional if-goto."""
        self.write_to_file([
            "@SP", "AM=M-1", "D=M", f"@{self.function_name}${label}", "D;JNE"
        ])

    def write_function(self, function_name: str, num_vars: int):
        """Write assembly code for defining a function."""
        self.function_name = function_name
        output = [f"({self.function_name})"]
        output.extend(["@SP", "AM=M+1", "A=A-1", "M=0"] * num_vars)
        self.write_to_file(output)

    def write_call(self, function_name: str, num_args: int):
        """Write assembly code to call a function."""
        return_label = f"{self.function_name}$ret.{self.label_counter}"
        self.label_counter += 1
        output = [
            f"@{return_label}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"
        ]
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            output.extend([f"@{segment}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"])
        output.extend([
            f"@SP", "D=M", f"@{num_args + 5}", "D=D-A", "@ARG", "M=D",
            "@SP", "D=M", "@LCL", "M=D",
            f"@{function_name}", "0;JMP",
            f"({return_label})"
        ])
        self.write_to_file(output)

    def write_return(self):
        """Write the assembly code for the return statement."""
        output = [
            "@LCL", "D=M", "@R13", "M=D",  # Save LCL to R13
            "@5", "A=D-A", "D=M", "@R14", "M=D",  # Store return address in R14
            "@SP", "AM=M-1", "D=M", "@ARG", "A=M", "M=D",  # Reposition the return value
            "@ARG", "D=M+1", "@SP", "M=D"  # Restore SP for caller
        ]
        for segment, offset in [("THAT", 1), ("THIS", 2), ("ARG", 3), ("LCL", 4)]:
            output.extend([
                "@R13", "D=M", f"@{offset}", "A=D-A", "D=M", f"@{segment}", "M=D"
            ])
        output.extend(["@R14", "A=M", "0;JMP"])
        self.write_to_file(output)

    def write_to_file(self, lines: list, newline=True):
        """Helper function to write lines to the output file."""
        if newline:
            lines.append("")
        self.file.write("\n".join(lines) + "\n")

    def close(self):
        """Close the output file."""
        self.file.close()



def main():
    """Arranges the parsing and code conversion of a Virtual Machine file."""

    # Check if an input file or a directory is given.
    if len(sys.argv) != 2:
        print("Error: No input file is found.")
        print("Usage: python " + __file__ + " [file.vm] | [directory]")
        return

    # Extract input files and setup the output file name.
    input_files = []
    input_path = sys.argv[1]

    # If a single file is provided
    if os.path.isfile(input_path) and input_path.endswith(".vm"):
        input_files.append(input_path)
        output_file_name = input_path.replace(".vm", ".asm")
    # If a directory is provided
    elif os.path.isdir(input_path):
        # Collect all .vm files in the directory
        input_files = [
            os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".vm")
        ]
        # Set the output file name to the directory name
        output_file_name = os.path.join(input_path, os.path.basename(input_path) + ".asm")
    else:
        print("Error: Invalid input. Please provide a .vm file or a directory containing .vm files.")
        return

    # Initialize the CodeWriter with the output file name.
    code_writer = CodeWriter(output_file_name)
    # Write the bootstrap code if handling multiple files.
    if len(input_files) >= 1:
        code_writer.write_init()

    # Process each .vm file.
    for input_file in input_files:
        parser = Parser(input_file)
        # Update the code writer with the current file name for static variable handling.
        code_writer.set_file_name(os.path.basename(input_file).replace(".vm", ""))

        # Translate each command in the current .vm file.
        while parser.hasMoreCommands():
            parser.advance()
            command_type = parser.commandType()
            if command_type == "C_ARITHMETIC":
                code_writer.write_arithmetic(parser.arg1())
            elif command_type in {"C_PUSH", "C_POP"}:
                code_writer.write_push_pop(command_type, parser.arg1(), parser.arg2())
            elif command_type == "C_LABEL":
                code_writer.write_label(parser.arg1())
            elif command_type == "C_GOTO":
                code_writer.write_goto(parser.arg1())
            elif command_type == "C_IF":
                code_writer.write_if(parser.arg1())
            elif command_type == "C_FUNCTION":
                code_writer.write_function(parser.arg1(), parser.arg2())
            elif command_type == "C_CALL":
                code_writer.write_call(parser.arg1(), parser.arg2())
            elif command_type == "C_RETURN":
                code_writer.write_return()

    # Close the output file after processing.
    code_writer.close()
    print(f"Translation completed: {output_file_name}")



if __name__ == "__main__":
    main()
