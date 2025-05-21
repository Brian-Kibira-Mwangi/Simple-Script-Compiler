The SimpleScript Compiler is a mini compiler developed to demonstrate core concepts of compiler design. It processes a custom scripting language through key compilation phases;

Lexical Analysis: Tokenizes input source code using regular expressions, identifying keywords, identifiers, literals, and operators.

Syntax Analysis (Parsing): Constructs an Abstract Syntax Tree (AST) from tokens based on a context-free grammar.

Intermediate Code Generation: Converts parsed expressions into Three-Address Code (TAC), enabling simplified code optimization and translation to lower-level representations.

Context Free grammar for sipmlescript code;

<program> → <statement_list>

<statement_list> → <statement> <statement_list> | ε

<statement> → <assignment>

 | <if_statement>
 
 | <loop>
 
 | <function_def>
 
 | <function_call>
 
 | <log_statement>
 
 | <return_statement>
 
<assignment> → identifier := <expression>

<if_statement> → ? <expression> do <statement_list> : <statement_list> end

<loop> → repeat <statement_list> until <expression>

<function_def> → func identifier ( <param_list> ) do <statement_list> end

<param_list> → identifier , <param_list> | identifier | ε

<function_call> → identifier ( <arg_list> )

<arg_list> → <expression> , <arg_list> | <expression> | ε

<log_statement> → log ( <log_content> )

<log_content> → STRING | <expression>

<return_statement> → return <expression> | return

<expression> → <comparison> ((&& | ||) <comparison>)*

<comparison> → <term> ((> | < | == | != | >= | <=) <term>)*

<term> → <factor> ((+ | -) <factor>)*

<factor> → <primary> ((* | /) <primary>)*

<primary> → identifier

 | number
 
 | ( <expression> )
 
 | <function_call>
