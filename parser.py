from lexer import Lexer

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def match(self, expected_type):
        """Consume the current token if it matches the expected type."""
        token_type, value = self.lexer.peek()
        if token_type == expected_type:
            self.lexer.advance()
            return value
        else:
            raise SyntaxError(f"Expected {expected_type}, got {token_type}")

    def program(self):
        """<program> → <statement_list>"""
        return self.statement_list()

    def statement_list(self):
        """<statement_list> → <statement> <statement_list> | ε"""
        statements = []
        # Continue until we hit a terminating token
        while not self.is_terminator():
            statements.append(self.statement())
        return statements

    def is_terminator(self):
        """Check if current token is a statement list terminator"""
        token_type, value = self.lexer.peek()
        return (token_type == 'EOF' or 
                (token_type == 'KEYWORD' and value in {'end', 'until'}) or
                (token_type == 'DELIMITER' and value == ':'))

    def statement(self):
        """<statement> → <assignment> | <if_statement> | <loop> | <function_def> | <function_call> | <print_statement>"""
        token_type, value = self.lexer.peek()
        if token_type == 'IDENTIFIER':
            return self.assignment_or_function_call()
        elif token_type == 'QUESTION':
            return self.if_statement()
        elif token_type == 'KEYWORD' and value == 'repeat':
            return self.loop()
        elif token_type == 'KEYWORD' and value == 'func':
            return self.function_def()
        elif token_type == 'KEYWORD' and value == 'log':
            return self.log_statement()
        elif token_type == 'KEYWORD' and value == 'return':
            return self.return_statement()
        else:
            raise SyntaxError(f"Unexpected token: {token_type}")
        
    def return_statement(self):
        """Handles return statements"""
        self.match('KEYWORD')  # return
        # Return can have an optional expression
        if self.lexer.peek()[0] not in {'DELIMITER', 'KEYWORD'}:
            expr = self.expression()
        else:
            expr = None
        return ('return', expr)
    
    def assignment_or_function_call(self):
        """Handle both assignment and function call"""
        identifier = self.match('IDENTIFIER')
        if self.lexer.peek()[0] == 'ASSIGN':
            self.match('ASSIGN')
            expr = self.expression()
            return ('assign', identifier, expr)
        elif self.lexer.peek()[0] == 'DELIMITER' and self.lexer.peek()[1] == '(':
            return self.function_call(identifier)
        else:
            raise SyntaxError("Invalid statement")
    def if_statement(self):
        """<if_statement> → ? <expression> do <statement_list> : <statement_list> end"""
        self.match('QUESTION')  # Match `?`
        condition = self.expression()
        self.match('KEYWORD')  # Match `do`

        # Parse then-block
        then_block = self.statement_list()
    
        # Match the colon separator
        self.match('DELIMITER')  # Match `:`
    
        # Parse else-block
        else_block = self.statement_list()
    
        self.match('KEYWORD')  # Match `end`
        return ('if', condition, then_block, else_block)


    def loop(self):
        """<loop> → repeat <statement_list> until <expression>"""
        self.match('KEYWORD')  # repeat
        body = self.statement_list()
        self.match('KEYWORD')  # until
        condition = self.expression()
        return ('loop', body, condition)
    
    def log_statement(self):
        """<log_statement> → log ( <log_content> )"""
        self.match('KEYWORD')  # log
        self.match('DELIMITER')  # (
    
        token_type, value = self.lexer.peek()
        if token_type == 'STRING':
            content = self.match('STRING')
            expr = None
        else:
            content = None
            expr = self.expression()
        
        self.match('DELIMITER')  # )
        return ('log', content, expr)

    def function_def(self):
        """<function_def> → func identifier ( <param_list> ) do <statement_list> end"""
        self.match('KEYWORD')  # func
        name = self.match('IDENTIFIER')
        self.match('DELIMITER')  # (
        params = self.param_list()
        self.match('DELIMITER')  # )
        self.match('KEYWORD')  # do
        body = self.statement_list()
        self.match('KEYWORD')  # end
        return ('func_def', name, params, body)

    def param_list(self):
        """<param_list> → identifier , <param_list> | identifier | ε"""
        params = []
        if self.lexer.peek()[0] == 'IDENTIFIER':
            params.append(self.match('IDENTIFIER'))
            while self.lexer.peek()[0] == 'DELIMITER' and self.lexer.peek()[1] == ',':
                self.match('DELIMITER')  # ,
                params.append(self.match('IDENTIFIER'))
        return params

    def function_call(self, name):
        """<function_call> → identifier ( <arg_list> )"""
        self.match('DELIMITER')  # (
        args = self.arg_list()
        self.match('DELIMITER')  # )
        return ('func_call', name, args)

    def arg_list(self):
        """<arg_list> → <expression> , <arg_list> | <expression> | ε"""
        args = []
        if self.lexer.peek()[0] not in {'DELIMITER'}:
            args.append(self.expression())
            while self.lexer.peek()[0] == 'DELIMITER' and self.lexer.peek()[1] == ',':
                self.match('DELIMITER')  # ,
                args.append(self.expression())
        return args
    def expression(self):
        """<expression> → <comparison> ((&& | ||) <comparison>)*"""
        left = self.comparison()
        while self.lexer.peek()[0] == 'OPERATOR' and self.lexer.peek()[1] in {'&&', '||'}:
            op = self.match('OPERATOR')
            right = self.comparison()
            left = ('logop', op, left, right)  # New node type for logical ops
        return left

    def comparison(self):
        """<comparison> → <term> ((> | < | == | != | >= | <=) <term>)*"""
        left = self.term()
        while self.lexer.peek()[0] == 'OPERATOR' and self.lexer.peek()[1] in {'>', '<', '==', '!=', '>=', '<='}:
            op = self.match('OPERATOR')
            right = self.term()
            left = ('compare', op, left, right)  # Create a comparison node
        return left

    def term(self):
        """<term> → <factor> ((+ | -) <factor>)*"""
        left = self.factor()
        while self.lexer.peek()[0] == 'OPERATOR' and self.lexer.peek()[1] in {'+', '-'}:
            op = self.match('OPERATOR')
            right = self.factor()
            left = ('binop', op, left, right)  # Create a binary operation node
        return left

    def factor(self):
        """<factor> → <primary> ((* | /) <primary>)*"""
        left = self.primary()
        while self.lexer.peek()[0] == 'OPERATOR' and self.lexer.peek()[1] in {'*', '/'}:
            op = self.match('OPERATOR')
            right = self.primary()
            left = ('binop', op, left, right)  # Create a binary operation node
        return left

    def primary(self):
        """<primary> → identifier | number | ( <expression> ) | <function_call>"""
        token_type, value = self.lexer.peek()
        if token_type == 'IDENTIFIER':
            # Check if this is a function call
            if self.lexer.peek()[1] == '(':
                return self.function_call(self.match('IDENTIFIER'))
            return ('identifier', self.match('IDENTIFIER'))
        elif token_type == 'NUMBER':
            return ('number', self.match('NUMBER'))
        elif token_type == 'DELIMITER' and value == '(':
            self.match('DELIMITER')  # Consume '('
            expr = self.expression()
            self.match('DELIMITER')  # Consume ')'
            return expr
        else:
            raise SyntaxError(f"Unexpected token in expression: {token_type}")
    
def print_tokens(lexer):
    """Print all tokens in a readable format"""
    print("\n=== Tokens ===")
    for token in lexer.tokens[:-1]:  # Skip EOF token for cleaner output
        print(token)
    print("="*40)

    
            
class CompactPrintAST:
    def __init__(self, ast):
        self.ast = ast
    
    def print_tree(self):
        """Compact tree representation"""
        for node in self.ast:
            self._print_node(node)
    
    def _print_node(self, node, level=0):
        """Recursive printing with indentation"""
        prefix = "│   " * (level-1) + "├── " if level > 0 else ""
        
        if not isinstance(node, tuple):
            print(prefix + str(node))
            return
        
        node_type = node[0]
        print(prefix + node_type)
        
        for item in node[1:]:
            if isinstance(item, list):
                for subnode in item:
                    self._print_node(subnode, level+1)
            else:
                self._print_node(item, level+1)

# Run parser
file_path = "simplescript.ssc"
with open(file_path, 'r') as file:
    source_code = file.read()

lexer = Lexer(source_code)
print_tokens(lexer)
parser = Parser(lexer)
ast = parser.program()
print("Parsing completed successfully!")

print("\n AST structure:")
CompactPrintAST(ast).print_tree()  # This shows the nice tree format
