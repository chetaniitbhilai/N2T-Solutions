import re
import sys
from collections import namedtuple

# Define the structure for tokens
Token = namedtuple('Token', ('type', 'value'))

class JackTokenizer:
    '''A tokenizer for the Jack programming language, capable of breaking down source code into tokens.'''

    # Regular expressions for Jack language components
    RE_INTEGER = r'\d+'  # Matches integer constants
    RE_STRING = r'"[^"]*"'  # Matches string constants enclosed in double quotes
    RE_IDENTIFIER = r'[A-Za-z_][A-Za-z_\d]*'  # Matches valid Jack identifiers
    RE_SYMBOL = r'\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~'  # Matches symbols
    RE_KEYWORD = '|'.join(keyword for keyword in [
        'class', 'method', 'constructor', 'function', 'field', 'static', 'var',
        'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
        'let', 'do', 'if', 'else', 'while', 'return'
    ])  # Matches Jack keywords

    # Pair regular expressions with their respective token types
    LEXICAL_TYPES = [
        (RE_KEYWORD, 'keyword'),
        (RE_SYMBOL, 'symbol'),
        (RE_INTEGER, 'integerConstant'),
        (RE_STRING, 'stringConstant'),
        (RE_IDENTIFIER, 'identifier')
    ]

    # Regular expression to split code into tokens while preserving symbols and strings
    RE_SPLIT = '(' + '|'.join(expr for expr in [RE_SYMBOL, RE_STRING]) + ')|\s+'

    @staticmethod
    def remove_comments(file):
        '''Remove single-line and multi-line comments from the Jack source code.'''
        # Remove single-line comments
        uncommented = re.sub(r'//.*?\n', '\n', file)
        # Remove multi-line comments (non-greedy match for block comments)
        uncommented = re.sub(r'/\*.*?\*/', '', uncommented, flags=re.DOTALL)
        return uncommented

    def __init__(self, file):
        '''Initialize the tokenizer with a source file as a string.'''
        # Preprocess the code by removing comments
        self.code = JackTokenizer.remove_comments(file)
        # Tokenize the processed code
        self.tokens = self.tokenize()

    def tokenize(self):
        '''Split the source code into a list of tokens based on Jack's lexical rules.'''
        # Split the code using the specified regex
        split_code = re.split(self.RE_SPLIT, self.code)
        tokens = []

        for lex in split_code:
            # Skip empty or whitespace-only fragments
            if lex is None or re.match(r'^\s*$', lex):
                continue

            # Match the fragment against lexical rules to determine its type
            for expr, lex_type in self.LEXICAL_TYPES:
                if re.match(expr, lex):
                    tokens.append(Token(lex_type, lex))  # Add the token to the list
                    break
            else:
                # Handle unknown tokens by exiting with an error message
                print('Error: unknown token', lex)
                sys.exit(1)

        return tokens

    def current_token(self):
        '''Retrieve the current token without advancing. Returns None if no tokens remain.'''
        return self.tokens[0] if self.tokens else None

    def advance(self):
        '''Move to the next token and return the current token. Returns None if no tokens remain.'''
        return self.tokens.pop(0) if self.tokens else None
