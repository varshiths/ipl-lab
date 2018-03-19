from .Lexer import Lexer
import ply.yacc as yacc

import sys

import io
from contextlib import redirect_stdout

from .AST import ASTNode, rev_binary_ops, rev_unary_ops

from .Sym import Sym

class Parser:

    tokens = Lexer.tokens

    def __init__(self, parser_debug=False, lexer_debug=False):
        self.lexer = Lexer(lexer_debug)
        self.parser = yacc.yacc(debug=parser_debug, module=self)
        self.symbol_table = Sym()

    precedence = (
        ('right', 'ASSIGN'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NEQ'),
        ('left', 'LESS', 'LESS_EQ', 'GRT', 'GRT_EQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'STAR', 'DIV'),
        ('right', 'UMINUS', 'REF', 'AMP'),
        ('right', 'NOT'),
        ('left', 'RPAREN'),
        ('left', 'ELSE'),
        ('left', 'SEMICOLON'),
        ('left', 'TYPE'),
    )

    def p_prog(self, p):
        '''
        prog : var_decls proc_decls
            | proc_decls

        '''
        if len(p) == 3:
            for entity in p[1]:
                self.symbol_table.add_entry(
                    entity,
                    "global"
                    )

        p[0] = self.symbol_table
        pass

    def p_var_decls(self, p):
        '''
        var_decls : declaration SEMICOLON
                    | var_decls declaration SEMICOLON
        '''
                    # | declaration SEMICOLON var_decls 
        p[0] = []
        if len(p) == 3:
            p[0].extend(p[1])
        else:
            p[0].extend(p[1]) 
            p[0].extend(p[2]) 
            # p[0].extend(p[3]) 
        pass

    def p_proc_decls(self, p):
        '''
        proc_decls : 
                | proc proc_decls
        '''
        pass

    def p_proc(self, p):
        '''
        proc : type variable LPAREN RPAREN SEMICOLON
            | type pointer_d LPAREN RPAREN SEMICOLON

            | type variable LPAREN proc_args RPAREN SEMICOLON
            | type pointer_d LPAREN proc_args RPAREN SEMICOLON

            | type variable LPAREN RPAREN LBRACE body RBRACE
            | type pointer_d LPAREN RPAREN LBRACE body RBRACE

            | type variable LPAREN proc_args RPAREN LBRACE body RBRACE
            | type pointer_d LPAREN proc_args RPAREN LBRACE body RBRACE
        '''
        procedure_name = p[2]["attr"]["name"]
        ret_type = {
            "base_type" : p[1],
            "level" : p[2]["attr"]["level"]
        }
        list_of_parameters = []

        if len(p) == 6:
            pass
        elif len(p) == 7:
            list_of_parameters = p[4]
        elif len(p) == 8:
            pass
        elif len(p) == 9:
            list_of_parameters = p[4]

        self.symbol_table.add_procedure(procedure_name, ret_type, list_of_parameters)

        list_declrs = []
        if len(p) == 8:
            list_declrs = p[6]["attr"]
        elif len(p) == 9:
            list_declrs = p[7]["attr"]
        
        for declr in list_declrs:
            self.symbol_table.add_entry(declr, procedure_name)
        pass

    def p_proc_args(self, p):
        '''
        proc_args : arg
                | arg COMMA proc_args
        '''
        p[0] = []
        if len(p) == 2:
            p[0].append(p[1])
        else:
            p[0].append(p[1]) 
            p[0].extend(p[3]) 
        pass

    def p_arg(self, p):
        '''
        arg : type declr_entity
            | type
        '''
        name = None
        base_type = p[1]
        level = 0

        if len(p) == 3:
            name = p[2]["attr"]["name"]
            level = p[2]["attr"]["level"]

        p[0] = {
            "name" : name,
            "base_type" : base_type,
            "level" : level
        }
        pass

    def p_body(self, p):
        '''
        body : list_declr list_stat ret_stmt
                | list_declr list_stat
        '''
        node = None
        if len(p) == 3:
            node = p[2]
        else:
            p[2].children.append(p[3])
            node = p[2]

        attr = p[1]

        p[0] = {
            "node" : node,
            "attr" : attr
        }

    def p_ret_stmt(self, p):
        '''
        ret_stmt : RETURN expression SEMICOLON
        '''
        p[0] = ASTNode("RETURN", [p[2]])

    def p_list_declr(self, p):
        '''
        list_declr :
                | declaration SEMICOLON list_declr
        '''

        attr = []
        if len(p) == 4:
            attr.extend(p[1])
            attr.extend(p[3])
        p[0] = attr

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

        other :  assignment SEMICOLON
                | func_call SEMICOLON
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

            if len(p) == 8:
                p[0] = ASTNode("IF", [p[3], if_body_node, else_body_node])
            else:
                p[0] = ASTNode("IF", [p[3], if_body_node, ASTNode("EBLOCK", [])])
                        
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
        type : INT %prec TYPE
            | FLOAT %prec TYPE
            | VOID %prec TYPE
        '''
        p[0] = p[1]           
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
        p[0] = {}
        p[0]["node"] = None
        p[0]["attr"] = {
            "name" : p[2]["attr"]["name"], 
            "base_type" : p[2]["attr"]["base_type"], 
            "level" : 1 + p[2]["attr"]["level"]
        }
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
        node = ASTNode("VAR", [ASTNode(p[1], [])])

        attr = {
            "name": p[1],
            "base_type": None,
            "level": 0
        }

        p[0] = {
            "node" : node,
            "attr" : attr
        }
        pass

    def p_declr_entity_var(self, p):
        '''
        declr_entity : variable
        '''
        p[0] = {}
        p[0]["node"] = None
        p[0]["attr"] = p[1]["attr"]
        pass

    def p_declr_entity_pointer(self, p):
        '''
        declr_entity : pointer_d
        '''
        p[0] = p[1]
        pass

    def p_list_var(self, p):
        '''
        list_var : declr_entity
                | list_var COMMA declr_entity
        '''
        p[0] = []
        if len(p) == 2:
            p[0].append(p[1]["attr"])
        else:
            p[0].extend(p[1]) 
            p[0].append(p[3]["attr"]) 
        pass

    def p_declaration(self, p):
        '''
        declaration : type list_var
        '''
        p[0] = []
        for entity in p[2]:
            entity["base_type"] = p[1]
            p[0].append(entity)
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
        bool_expr : 
                | LPAREN bool_expr RPAREN
                | NOT bool_expr
                | bool_expr AND bool_expr
                | bool_expr OR bool_expr
                | expression EQ expression
                | expression NEQ expression
                | expression LESS expression
                | expression GRT expression
                | expression LESS_EQ expression
                | expression GRT_EQ expression
               
        '''
        
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ASTNode(rev_unary_ops[p[1]], [p[2]])
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
            | func_call
            | LPAREN anfp RPAREN
        '''

        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]
        pass

    def p_func_call(self, p):
        '''
        func_call : NAME LPAREN RPAREN
                | NAME LPAREN func_args RPAREN

        func_args : func_arg
                    | func_arg COMMA func_args

        func_arg : num
                | declr_entity
                | func_call
        '''
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

            # with io.StringIO() as buf, redirect_stdout(buf):
            #     a.print_tree()
            #     ast = buf.getvalue()

            # a.generate_flow_graph()
            # with io.StringIO() as buf, redirect_stdout(buf):
            #     a.print_flow_graph()
            #     cfg = buf.getvalue()[:-1]

            a.print_symbol_table()
            return "ast", "cfg"

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e, file=sys.stderr)

            return "", ""