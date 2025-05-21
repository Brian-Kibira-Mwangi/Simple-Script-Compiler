import re

# Define token types
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

def tokenize(code):
    tokens = []
    for match in re.finditer(token_regex, code):
        token_type = match.lastgroup
        value = match.group(token_type)
        if token_type != 'WHITESPACE':  # Ignore spaces
            tokens.append((token_type, value))
    return tokens

# Read a SimpleScript file
file_path = "simplescript.ssc"  # Example file name
with open(file_path, 'r') as file:
    source_code = file.read()

# Tokenize and print output
tokens = tokenize(source_code)
for token in tokens:
    print(token)
