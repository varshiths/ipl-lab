#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc

DBG = False

tokens = [
        'NAME', 'NUMBER',
        'ASSIGN',
        'COMMA',
        'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE',
        'SEMICOLON', 'STAR', 'AMP'
]

reserved = {
    'int' : 'INT',
    'void' : 'VOID',
    'main' : 'MAIN',
}
tokens += list(reserved.values())

t_ignore = " \t"

t_ASSIGN = r'='
t_COMMA = r','

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LBRACE = r'\{'
t_RBRACE = r'\}'

t_SEMICOLON = r';'
t_STAR = r'\*'
t_AMP = r'&'

t_NUMBER = r'\d+'

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t): 
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# Parsing rules
precedence = (
    ('right', 'ASSIGN'),
    ('right', 'STAR', 'AMP'),
)

def p_main(p):
    '''
    main : VOID MAIN LPAREN RPAREN LBRACE body RBRACE
    '''
    pass

def p_body(p):
	'''
    body : list_stat
    '''
	pass

def p_list_stat(p):
    '''
    list_stat : 
    list_stat : statement SEMICOLON list_stat 
    '''
    pass

def p_statement(p):
    '''
    statement : declaration
            | list_assignments
    '''
    pass

def p_type(p):
    '''
    type : INT
        | VOID
    '''
    pass

def p_pointer(p):
    '''
    pointer : STAR NAME
    '''
    pass

def p_reference(p):
    '''
    reference : AMP NAME
    '''
    pass

def p_variable(p):
    '''
    variable : NAME
    '''
    pass

def p_declr_entity(p):
    '''
    declr_entity : variable
        | pointer
    '''
    pass

def p_list_var(p):
    '''
    list_var : declr_entity
            | list_var COMMA declr_entity
    '''
    pass

def p_declaration(p):
    '''
    declaration : type list_var
    '''
    pass

def p_assigned_value(p):
    '''
    assigned_value : variable
                    | pointer
                    | reference
                    | NUMBER
    '''
    pass

def p_list_assignments(p):
    '''
    list_assignments : assignment
                    | list_assignments COMMA assignment
    '''
    pass

def p_assignment(p):
    '''
    assignment : declr_entity ASSIGN assigned
    assigned : assignment
            | assigned_value
    '''
    pass

# def p_expression_name(p):
#         '''
#         expression : NAME
#         '''
#         try:
#             p[0] = p[1]
#         except LookupError:
#             print("Undefined name '%s'" % p[1])
#             p[0] = 0


def p_error(p):
	if p:
		print("syntax error at %s on line no %d" % (p.value, p.lineno))
	else:
		print("syntax error at EOF")		

def init():
	lex.lex(debug=DBG)
	yacc.yacc(debug=DBG)

def process(data):
	yacc.parse(data)

if __name__ == "__main__":
    init()
    if len(sys.argv) != 2:
        print("Error: Incorrect number of arguments")
        print("Usage: main.py program")
        sys.exit()

    with open(sys.argv[1], 'r') as f:
        process(f.read())
