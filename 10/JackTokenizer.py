import re  # Used for regular expression operations

# Regular expressions for various patterns
COMMENT = "(//.*)|(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)"  # Matches single-line (//) and multi-line (/* */) comments
EMPTY_TEXT_PATTERN = re.compile("\s*")  # Matches empty or whitespace-only text
KEY_WORD_PATTERN = re.compile("^\s*("
                              "class|constructor|function|method|static|field"
                              "|var|int|char|boolean|void|true|false|null|this|"
                              "let|do|if|else|while|return)\s*")  # Matches Jack language keywords
SYMBOL_PATTERN = re.compile("^\s*([{}()\[\].,;+\-*/&|<>=~])\s*")  # Matches symbols used in Jack
DIGIT_PATTERN = re.compile("^\s*(\d+)\s*")  # Matches integers
STRING_PATTERN = re.compile("^\s*\"(.*)\"\s*")  # Matches string literals (excluding the quotes)
IDENTIFIER_PATTERN = re.compile("^\s*([a-zA-Z_][a-zA-Z1-9_]*)\s*")  # Matches identifiers (variable names, etc.)

DEBUGGING = False  # Toggle for debugging

class JackTokenizer:
    """
    The JackTokenizer module as described in Chapter 10 of the Nand2Tetris project.
    Responsible for breaking input into meaningful tokens and identifying token types.
    """

    # List of keywords used in Jack
    keyword = ["CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
               "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET",
               "DO", "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE",
               "NULL", "THIS"]

    # Token type constants
    KEYWORD = 0
    SYMBOL = 1
    INT_CONST = 2
    STRING_CONST = 3
    IDENTIFIER = 4

    def __init__(self, input_file_path):
        
        with open(input_file_path, "r") as file:
            self.text = file.read()  # Read the entire input file as a string
        self._clear_all_comments()  # Remove comments from the input text
        self._tokenType = None  # Current token type
        self._currentToken = None  # Current token value

    def _clear_all_comments(self):
        
        self.text = re.sub(COMMENT, "", self.text)  # Replace comments with empty strings

    def hasMoreTokens(self):
      
        if re.fullmatch(EMPTY_TEXT_PATTERN, self.text):  # If text is empty or whitespace
            return False
        else:
            return True

    def advance(self):
        """
        Advances to the next token in the input.
        Identifies and sets the type and value of the current token.
        """
        if self.hasMoreTokens():  # Check if there are more tokens to process
            # Try matching a keyword
            current_match = re.match(KEY_WORD_PATTERN, self.text)
            if current_match is not None:
                self.text = re.sub(KEY_WORD_PATTERN, "", self.text)  # Remove the matched token from the text
                self._tokenType = JackTokenizer.KEYWORD  # Set token type
                self._currentToken = current_match.group(1)  # Set token value
            else:
                # Try matching a symbol
                current_match = re.match(SYMBOL_PATTERN, self.text)
                if current_match is not None:
                    self.text = re.sub(SYMBOL_PATTERN, "", self.text)
                    self._tokenType = JackTokenizer.SYMBOL
                    self._currentToken = current_match.group(1)
                else:
                    # Try matching an integer constant
                    current_match = re.match(DIGIT_PATTERN, self.text)
                    if current_match is not None:
                        self.text = re.sub(DIGIT_PATTERN, "", self.text)
                        self._tokenType = JackTokenizer.INT_CONST
                        self._currentToken = current_match.group(1)
                    else:
                        # Try matching a string constant
                        current_match = re.match(STRING_PATTERN, self.text)
                        if current_match is not None:
                            self.text = re.sub(STRING_PATTERN, "", self.text)
                            self._tokenType = JackTokenizer.STRING_CONST
                            self._currentToken = current_match.group(1)
                        else:
                            # Try matching an identifier
                            current_match = re.match(IDENTIFIER_PATTERN, self.text)
                            if current_match is not None:
                                self.text = re.sub(IDENTIFIER_PATTERN, "", self.text)
                                self._tokenType = JackTokenizer.IDENTIFIER
                                self._currentToken = current_match.group(1)

    # Token type access methods
    def tokenType(self):
        """
        :return: Current token type
        """
        return self._tokenType

    def keyWord(self):
        """
        :return: Current keyword token value (if applicable)
        """
        return self._currentToken

    def symbol(self):
        """
        :return: Current symbol token value (if applicable)
        """
        return self._currentToken

    def identifier(self):
        """
        :return: Current identifier token value (if applicable)
        """
        return self._currentToken

    def intVal(self):
        """
        :return: Current integer token value (converted to int)
        """
        return int(self._currentToken)

    def stringVal(self):
        """
        :return: Current string token value
        """
        return self._currentToken

# Main testing code for debugging
if __name__ == "__main__" and DEBUGGING:
    a = JackTokenizer("Square.jack")  # Create a tokenizer instance for a .jack file change jack file name here
    while a.hasMoreTokens():  # Process tokens until none are left
        a.advance()  # Move to the next token
        print(a.keyWord())  # Print the current keyword token (if applicable)
