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
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'B_OR'),
        ('left', 'B_AND'),
        ('left', 'EQ', 'NEQ'),
        ('left', 'LESS', 'LESS_EQ', 'GRT', 'GRT_EQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'STAR', 'DIV'),
        ('right', 'UMINUS', 'REF', 'AMP'),
        ('right', 'NOT'),
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

    def p_single_stat(self, p):
        '''
        single_stat : statement SEMICOLON
                | if_stmt

        '''
        p[0] = p[1]

    def p_list_stat(self, p):
        '''
        list_stat :
        list_stat : single_stat list_stat 
        '''
        p[0] = []
        if len(p) != 1:
            p[0].append(p[1])
            p[0].extend(p[2])
        pass

    def p_statement(self, p):
        '''
        statement : declaration
                | assignment
        '''
                # | if_stmt
                # | while_stmt
                # | list_assignments
        p[0] = p[1]
        pass

    def p_if_stmt(self, p):
        '''
        if_stmt : IF LPAREN expression RPAREN single_stat else_stmt
                | IF LPAREN expression RPAREN SEMICOLON else_stmt
                | IF LPAREN expression RPAREN LBRACE list_stat RBRACE else_stmt

        '''
        if len(p) == 7:
            if p[5] == ";":
                p[5] = []

            if p[6] is not None:
                p[0] = ASTNode("IF", [p[3], p[5], p[6]])
            else:
                p[0] = ASTNode("IF", [p[3], p[5]])
        else:
            if p[8] is not None:
                p[0] = ASTNode("IF", [p[3], p[6], p[8]])
            else:
                p[0] = ASTNode("IF", [p[3], p[6]])

    def p_else_stmt(self, p):
        '''
        else_stmt :
                | ELSE single_stat
                | ELSE SEMICOLON
                | ELSE LBRACE list_stat RBRACE

        '''
        if len(p) == 1:
            p[0] = None
        elif len(p) == 3:
            if p[2] == ";":
                p[0] = ASTNode("ELSE", [])
            else:    
                p[0] = ASTNode("ELSE", [p[2]])
        else:
            p[0] = ASTNode("ELSE", [p[3]])


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

                | NOT num_expr
                | num_expr AND num_expr
                | num_expr OR num_expr
                | num_expr EQ num_expr
                | num_expr NEQ num_expr
                | num_expr LESS num_expr
                | num_expr GRT num_expr
                | num_expr LESS_EQ num_expr
                | num_expr GRT_EQ num_expr
                | num_expr AMP num_expr %prec B_AND
                | num_expr B_OR num_expr
        '''

        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            if p[2] == '-':
                p[0] = ASTNode("UMINUS", [p[2]])
            elif p[2] == '!':
                p[0] = ASTNode("NOT", [p[2]])
        else:
            if p[2] == "+":
                p[0] = ASTNode("PLUS", [p[1], p[3]])
            elif p[2] == "-":
                p[0] = ASTNode("MINUS", [p[1], p[3]])
            elif p[2] == "*":
                p[0] = ASTNode("MUL", [p[1], p[3]])
            elif p[2] == "/":
                p[0] = ASTNode("DIV", [p[1], p[3]])
            elif p[2] == "&&":
                p[0] = ASTNode("AND", [p[1], p[3]])
            elif p[2] == "||":
                p[0] = ASTNode("OR", [p[1], p[3]])
            elif p[2] == "==":
                p[0] = ASTNode("EQ", [p[1], p[3]])
            elif p[2] == "!=":
                p[0] = ASTNode("NEQ", [p[1], p[3]])
            elif p[2] == "<":
                p[0] = ASTNode("LESS", [p[1], p[3]])
            elif p[2] == ">":
                p[0] = ASTNode("GRT", [p[1], p[3]])
            elif p[2] == "<=":
                p[0] = ASTNode("LESS_EQ", [p[1], p[3]])
            elif p[2] == ">=":
                p[0] = ASTNode("GRT_EQ", [p[1], p[3]])
            elif p[2] == "&":
                p[0] = ASTNode("B_AND", [p[1], p[3]])
            elif p[2] == "|":
                p[0] = ASTNode("B_OR", [p[1], p[3]])
            

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

            | NOT anfp

            | anfp AND anfp
            | anfp OR anfp
            | anfp EQ anfp
            | anfp NEQ anfp
            | anfp LESS anfp
            | anfp GRT anfp
            | anfp LESS_EQ anfp
            | anfp GRT_EQ anfp
            | anfp AMP anfp %prec B_AND
            | anfp B_OR anfp

            | num_expr AND anfp
            | num_expr OR anfp
            | num_expr EQ anfp
            | num_expr NEQ anfp
            | num_expr LESS anfp
            | num_expr GRT anfp
            | num_expr LESS_EQ anfp
            | num_expr GRT_EQ anfp
            | num_expr AMP anfp %prec B_AND
            | num_expr B_OR anfp

            | anfp AND num_expr
            | anfp OR num_expr
            | anfp EQ num_expr
            | anfp NEQ num_expr
            | anfp LESS num_expr
            | anfp GRT num_expr
            | anfp LESS_EQ num_expr
            | anfp GRT_EQ num_expr
            | anfp AMP num_expr %prec B_AND
            | anfp B_OR num_expr

    '''

        if len(p) == 3:
            if p[2] == '-':
                p[0] = ASTNode("UMINUS", [p[2]])
            elif p[2] == '!':
                p[0] = ASTNode("NOT", [p[2]])

        else:
            if p[2] == "+":
                p[0] = ASTNode("PLUS", [p[1], p[3]])
            elif p[2] == "-":
                p[0] = ASTNode("MINUS", [p[1], p[3]])
            elif p[2] == "*":
                p[0] = ASTNode("MUL", [p[1], p[3]])
            elif p[2] == "/":
                p[0] = ASTNode("DIV", [p[1], p[3]])
            elif p[2] == "&&":
                p[0] = ASTNode("AND", [p[1], p[3]])
            elif p[2] == "||":
                p[0] = ASTNode("OR", [p[1], p[3]])
            elif p[2] == "==":
                p[0] = ASTNode("EQ", [p[1], p[3]])
            elif p[2] == "!=":
                p[0] = ASTNode("NEQ", [p[1], p[3]])
            elif p[2] == "<":
                p[0] = ASTNode("LESS", [p[1], p[3]])
            elif p[2] == ">":
                p[0] = ASTNode("GRT", [p[1], p[3]])
            elif p[2] == "<=":
                p[0] = ASTNode("LESS_EQ", [p[1], p[3]])
            elif p[2] == ">=":
                p[0] = ASTNode("GRT_EQ", [p[1], p[3]])
            elif p[2] == "&":
                p[0] = ASTNode("B_AND", [p[1], p[3]])
            elif p[2] == "|":
                p[0] = ASTNode("B_OR", [p[1], p[3]])

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