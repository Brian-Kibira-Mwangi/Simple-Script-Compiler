from lexer import Lexer
from parser import Parser

class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []
    
    def new_temp(self):
        """Generate a new temporary variable"""
        self.temp_count += 1
        return f"t{self.temp_count}"
    
    def new_label(self):
        """Generate a new label"""
        self.label_count += 1
        return f"L{self.label_count}"
    
    def emit(self, instruction):
        """Add an instruction to the code"""
        self.code.append(instruction)
    
    def get_code(self):
        """Return the generated TAC"""
        return "\n".join(self.code)

def generate_tac(ast):
    """Generate TAC from AST"""
    tac = TACGenerator()
    
    for node in ast:
        process_node(node, tac)
    
    return tac.get_code()

def process_node(node, tac):
    """Process individual AST nodes"""
    if node[0] == 'assign':
        # Handle assignment: ('assign', target, expr)
        target = node[1]
        value = process_expression(node[2], tac)
        tac.emit(f"{target} := {value}")
    
    elif node[0] == 'binop':
        # Handle binary operation: ('binop', op, left, right)
        temp = tac.new_temp()
        left = process_expression(node[2], tac)
        right = process_expression(node[3], tac)
        tac.emit(f"{temp} := {left} {node[1]} {right}")
        return temp
    
    elif node[0] == 'compare':
        # Handle comparison: ('compare', op, left, right)
        temp = tac.new_temp()
        left = process_expression(node[2], tac)
        right = process_expression(node[3], tac)
        tac.emit(f"{temp} := {left} {node[1]} {right}")
        return temp
    
    elif node[0] == 'if':
        # Handle if statement: ('if', cond, then_block, else_block)
        cond = process_expression(node[1], tac)
        else_label = tac.new_label()
        end_label = tac.new_label()
        
        tac.emit(f"if not {cond} goto {else_label}")
        for stmt in node[2]:  # Then block
            process_node(stmt, tac)
        tac.emit(f"goto {end_label}")
        tac.emit(f"{else_label}:")
        for stmt in node[3]:  # Else block
            process_node(stmt, tac)
        tac.emit(f"{end_label}:")
    
    elif node[0] == 'loop':
        # Handle loop: ('loop', body, condition)
        start_label = tac.new_label()
        end_label = tac.new_label()
        
        tac.emit(f"{start_label}:")
        for stmt in node[1]:  # Loop body
            process_node(stmt, tac)
        
        cond = process_expression(node[2], tac)
        tac.emit(f"if {cond} goto {start_label}")
        tac.emit(f"{end_label}:")
    
    elif node[0] == 'log':
        # Handle print: ('print', content, expr)
        if node[1]:  # String literal
            tac.emit(f'log "{node[1]}"')
        else:  # Expression
            value = process_expression(node[2], tac)
            tac.emit(f'log {value}')
    
    elif node[0] == 'func_def':
        # Handle function definition
        tac.emit(f"func {node[1]}({', '.join(node[2])}):")
        for stmt in node[3]:  # Function body
            process_node(stmt, tac)
        tac.emit(f"end {node[1]}")
    
    elif node[0] in ('identifier', 'number'):
        return node[1]  # Return raw value

def process_expression(expr, tac):
    """Process expressions recursively"""
    if isinstance(expr, tuple):
        return process_node(expr, tac)
    return expr  # For numbers and identifiers

if __name__ == "__main__":
    # Read source code
    with open("simplescript.ssc", "r") as f:
        source_code = f.read()
    
    # Step 1: Lexical analysis
    lexer = Lexer(source_code)
    
    # Step 2: Parsing
    parser = Parser(lexer)
    ast = parser.program()
    print("AST generated successfully!")
    
    # Step 3: Generate TAC
    tac_code = generate_tac(ast)
    print("\n=== Three-Address Code ===")
    print(tac_code)
