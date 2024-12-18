kind_to_segment = {'static': 'static',
                   'field': 'this',
                   'arg': 'argument',
                   'var': 'local'}

class VMWriter:
    '''A utility class for writing VM code, used in the Jack-to-VM compiler'''

    def __init__(self, ostream):
        '''Initialize the VMWriter with an output stream to write VM code'''
        self.ostream = ostream  # The output stream for VM code
        self.label_count = 0    # Counter for generating unique labels

    def write_if(self, label):
        '''Write an if-goto command to jump to a label if the condition is false.
        The top stack value is negated and checked.'''
        self.ostream.write('not\n')  # Negate the top of the stack
        self.ostream.write(f'if-goto {label}\n')  # Conditional jump

    def write_goto(self, label):
        '''Write an unconditional goto command to jump to a specific label.'''
        self.ostream.write(f'goto {label}\n')

    def write_label(self, label):
        '''Write a label declaration in the VM code.'''
        self.ostream.write(f'label {label}\n')

    def write_function(self, jack_subroutine):
        '''Write a function declaration in the VM code. 
        Includes the function name and the number of local variables.'''
        class_name = jack_subroutine.jack_class.name  # Name of the Jack class
        name = jack_subroutine.name  # Name of the subroutine
        local_vars = jack_subroutine.var_symbols  # Count of local variables
        self.ostream.write(f'function {class_name}.{name} {local_vars}\n')

    def write_return(self):
        '''Write a return statement in the VM code.'''
        self.ostream.write('return\n')

    def write_call(self, class_name, func_name, arg_count):
        '''Write a function call in the VM code with a specified number of arguments.'''
        self.ostream.write(f'call {class_name}.{func_name} {arg_count}\n')

    def write_pop_symbol(self, jack_symbol):
        '''Pop the top value from the stack and store it in a Jack symbol's memory location.'''
        kind = jack_symbol.kind  # Get the symbol's kind (e.g., static, field)
        offset = jack_symbol.id  # Offset in the segment
        segment = kind_to_segment[kind]  # Map kind to the corresponding VM segment
        self.write_pop(segment, offset)

    def write_push_symbol(self, jack_symbol):
        '''Push the value of a Jack symbol onto the stack.'''
        kind = jack_symbol.kind  # Get the symbol's kind (e.g., static, field)
        offset = jack_symbol.id  # Offset in the segment
        segment = kind_to_segment[kind]  # Map kind to the corresponding VM segment
        self.write_push(segment, offset)

    def write_pop(self, segment, offset):
        '''Write a pop command to store the top stack value in the specified segment and offset.'''
        self.ostream.write(f'pop {segment} {offset}\n')

    def write_push(self, segment, offset):
        '''Write a push command to load a value from a specified segment and offset onto the stack.'''
        self.ostream.write(f'push {segment} {offset}\n')

    def write(self, action):
        '''Write a generic VM action command.'''
        self.ostream.write(f'{action}\n')

    def write_int(self, n):
        '''Push an integer constant onto the stack.'''
        self.write_push('constant', n)

    def write_string(self, s):
        '''Create a new string object in the heap and append characters one by one.
        The string is enclosed in double quotes, so slicing is used to remove them.'''
        s = s[1:-1]  # Remove the enclosing double quotes
        self.write_int(len(s))  # Push the string length
        self.write_call('String', 'new', 1)  # Allocate memory for the string
        for c in s:
            self.write_int(ord(c))  # Push the ASCII value of each character
            self.write_call('String', 'appendChar', 2)  # Append the character
