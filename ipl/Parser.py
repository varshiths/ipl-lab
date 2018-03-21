from .Lexer import Lexer
import ply.yacc as yacc

import sys

import io
from contextlib import redirect_stdout

from .AST import ASTNode, rev_binary_ops, rev_unary_ops
from .AST import binary_ops, unary_ops

from .Sym import Sym

def remove_name(x):
    p = x.copy()
    p.pop("name")
    return p

class Parser:

    tokens = Lexer.tokens

    def __init__(self, parser_debug=False, lexer_debug=False):
        self.lexer = Lexer(lexer_debug)
        self.parser = yacc.yacc(debug=parser_debug, module=self)
        self.symbol_table = Sym()
        self.syntax_tree = None

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

        node = None
        if len(p) == 2:
            node = ASTNode("GLOBAL", p[1])
        else:
            node = ASTNode("GLOBAL", p[2])
        self.syntax_tree = node

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
        node = []
        if len(p) == 3:
            node.append(p[1])
            node.extend(p[2])
        p[0] = node

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
        is_prototype = False

        if len(p) == 6:
            is_prototype = True
            pass
        elif len(p) == 7:
            is_prototype = True
            list_of_parameters = p[4]
        elif len(p) == 8:
            pass
        elif len(p) == 9:
            list_of_parameters = p[4]

        self.symbol_table.add_procedure(procedure_name, ret_type, list_of_parameters, prototype=is_prototype)

        list_declrs = []
        if len(p) == 8:
            list_declrs = p[6]["attr"]
        elif len(p) == 9:
            list_declrs = p[7]["attr"]
        
        for declr in list_declrs:
            self.symbol_table.add_entry(declr, procedure_name)

        block = ASTNode("BLOCK", [])
        if len(p) == 8:
            block = p[6]["node"]
        elif len(p) == 9:
            block = p[7]["node"]

        p[0] = ASTNode("FUNCTION", [ASTNode("ID", [ASTNode(procedure_name, [is_prototype])]), block])

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
        arg :  prototype_type variable
            | prototype_type
        '''
        name = None
        base_type = p[1]["base_type"]
        level = p[1]["level"]

        if len(p) == 3:
            name = p[2]["attr"]["name"]

        p[0] = {
            "name" : name,
            "base_type" : base_type,
            "level" : level
        }
        pass

    def p_prototype_type(self, p):
        '''
        prototype_type : type
                    | prototype_type STAR
        '''
        if len(p) == 2:
            p[0] = {"base_type": p[1], "level": 0}
        else:
            p[0] = {"base_type": p[1]["base_type"], "level": p[1]["level"] + 1 }

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
        node = ASTNode("DEREF", [p[2]["node"]])
        p[0] = {
            "node" : node
        }
        pass

    def p_pointer_d(self, p):
        '''
        pointer_d : STAR variable %prec REF
                    | STAR pointer_d %prec REF
        '''
        node = ASTNode("DEREF", [p[2]["node"]])

        p[0] = {}
        p[0]["node"] = node
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
        node = p[1]["node"]
        p[0] = {
            "node" : node
        }
        pass

    def p_reference(self, p):
        '''
        reference : AMP combine
        '''
        node = ASTNode("ADDR", [p[2]["node"]])
        p[0] = {
            "node" : node
        }
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
        p[0]["node"] = p[1]["node"]
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
        p[0] = ASTNode("ASGN", [p[1]["node"], p[3]])
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
        p[0] = ASTNode("ASGN", [p[1]["node"], p[3]])
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
            | func_call
            | LPAREN anfp RPAREN
        '''

        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]["node"]
        pass

    def p_func_call(self, p):
        '''
        func_call : NAME LPAREN RPAREN
                | NAME LPAREN func_args RPAREN
        '''
        if p[1] not in self.symbol_table.keys() or self.symbol_table[p[1]]["type"] != 'procedure':
            raise Exception("Procedure %s not declared" % (p[1]))

        node_children = [ ASTNode("ID", [ASTNode(p[1], [])]) ]
        if len(p) == 5:
            node_children.extend(p[3])
        node = ASTNode("CALL", node_children)
        p[0] = node
        pass

    def p_func_args(self, p):
        '''
        func_args : func_arg
                    | func_arg COMMA func_args
        '''
        node = []
        if len(p) == 2:
            node.append(p[1])
        else:
            node.append(p[1])
            node.extend(p[3])
        p[0] = node

    def p_func_arg_num(self, p):
        '''
        func_arg : num
                | func_call
        '''
        p[0] = p[1]
        pass

    def p_func_arg(self, p):
        '''
        func_arg : declr_entity
                | reference  
        '''
        p[0] = p[1]["node"]
        pass

    def p_rec_anfp(self, p):
        '''
        anfp : rec_anfp

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

        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ASTNode(rev_unary_ops[p[1]], [p[2]])
        else:
            p[0] = ASTNode(rev_binary_ops[p[2]], [p[1], p[3]])

        pass

    def p_error(self, p):
        if p:
            raise Exception("syntax error at '%s' on line no '%d'" % (p.value, p.lineno))
        else:
            raise Exception("syntax error at EOF")

    def print_syntax_tree(self):
        self.syntax_tree.print_tree(debug=True)

    def print_symbol_table(self):
        self.symbol_table.print_table()

    def rec_type_check(self, node, scope):

        children = node.children

        if node.label == "GLOBAL":
            scope = "global"
            for child in children:
                self.rec_type_check(child, scope)

        elif node.label == "FUNCTION":
            func_name = children[0].children[0].label
            is_prototype = children[0].children[0].children[0]
            if self.symbol_table[func_name]["return_type"]["base_type"] != "void" and not is_prototype:
                if len(children[1].children) == 0 or children[1].children[-1].label != "RETURN":
                    raise Exception("Return statement missing")

            self.rec_type_check(children[1], func_name)

        elif node.label == "RETURN":
            ret_type = self.rec_type_check(children[0], scope)
            ret_type.pop("dnp")
            func_name = scope
            if ret_type != self.symbol_table[func_name]["return_type"]:
                message = str(ret_type) + " " + str(self.symbol_table[func_name]["return_type"])
                raise Exception("Return type mismatch: " + message)

        elif node.label == "BLOCK" or node.label == "EBLOCK":
            for child in children:
                self.rec_type_check(child, scope)

        elif node.label == "CALL":
            func_name = children[0].children[0].label

            if func_name not in self.symbol_table.keys():
                message = func_name
                raise Exception("Function not defined: " + message)
            if self.symbol_table[func_name]["type"] != "procedure":
                message = func_name
                raise Exception("Not a function: " + message)

            calllist = [self.rec_type_check(x, scope) for x in children[1:]]
            for i, callparam in enumerate(calllist):
                if callparam["dnp"]:
                    raise Exception("Direct use of non-pointer")
                calllist[i].pop("dnp")

            plist = list(map(lambda x: remove_name(x), self.symbol_table[func_name]["parameters"]))
            result = [ plist[i] == calllist[i] for i in range(min(len(calllist), len(plist))) ]
            if (len(plist) != len(calllist)) or (False in result):
                raise Exception("Function parameters mismatch: ")

            return self.symbol_table[func_name]["return_type"]

        elif node.label == "IF":
            ntype = self.rec_type_check(children[0], scope)
            if ntype["base_type"] != "boolean":
                raise Exception("Invalid control condition")
            self.rec_type_check(children[1], scope)
            self.rec_type_check(children[2], scope)

        elif node.label == "WHILE":
            self.rec_type_check(children[0], scope)
            if ntype["base_type"] != "boolean":
                raise Exception("Invalid control condition")
            self.rec_type_check(children[1], scope)

        elif node.label == "DEREF":
            ret_type = self.rec_type_check(children[0], scope)
            if ret_type["level"] <= 0:
                raise Exception("Too much indirection: ")
            ret_type["level"] -= 1
            ret_type["dnp"] = False
            return ret_type

        elif node.label == "ADDR":
            ret_type = self.rec_type_check(children[0], scope)
            ret_type["level"] += 1
            ret_type["dnp"] = False
            return ret_type

        elif node.label == "CONST":
            base_type = ""
            level = 0

            try:
                int(children[0].label)
                base_type = "int"
            except ValueError:
                base_type = "float"

            ntype = {
                "base_type" : base_type,
                "level" : level,
                "dnp" : False
            }
            return ntype

        elif node.label == "VAR":
            name = children[0].label
            ntype, exists = self.symbol_table.get_entry(name, scope)

            if not exists:
                message = name
                raise Exception("Variable doesn't exist in scope: " + message)

            ntype["dnp"] = ntype["level"] == 0
            return ntype

        elif node.label == "ASGN":
            ret_type_lop = self.rec_type_check(children[0], scope)
            ret_type_rop = self.rec_type_check(children[1], scope)

            if ret_type_lop["dnp"]:
                raise Exception("Direct use of non-pointer")
            if ret_type_rop["dnp"]:
                raise Exception("Direct use of non-pointer")

            if ret_type_lop != ret_type_rop:
                raise Exception("Type mismatch for = at: ")

        elif node.label in binary_ops.keys():
            ret_type_lop = self.rec_type_check(children[0], scope)
            ret_type_rop = self.rec_type_check(children[1], scope)

            if ret_type_lop["dnp"]:
                raise Exception("Direct use of non-pointer")
            if ret_type_rop["dnp"]:
                raise Exception("Direct use of non-pointer")

            ntype = {
                "dnp" : False
            }

            if node.label in ['PLUS', 'MINUS', 'MUL', 'DIV']:
                if ret_type_lop["base_type"] == "boolean" or ret_type_lop != ret_type_rop:
                    raise Exception("Type mismatch for "+node.label+" at: ")
                ntype = ret_type_lop

            elif node.label in ["AND", "OR"]:
                if ret_type_lop["base_type"] != "boolean" or ret_type_lop != ret_type_rop:
                    raise Exception("Type mismatch for "+node.label+" at: ")
                ntype["base_type"] = "boolean"

            else:
                if ret_type_lop["base_type"] == "boolean" or ret_type_lop != ret_type_rop:
                    raise Exception("Type mismatch for "+node.label+" at: ")
                ntype["base_type"] = "boolean"
            return ntype

        elif node.label in unary_ops.keys():
            ret_type = self.rec_type_check(children[0], scope)

            ntype = {
                "dnp" : False
            }
            
            if node.label == "UMINUS":
                if ret_type["base_type"] == "boolean":
                    raise Exception("Type mismatch for - at: ")
                ntype = ret_type
            elif node.label == "NOT":
                if ret_type["base_type"] != "boolean":
                    raise Exception("Type mismatch for ! at: ")
                ntype["base_type"] = "boolean"
            return ntype

        else:
            raise Exception("Error in type check implementation")

    def type_check(self):
        self.rec_type_check(self.syntax_tree, None)

    def process(self, data):
        try:
            yacc.parse(data, lexer=self.lexer.lexer)

            self.type_check()

            with io.StringIO() as buf, redirect_stdout(buf):
                self.print_syntax_tree()
                ast = buf.getvalue()

            # a.generate_flow_graph()
            # with io.StringIO() as buf, redirect_stdout(buf):
            #     a.print_flow_graph()
            #     cfg = buf.getvalue()[:-1]

            with io.StringIO() as buf, redirect_stdout(buf):
                self.print_symbol_table()
                sym = buf.getvalue()

            return ast, "", sym

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Error: " + str(e), file=sys.stderr)

            return "", "", ""