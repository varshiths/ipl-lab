#!/usr/bin/python3

import sys
import ply.lex as lex
import ply.yacc as yacc

def tabs(n):
    return "\t"*n

class ASTNode:


    def __init__(self, label, children):
        self.label = label
        self.children = children

    def print_tree(self, ntabs=0):
        if self.label == "VAR" or self.label == "CONST":
            print(tabs(ntabs), end='')            
            print(self.label, "(", self.children[0].label, ")", sep='')
        else:
            print(tabs(ntabs), self.label, sep='')

            if len(self.children) != 0:
                print(tabs(ntabs), "(", sep='')
                for i, child in enumerate(self.children):
                    child.print_tree(ntabs + 1)
                    if i != len(self.children)-1:
                        print(tabs(ntabs+1), ",", sep='')
                print(tabs(ntabs), ")", sep='')


DBG = False

tokens = [
        'NAME', 'NUMBER',
        'ASSIGN',
        'COMMA',
        'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE',
        'SEMICOLON', 'STAR', 'AMP',
        'PLUS', 'MINUS', 'DIV'
]

reserved = {
    'int' : 'INT',
    'void' : 'VOID',
    'main' : 'MAIN',
}
tokens += list(reserved.values())

# t_ignore = "( \t)|(//.*)"
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

t_PLUS = r'\+'
t_MINUS = r'\-'
t_DIV = r'/'

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
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'DIV'),
    ('right', 'UMINUS', 'REF', 'AMP'),
)

def p_main(p):
    '''
    main : VOID MAIN LPAREN RPAREN LBRACE body RBRACE
    '''
    p[0] = p[6]
    return p[0]
    pass

def p_body(p):
    '''
    body : list_stat
    '''
    p[0] = p[1]
    pass

def p_list_stat(p):
    '''
    list_stat : 
    list_stat : statement SEMICOLON list_stat 
    '''
    p[0] = []
    if len(p) != 1:
        if p[1] is not None:
            p[0].append(p[1])
        p[0].extend(p[3])
    pass

def p_statement(p):
    '''
    statement : declaration
            | assignment
    '''
            # | list_assignments
    p[0] = p[1]
    pass

def p_type(p):
    '''
    type : INT
    '''
        # | VOID
    pass

def p_pointer(p):
    '''
    pointer : STAR combine %prec REF
    '''

    p[0] = ASTNode("DEREF", [p[2]])

    pass

def p_pointer_d(p):
    '''
    pointer_d : STAR variable %prec REF
                | STAR pointer_d %prec REF
    '''
    pass

def p_combination(p):
    '''
    combine : variable
            | pointer
            | reference
    '''
    p[0] = p[1]
    pass

def p_reference(p):
    '''
    reference : AMP combine
    '''
    p[0] = ASTNode("ADDR", [p[2]])
    pass

def p_num(p):
    '''
    num : NUMBER
    '''
    p[0] = ASTNode("CONST", [ASTNode(p[1], [])])
    pass

def p_variable(p):
    '''
    variable : NAME
    '''
    p[0] = ASTNode("VAR", [ASTNode(p[1], [])])
    pass

def p_declr_entity_var(p):
    '''
    declr_entity : variable
    '''
    pass

def p_declr_entity_pointer(p):
    '''
    declr_entity : pointer_d
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
    p[0] = None
    pass

def p_assignment(p):
    '''
    assignment : assignment1
                | assignment2
    '''
    p[0] = p[1]
    pass

def p_assignment2(p):
    '''
    assignment2 : variable ASSIGN assigned2_value
    '''
    p[0] = ASTNode("ASGN", [p[1], p[3]])
    pass

def p_assigned2_value(p):
    '''
    assigned2_value : expression2
    '''
    p[0] = p[1]
    pass

def p_assignment1(p):
    '''
    assignment1 :  assigned1_entity ASSIGN assigned1_value
    '''
    p[0] = ASTNode("ASGN", [p[1], p[3]])
    pass

def p_assigned1_entity(p):
    '''
    assigned1_entity : pointer
    '''
    p[0] = p[1]
    pass

def p_assigned1_value(p):
    '''
    assigned1_value : expression
    '''
    p[0] = p[1]
    pass

def p_expression(p):
    '''
    expression : reference
                | pointer
                | variable
                | num
                | binary_expr
    '''
    p[0] = p[1]
    pass

def p_binary_expr(p):
    '''
    binary_expr : expression PLUS expression
                | expression MINUS expression
                | expression STAR expression
                | expression DIV expression
                | MINUS expression %prec UMINUS
    '''

    if len(p) == 3:
        p[0] = ASTNode("UMINUS", [p[2]])
    else:
        if p[2] == "+":
            p[0] = ASTNode("PLUS", [p[1], p[3]])
        elif p[2] == "-":
            p[0] = ASTNode("MINUS", [p[1], p[3]])
        elif p[2] == "*":
            p[0] = ASTNode("MUL", [p[1], p[3]])
        elif p[2] == "/":
            p[0] = ASTNode("DIV", [p[1], p[3]])

    pass

def p_expression2(p):
    '''
    expression2 : reference
                | pointer
                | variable
                | binary_expr2
    '''
    p[0] = p[1]
    pass

def p_binary_expr2(p):
    '''
    binary_expr2 : expression PLUS expression
                | expression MINUS expression
                | expression STAR expression
                | expression DIV expression
                | MINUS expression2 %prec UMINUS
    '''

    if len(p) == 3:
        p[0] = ASTNode("UMINUS", [p[2]])
    else: # check that both p[1] and p[2] can't be numbers
        if p[2] == "+":
            p[0] = ASTNode("PLUS", [p[1], p[3]])
        elif p[2] == "-":
            p[0] = ASTNode("MINUS", [p[1], p[3]])
        elif p[2] == "*":
            p[0] = ASTNode("MUL", [p[1], p[3]])
        elif p[2] == "/":
            p[0] = ASTNode("DIV", [p[1], p[3]])

    pass

def p_error(p):
    if p:
        print("syntax error at %s on line no %d" % (p.value, p.lineno))
    else:
        print("syntax error at EOF")        

def init():
    lex.lex(debug=DBG)
    yacc.yacc(debug=DBG)

def process(data):
    a = yacc.parse(data)
    try:
        for node in a:
            node.print_tree()
            print()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error: Incorrect number of arguments")
        print("Usage: main.py program")
        sys.exit()

    init()

    with open(sys.argv[1], 'r') as f:
        process(f.read())

