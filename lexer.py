import re

# Token definitions
token_specs = [
    ('KEYWORD', r'\b(var|return|const|repeat|until|do|end|func|log)\b'),
    ('ASSIGN', r':='),  # :=
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('NUMBER', r'\b\d+(\.\d*)?\b'),
    ('OPERATOR', r'[+\-*/=<>!&|]+'),
    ('DELIMITER', r'[;,\(\)\[\]\{\}:]'),  # (, ), :, etc.
    ('QUESTION', r'\?'),  # If condition
    ('STRING', r'"[^"]*"'),
    ('WHITESPACE', r'\s+'),
    ('UNKNOWN', r'.'),  # Catch all unknown characters
]

# Compile regex
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)

class Lexer:
    def __init__(self, code):
        self.tokens = self.tokenize(code)
        self.position = 0

    def tokenize(self, code):
        tokens = []
        for match in re.finditer(token_regex, code):
            token_type = match.lastgroup
            value = match.group(token_type)
            if token_type != 'WHITESPACE':  # Ignore spaces
                tokens.append((token_type, value))
        tokens.append(('EOF', None))  # End of file token
        return tokens

    def advance(self):
        """Move to the next token."""
        if self.position < len(self.tokens) - 1:
            self.position += 1

    def peek(self):
        """Return the current token without consuming it."""
        return self.tokens[self.position]