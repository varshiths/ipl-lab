from .Lexer import Lexer
import ply.yacc as yacc

import sys

from .AST import ASTNode

class Parser:

	tokens = Lexer.tokens

	def __init__(self, parser_debug=False, lexer_debug=False):
		self.lexer = Lexer(lexer_debug)
		self.parser = yacc.yacc(debug=parser_debug, module=self)

	precedence = (
	    ('right', 'ASSIGN'),
	    ('left', 'PLUS', 'MINUS'),
	    ('left', 'STAR', 'DIV'),
	    ('right', 'UMINUS', 'REF', 'AMP'),
	)

	def p_main(self, p):
	    '''
	    main : VOID MAIN LPAREN RPAREN LBRACE body RBRACE
	    '''
	    p[0] = p[6]
	    return p[0]
	    pass

	def p_body(self, p):
	    '''
	    body : list_stat
	    '''
	    p[0] = p[1]
	    pass

	def p_list_stat(self, p):
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

	def p_statement(self, p):
	    '''
	    statement : declaration
	            | assignment
	    '''
	            # | list_assignments
	    p[0] = p[1]
	    pass

	def p_type(self, p):
	    '''
	    type : INT
	    '''
	        # | VOID
	    pass

	def p_pointer(self, p):
	    '''
	    pointer : STAR combine %prec REF
	    '''

	    p[0] = ASTNode("DEREF", [p[2]])

	    pass

	def p_pointer_d(self, p):
	    '''
	    pointer_d : STAR variable %prec REF
	                | STAR pointer_d %prec REF
	    '''
	    pass

	def p_combination(self, p):
	    '''
	    combine : variable
	            | pointer
	            | reference
	    '''
	    p[0] = p[1]
	    pass

	def p_reference(self, p):
	    '''
	    reference : AMP combine
	    '''
	    p[0] = ASTNode("ADDR", [p[2]])
	    pass

	def p_num(self, p):
	    '''
	    num : NUMBER
	    '''
	    p[0] = ASTNode("CONST", [ASTNode(p[1], [])])
	    pass

	def p_variable(self, p):
	    '''
	    variable : NAME
	    '''
	    p[0] = ASTNode("VAR", [ASTNode(p[1], [])])
	    pass

	def p_declr_entity_var(self, p):
	    '''
	    declr_entity : variable
	    '''
	    pass

	def p_declr_entity_pointer(self, p):
	    '''
	    declr_entity : pointer_d
	    '''
	    pass

	def p_list_var(self, p):
	    '''
	    list_var : declr_entity
	            | list_var COMMA declr_entity
	    '''
	    pass

	def p_declaration(self, p):
	    '''
	    declaration : type list_var
	    '''
	    p[0] = None
	    pass

	def p_assignment(self, p):
	    '''
	    assignment : assignment1
	                | assignment2
	    '''
	    p[0] = p[1]
	    pass

	def p_assignment2(self, p):
	    '''
	    assignment2 : variable ASSIGN assigned2_value
	    '''
	    p[0] = ASTNode("ASGN", [p[1], p[3]])
	    pass

	def p_assigned2_value(self, p):
	    '''
	    assigned2_value : expression2
	    '''
	    p[0] = p[1]
	    pass

	def p_assignment1(self, p):
	    '''
	    assignment1 : pointer ASSIGN assigned1_value
	    '''
	    p[0] = ASTNode("ASGN", [p[1], p[3]])
	    pass

	def p_assigned1_value(self, p):
	    '''
	    assigned1_value : expression
	    '''
	    p[0] = p[1]
	    pass

	def p_expression(self, p):
	    '''
	    expression : anfp
	                | num_expr
	    '''
	    if len(p) == 4:
	        p[0] = p[2]
	    else:
	        p[0] = p[1]
	    pass

	def p_num_expr(self, p):
	    '''
	    num_expr : num
	            | rec_num
	            | LPAREN num_expr RPAREN

	    rec_num : num_expr PLUS num_expr
	            | num_expr MINUS num_expr
	            | num_expr STAR num_expr
	            | num_expr DIV num_expr
	            | MINUS num_expr %prec UMINUS
	    '''

	    if len(p) == 2:
	        p[0] = p[1]
	    elif len(p) == 3:
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
	        # parenthesis handle
	        elif p[1] == "(":
	            p[0] = p[2]
	    pass

	def p_expression2(self, p):
	    '''
	    expression2 : anfp

	    '''
	    p[0] = p[1]
	    pass

	def p_anfp(self, p):
	    '''
	    anfp : reference
	        | pointer
	        | variable
	        | rec_anfp
	        | LPAREN anfp RPAREN
	    '''

	    if len(p) == 4:
	        p[0] = p[2]
	    else:
	        p[0] = p[1]
	    pass

	def p_rec_anfp(self, p):
	    '''
	    rec_anfp : MINUS anfp %prec UMINUS
	        | anfp PLUS anfp
	        | anfp MINUS anfp
	        | anfp STAR anfp
	        | anfp DIV anfp
	        | anfp PLUS num_expr
	        | num_expr PLUS anfp
	        | anfp MINUS num_expr
	        | num_expr MINUS anfp
	        | anfp STAR num_expr
	        | num_expr STAR anfp
	        | anfp DIV num_expr
	        | num_expr DIV anfp
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

	def p_error(self, p):
	    if p:
	        raise Exception("syntax error at '%s' on line no '%d'" % (p.value, p.lineno))
	    else:
	        raise Exception("syntax error at EOF")

	def process(self, data):
	    try:
	        a = yacc.parse(data, lexer=self.lexer.lexer)
	        for node in a:
	            node.print_tree()
	            print()
	    except Exception as e:
	        print(e, file=sys.stderr)