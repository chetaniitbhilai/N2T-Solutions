from collections import namedtuple

# Define the structure for symbols in the Jack compiler
JackSymbol = namedtuple('Symbol', ['kind', 'type', 'id'])

class JackClass:
    '''Represents a Jack class in the compiler, including its variables and symbols.'''

    def __init__(self, name):
        '''Initialize the Jack class with its name and symbol tables.'''
        self.name = name  # Name of the class
        self.symbols = dict()  # Dictionary to store symbols (fields and statics)

        # Counters for the number of static and field symbols
        self.static_symbols = 0
        self.field_symbols = 0

    def add_field(self, name, var_type):
        '''Add a field-level variable to the class symbol table.'''
        self.symbols[name] = JackSymbol('field', var_type, self.field_symbols)
        self.field_symbols += 1  # Increment the counter for field variables

    def add_static(self, name, var_type):
        '''Add a static-level variable to the class symbol table.'''
        self.symbols[name] = JackSymbol('static', var_type, self.static_symbols)
        self.static_symbols += 1  # Increment the counter for static variables

    def get_symbol(self, name):
        '''Retrieve a symbol from the class symbol table. Returns None if not found.'''
        return self.symbols.get(name)

class JackSubroutine:
    '''Represents a Jack subroutine (method, function, or constructor) in the compiler.'''

    def __init__(self, name, subroutine_type, return_type, jack_class):
        '''Initialize a Jack subroutine with its name, type, return type, and parent class.'''
        self.name = name  # Name of the subroutine
        self.jack_class = jack_class  # Reference to the parent class
        self.subroutine_type = subroutine_type  # Type: method, function, or constructor
        self.return_type = return_type  # Return type of the subroutine

        self.symbols = dict()  # Dictionary to store argument and local variable symbols
        self.arg_symbols = 0  # Counter for argument variables
        self.var_symbols = 0  # Counter for local variables

        # For methods, the 'this' reference is automatically added as the first argument
        if subroutine_type == 'method':
            self.add_arg('this', self.jack_class.name)

    def add_arg(self, name, var_type):
        '''Add an argument to the subroutine's symbol table.'''
        self.symbols[name] = JackSymbol('arg', var_type, self.arg_symbols)
        self.arg_symbols += 1  # Increment the counter for argument variables

    def add_var(self, name, var_type):
        '''Add a local variable to the subroutine's symbol table.'''
        self.symbols[name] = JackSymbol('var', var_type, self.var_symbols)
        self.var_symbols += 1  # Increment the counter for local variables

    def get_symbol(self, name):
        '''Retrieve a symbol from the subroutine's scope or fall back to the class scope.'''
        # Check if the symbol exists in the subroutine's local scope
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol

        # If not found, look for the symbol in the parent class scope
        return self.jack_class.get_symbol(name)
