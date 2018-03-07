from .Lexer import Lexer
import ply.yacc as yacc

import sys

from .AST import ASTNode, rev_binary_ops, rev_unary_ops

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
        ('left', 'RPAREN'),
        ('left', 'ELSE'),
    )

    def p_main(self, p):
        '''
        main : VOID MAIN LPAREN RPAREN LBRACE body RBRACE
        '''
        p[0] = p[6]
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
        list_stat : statement list_stat 
        '''
        p[0] = ASTNode("BLOCK", [])
        if len(p) != 1:
            if p[1] is not None:
                p[0].children.append(p[1])
            p[0].children.extend(p[2].children)
        pass

    def p_statement(self, p):
        '''
        statement : matched_stmt
                | unmatched_stmt

        other : declaration SEMICOLON
                | assignment SEMICOLON
                | while
        '''
        p[0] = p[1]
        pass

    def p_if_stmt(self, p):
        '''
        temp1 : matched_stmt
                | SEMICOLON
                | LBRACE list_stat RBRACE

        matched_stmt : IF LPAREN bool_expr RPAREN temp1 ELSE temp1
                    | other

        unmatched_stmt : IF LPAREN bool_expr RPAREN temp1
                    | IF LPAREN bool_expr RPAREN unmatched_stmt
                    | IF LPAREN bool_expr RPAREN temp1 ELSE unmatched_stmt
        '''
        if len(p) == 2:
            if p[1] == ";":
                p[0] = ASTNode("BLOCK", [])
            else:
                p[0] = p[1]

        elif len(p) == 4:
            p[0] = p[2]

        else:
            if_body_node = ASTNode("BLOCK", [])
            else_body_node = ASTNode("BLOCK", [])

            if len(p) >= 6:
                if p[5].label == "BLOCK":
                    if_body_node = p[5]
                else:
                    if_body_node.children.append(p[5])

            if len(p) == 8:
                if p[7].label == "BLOCK":
                    else_body_node = p[7]
                else:
                    else_body_node.children.append(p[7])

            p[0] = ASTNode("IF", [p[3], if_body_node, else_body_node])
                        
    def p_while(self, p):
        '''
        while : WHILE LPAREN bool_expr RPAREN LBRACE list_stat RBRACE
                | WHILE LPAREN bool_expr RPAREN statement
                | WHILE LPAREN bool_expr RPAREN SEMICOLON
        '''

        if len(p) == 6:
            if p[5] == ";":
                p[0] = ASTNode("WHILE", [p[3], ASTNode("BLOCK", [])])
            else:
                p[0] = ASTNode("WHILE", [p[3], ASTNode("BLOCK", [p[5]])])
        else:
            p[0] = ASTNode("WHILE", [p[3], p[6]])


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
        
        p[0] = p[1]
        pass

    def p_bool_expr(self, p):
        '''
        bool_expr : variable
                | num
                | pointer
                | reference
                | LPAREN num_expr RPAREN
                | NOT bool_expr
                | bool_expr AND bool_expr
                | bool_expr OR bool_expr
                | bool_expr EQ bool_expr
                | bool_expr NEQ bool_expr
                | bool_expr LESS bool_expr
                | bool_expr GRT bool_expr
                | bool_expr LESS_EQ bool_expr
                | bool_expr GRT_EQ bool_expr
               
        '''
        
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ASTNode(rev_binary_ops[p[1]], [p[2]])
        elif p[1] == "(":
            p[0] = p[2]
        else:
            p[0] = ASTNode(rev_binary_ops[p[2]], [p[1], p[3]])

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
                | num_expr AMP num_expr %prec B_AND
                | num_expr B_OR num_expr
                
        '''

        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ASTNode(rev_unary_ops[p[1]], [p[2]])
        elif p[1] == "(":
                p[0] = p[2]
        else:
            p[0] = ASTNode(rev_binary_ops[p[2]], [p[1], p[3]])
            
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

            | anfp AMP anfp %prec B_AND
            | anfp B_OR anfp
            | num_expr AMP anfp %prec B_AND
            | num_expr B_OR anfp
            | anfp AMP num_expr %prec B_AND
            | anfp B_OR num_expr
        '''

        if len(p) == 3:
            p[0] = ASTNode(rev_unary_ops[p[1]], [p[2]])
        else:
            p[0] = ASTNode(rev_binary_ops[p[2]], [p[1], p[3]])

        pass

    def p_error(self, p):
        if p:
            raise Exception("syntax error at '%s' on line no '%d'" % (p.value, p.lineno))
        else:
            raise Exception("syntax error at EOF")

    def process(self, data):
        try:
            a = yacc.parse(data, lexer=self.lexer.lexer)
            for node in a.children:
                if node is not None:
                    node.print_tree()
                    print()

            a.generate_flow_graph()
            a.print_flow_graph()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e, file=sys.stderr)