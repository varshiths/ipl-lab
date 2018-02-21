import ply.lex as lex

class Lexer:

	tokens = [
	        'NAME', 'NUMBER',
	        'ASSIGN',
	        'COMMA',
	        'LPAREN', 'RPAREN',
	        'LBRACE', 'RBRACE',
	        'SEMICOLON', 'STAR', 'AMP',
	        'PLUS', 'MINUS', 'DIV', 'LESS', 'GRT', 'LESS_EQ', 'GRT_EQ', 'EQ', 'NEQ', 'AND',
	        'OR', 'B_OR', 'NOT'
	]

	reserved = {
	    'int' : 'INT',
	    'void' : 'VOID',
	    'main' : 'MAIN',
	    'if'   : 'IF',
	    #'while' : 'WHILE',
	    'else' : 'ELSE'
	}
	tokens += list(reserved.values())

	# t_ignore = "( \t)|(//.*)"
	t_ignore = " \t"

	t_EQ = r'=='
	t_ASSIGN = r'='
	t_COMMA = r','

	t_LPAREN = r'\('
	t_RPAREN = r'\)'

	t_LBRACE = r'\{'
	t_RBRACE = r'\}'

	t_SEMICOLON = r';'
	t_STAR = r'\*'
	t_AND = r'&&'
	t_AMP = r'&'

	t_PLUS = r'\+'
	t_MINUS = r'\-'
	t_DIV = r'/'

	t_NUMBER = r'\d+'

	t_LESS_EQ = r'<='
	t_LESS = r'<'
	t_GRT_EQ = r'>='
	t_GRT = r'>'
	t_NEQ = r'!='
	t_NOT = r'!'
	t_OR = r'\|\|'
	t_B_OR = r'\|'
	



	def t_NAME(self, t):
	    r'[a-zA-Z_][a-zA-Z0-9_]*'
	    t.type = Lexer.reserved.get(t.value, 'NAME')
	    return t

	def t_newline(self, t):
	    r'\n+'
	    t.lexer.lineno += len(t.value)

	def t_error(self, t): 
	    print("Illegal character '%s'" % t.value[0])
	    t.lexer.skip(1)

	def __init__(self, debug_flag=False):
		self.lexer = lex.lex(debug=debug_flag, module=self)		