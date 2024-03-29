binary_ops = {'PLUS':'+', 'MINUS':'-', 'MUL':'*', 'DIV':'/', 'LT':'<', 'GT':'>', 'LE':'<=', 'GE':'>=', 'EQ':'==', 'NE':'!=', 'AND':'&&',
            'OR':'||'}

unary_ops = {'UMINUS':'-', 'NOT':'!'}
rev_unary_ops = {}
rev_binary_ops = {}
for key, val in binary_ops.items():
    rev_binary_ops[val] = key

for key, val in unary_ops.items():
    rev_unary_ops[val] = key

def tabs(n):
    return "\t"*n

class Block:
    def __init__(self, control_type=False, return_type="false"):
        self.control_type = control_type
        self.return_type = return_type
        self.list_stat = []
        self.set = 0
        self.goto1 = None
        self.goto2 = None

    def setControlType(self, control_type):
        self.control_type = control_type

    def setGoto(self, goto):

        if self.set == 0:
            self.set += 1
            self.goto1 = goto

        elif self.set == 1:
            if not self.control_type:
                raise Exception()
            else:
                self.set += 1
                self.goto2 = goto
        else:
            raise Exception()

    def setGoto1(self, goto1):
        self.goto1 = goto1

    def setGoto2(self, goto2):
        self.goto2 = goto2

    def extend(self, stats):
        self.list_stat.extend(stats)

    def append(self, stat):
        self.list_stat.append(stat)

    def getStatementList(self):
        return self.list_stat

    def __repr__(self):
        ret = {}

        ret["control_type"] = self.control_type
        ret["return_type"] = self.return_type
        ret["stats"] = self.list_stat

        if not self.control_type:
            ret["goto"] = self.goto1
        else:
            ret["goto1"] = self.goto1
            ret["goto2"] = self.goto2

        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        return pp.pformat(ret)
        
class Statement:
    def __init__(self, tokens, stat_type="place"):
        self.tokens = tokens
        self.stat_type = stat_type
    
    def __repr__(self):

        list_token_strings = []

        if self.stat_type == "func_ret":
            list_token_strings = [ x.__str__() for x in self.tokens[:2]]
            func_name = self.tokens[2]
            args_str = ",".join([ x.__str__() for x in self.tokens[3:]])
            list_token_strings.append( "%s(%s)" % (func_name, args_str) )
        elif self.stat_type == "CALL":
            func_name = self.tokens[0]
            args_str = ",".join([ x.__str__() for x in self.tokens[1:]])
            list_token_strings.append( "%s(%s)" % (func_name, args_str) )
        else:
            for a in self.tokens:
                list_token_strings.append(a.__str__())

        return " ".join(list_token_strings)

class ASTNode:

    functions = {}
    blocks = {}
    temporaries = {}

    def __init__(self, label, children):
        self.label = label
        self.children = children

    def set_symbol_table(self, symbol_table):
        self.symbol_table = symbol_table
        for child in self.children:
            if isinstance(child, ASTNode):
                child.set_symbol_table(symbol_table)

    def print_tree(self, debug=False, ntabs=0):

        if self.label == "VAR" or self.label == "CONST" or self.label == "ID":
            print(tabs(ntabs), end='')            
            print(self.label, "(", self.children[0].label, ")", sep='')
        elif self.label == "BLOCK" or self.label == "GLOBAL":
            for child in self.children:
                child.print_tree(debug=False, ntabs=ntabs)
        elif self.label == "FUNCTION":

            print()

            func_name = self.children[0].children[0].label
            is_prototype = self.children[0].children[0].children[0]
            parameters = [ (get_type_str(y), x) for x, y in list(self.symbol_table[func_name]["parameters"].items())]
            return_type = self.symbol_table[func_name]["return_type"]

            if is_prototype:
                return

            if func_name == "main":
                print("Function Main")
            else:
                print("FUNCTION %s" % (func_name))
            print("PARAMS (%s)" % (", ".join([x + " " + y for x, y in parameters])))
            print("RETURNS %s" % (get_type_str(return_type, rev=True)))

            func_block = self.children[1]
            for child in func_block.children[:-1]:
                child.print_tree(debug=False, ntabs=ntabs+1)
            func_block.children[-1].print_tree(debug=False, ntabs=ntabs)
            print()

        elif self.label == "CALL":

            func_name = self.children[0].children[0].label
            print(tabs(ntabs), "%s %s(" % (self.label, func_name), sep='')

            non_empty_children = self.children[1:]

            for i, child in enumerate(non_empty_children):
                child.print_tree(debug=False, ntabs=ntabs + 1)
                if i != len(non_empty_children)-1:
                    print(tabs(ntabs+1), ",", sep='')
            print(tabs(ntabs), ")", sep='')

        else:
            print(tabs(ntabs), self.label, sep='')
            print(tabs(ntabs), "(", sep='')

            non_empty_children = [ x for x in self.children if x.label != "EBLOCK"]

            if len(non_empty_children) != 0:
                for i, child in enumerate(non_empty_children):
                    if child is not None:
                        child.print_tree(debug=False, ntabs=ntabs + 1)
                    if i != len(non_empty_children)-1:
                        print(tabs(ntabs+1), ",", sep='')
            if self.label == "WHILE" or self.label == "IF":
                print()
            print(tabs(ntabs), ")", sep='')

        # if self.label == "VAR" or self.label == "CONST" or self.label == "ID":
        #     print(tabs(ntabs), end='')            
        #     print(self.label, "(", self.children[0].label, ")", sep='')
        # elif self.label == "BLOCK" or self.label == "GLOBAL":
        #     for child in self.children:
        #         child.print_tree(ntabs)

        # elif self.label == "FUNCTION":

        #     func_name = self.children[0].children[0].label
        #     is_prototype = self.children[0].children[0].children[0]
        #     parameters = [ (get_type_str(y), x) for x, y in list(self.symbol_table[func_name]["parameters"].items())]
        #     return_type = self.symbol_table[func_name]["return_type"]

        #     if is_prototype:
        #         return

        #     print("FUNCTION %s" % (func_name))
        #     print("PARAMS (%s)" % (", ".join([x + " " + y for x, y in parameters])))
        #     print("RETURNS %s" % (get_type_str(return_type)))

        # else:
        #     print(tabs(ntabs), self.label, sep='')
        #     print(tabs(ntabs), "(", sep='')

        #     non_empty_children = [ x for x in self.children if x.label != "EBLOCK"]

        #     if len(non_empty_children) != 0:
        #         for i, child in enumerate(non_empty_children):
        #             if child is not None:
        #                 child.print_tree(debug=False, ntabs=ntabs + 1)
        #             if i != len(non_empty_children)-1:
        #                 print(tabs(ntabs+1), ",", sep='')
        #     print(tabs(ntabs), ")", sep='')


        #         # print(tabs(ntabs), self.label, sep='')
        #         # print(tabs(ntabs), "(", sep='')

        #         # non_empty_children = [ x for x in self.children if x.label != "EBLOCK"]

        #         # if len(non_empty_children) != 0:
        #         #     for i, child in enumerate(non_empty_children):
        #         #         if child is not None:
        #         #             child.print_tree(ntabs + 1)
        #         #         if i != len(non_empty_children)-1:
        #         #             print(tabs(ntabs+1), ",", sep='')
        #         # if self.label == "WHILE" or self.label == "IF":
        #         #     print()
        #         # print(tabs(ntabs), ")", sep='')
        #     # pass

    def statement(self):
        if self.label == "VAR" or self.label == "CONST":
            type((self.children[0].label))
            return [Statement([self.children[0].label], self.label)]
        elif self.label == "DEREF":
            ret_list = []
            a_list = self.children[0].statement()

            ret_list.extend(a_list[:-1])
            ret_list.append( Statement([ "*" + a_list[-1].__str__() ], self.label) )

            return ret_list

        elif self.label == "ADDR":

            ret_list = []
            a_list = self.children[0].statement()

            ret_list.extend(a_list[:-1])
            ret_list.append( Statement([ "&" + a_list[-1].__str__() ], self.label) )
            
            return ret_list

        elif self.label == "ASGN":

            a_list = self.children[0].statement()
            b_list = self.children[1].statement()

            ret_list = []
            ret_list.extend(a_list[:-1])
            ret_list.extend(b_list[:-1])

            lbl = self.label
            lst_tokens = [a_list[-1], "=", b_list[-1]]

            stat = Statement(lst_tokens, lbl)
            ret_list.append(stat)

            return ret_list

        elif self.label in binary_ops.keys():

            a_list = self.children[0].statement()
            b_list = self.children[1].statement()

            curr_temp = len(ASTNode.temporaries.keys())
            ASTNode.temporaries[curr_temp] = Statement(["t%d" % curr_temp, "=", a_list[-1], binary_ops[self.label], b_list[-1]], self.label)

            ret_list = []
            ret_list.extend(a_list[:-1])
            ret_list.extend(b_list[:-1])
            ret_list.append(ASTNode.temporaries[curr_temp])

            ret_list.append(Statement(["t%d" % curr_temp]))

            return ret_list

        elif self.label in unary_ops.keys():
            
            a_list = self.children[0].statement()

            curr_temp = len(ASTNode.temporaries.keys())
            ASTNode.temporaries[curr_temp] = Statement(["t%d" % curr_temp, "=", unary_ops[self.label], a_list[-1]], self.label)

            ret_list = []
            ret_list.extend(a_list[:-1])
            ret_list.append(ASTNode.temporaries[curr_temp])

            ret_list.append(Statement(["t%d" % curr_temp]))

            return ret_list

        elif self.label == "CALL":

            func_name = self.children[0].children[0].label
            args_list = [ child.statement() for child in self.children[1:] ]
            
            args_temps = []
            for i, arg in enumerate(args_list):
                args_temps.append(arg[-1])
                args_list[i] = arg[:-1]

            # if call_part_of_expression:
            #     # curr_temp = len(ASTNode.temporaries.keys())

            #     # list_tokens = ["t%d" % curr_temp, "=", func_name]
            #     list_tokens = [func_name]
            #     list_tokens.extend(args_temps)
            #     stat = Statement(list_tokens, "func_ret")

            #     # ret_list = [ stats for stats in arg for arg in args_list ]
            #     ret_list = []
            #     for arg in args_list:
            #         for stats in arg:
            #             ret_list.append(stats)
            #     ret_list.append(stat)
            #     # ret_list.append(ASTNode.temporaries[curr_temp])
            #     # ret_list.append(Statement(["t%d" % curr_temp]))
            # else:

            list_tokens = [func_name]
            list_tokens.extend(args_temps)
            stat = Statement(list_tokens, self.label)

            # ret_list = [ stats for stats in arg for arg in args_list ]
            ret_list = []
            for arg in args_list:
                for stats in arg:
                    ret_list.append(stats)
            ret_list.append(stat)

            return ret_list

    def node_generate_graph(node):

        # print(node.label)
        # print()

        if node is not None:
            if node.label == "BLOCK" or node.label == "EBLOCK" or node.label == "GLOBAL":
                if len(node.children) == 0:
                    return []
                else:
                    curr_block = len(ASTNode.blocks.keys())
                    ASTNode.blocks[curr_block] = Block()
                    for i, child in enumerate(node.children):
                        if child is not None:
                            if  child.label != "IF" \
                                and child.label != "WHILE" \
                                and child.label != "FUNCTION" \
                                and child.label != "RETURN":

                                ASTNode.blocks[curr_block].extend(child.statement())

                                if i == len(node.children)-1:
                                    return [curr_block]
                            else:

                                if len(ASTNode.blocks[curr_block].getStatementList()) == 0:
                                    del ASTNode.blocks[curr_block]
                                else:
                                    ASTNode.blocks[curr_block].setGoto(curr_block+1)

                                block_list = ASTNode.node_generate_graph(child)

                                if i == len(node.children)-1:
                                    return block_list
                                else:
                                    next_block = len(ASTNode.blocks.keys())
                                    for blk in block_list:
                                        ASTNode.blocks[blk].setGoto(next_block)

                                curr_block = len(ASTNode.blocks.keys())
                                ASTNode.blocks[curr_block] = Block()

            elif node.label == "IF":
                curr_block = len(ASTNode.blocks.keys())
                ASTNode.blocks[curr_block] = Block()

                cond_list = node.children[0].statement()
                true_blk = curr_block + 1
                a = ASTNode.node_generate_graph(node.children[1])
                false_blk = len(ASTNode.blocks.keys())
                b = ASTNode.node_generate_graph(node.children[2])

                ASTNode.blocks[curr_block].setControlType(True);
                ASTNode.blocks[curr_block].extend(cond_list[:-1])
                ASTNode.blocks[curr_block].append("if(%s)" % (cond_list[-1]))

                end_list = []
                if len(a) == 0:
                    end_list.append(curr_block)
                else:
                    ASTNode.blocks[curr_block].setGoto(true_blk)
                    end_list.extend(a)

                if len(b) == 0:
                    end_list.append(curr_block)
                else:
                    ASTNode.blocks[curr_block].setGoto(false_blk)
                    end_list.extend(b)

                return end_list

            elif node.label == "WHILE":
                curr_block = len(ASTNode.blocks.keys())
                ASTNode.blocks[curr_block] = Block()

                cond_list = node.children[0].statement()
                true_blk = curr_block + 1
                a = ASTNode.node_generate_graph(node.children[1])

                ASTNode.blocks[curr_block].setControlType(True)
                ASTNode.blocks[curr_block].extend(cond_list[:-1])
                ASTNode.blocks[curr_block].append("if(%s)" % (cond_list[-1]))

                if len(a) != 0:
                    ASTNode.blocks[curr_block].setGoto(true_blk)
                    for blk in a:
                        ASTNode.blocks[blk].setGoto(curr_block)
                else:
                    ASTNode.blocks[curr_block].setGoto(curr_block)

                return [curr_block]

            elif node.label == "FUNCTION":
                procedure_name = node.children[0].children[0].label
                is_prototype = node.children[0].children[0].children[0]

                if not is_prototype:
                    curr_block = len(ASTNode.blocks.keys())
                    ASTNode.functions[curr_block] = procedure_name

                if not is_prototype:
                    body = node.children[1]
                    if len(body.children) == 0 or body.children[-1].label != "RETURN":
                        node.children[1].children.append(ASTNode("RETURN", []))

                    ASTNode.node_generate_graph(node.children[1])

                # adda return statemennt if it isn't there
                

                return []

            elif node.label == "RETURN":
                curr_block = len(ASTNode.blocks.keys())

                if len(node.children) == 1:
                    ASTNode.blocks[curr_block] = Block(return_type="non_void")
                    statements = node.children[0].statement()
                    ASTNode.blocks[curr_block].extend(statements)
                else:
                    ASTNode.blocks[curr_block] = Block(return_type="void")

                return []

    def generate_graph(self):

        end_list = ASTNode.node_generate_graph(self)

        last_blk_id = len(ASTNode.blocks.keys())
        for blk in end_list:
            ASTNode.blocks[blk].setGoto(last_blk_id)

        # ASTNode.blocks[last_blk_id] = [-1]

    def print_graph(self):

        flow = ASTNode.blocks
        # print()

        # print(flow)
        # print(ASTNode.functions)

        print()

        for block_id, block in sorted(flow.items(), key=lambda x: x[0]):

            if block_id in ASTNode.functions.keys():
                func_name = ASTNode.functions[block_id]
                args = [ (get_type_str(y), x) for x, y in list(self.symbol_table[func_name]["parameters"].items())]
                print("function %s(%s)" % (func_name, ", ".join([x + " " + y for x, y in args])))

            list_stat = block.list_stat
            print("<bb %d>" % block_id)
            if block.control_type:

                for stat in list_stat[:-1]:
                    print((stat))
                print("%s goto %s" % (list_stat[-1], get_block_str(block.goto1)))
                print("else goto %s" % (get_block_str(block.goto2)))

            elif block.return_type != "false":
                for statement in list_stat[:-1]:
                    print(statement)

                if block.return_type == "void":
                    print("return")
                else:
                    print("return " + list_stat[-1].__str__())

            else:
                for statement in list_stat:
                    print(statement)

                next_block_num = get_block_str(block.goto1)
                if next_block_num != "End":
                    print("goto %s" % (next_block_num))
                else:
                    print(next_block_num)

            print()

            
def get_block_str(block_id):
    if block_id != -1:
        ret_str = "<bb %s>" % str(block_id)
    else:
        ret_str = "End"
    return ret_str

def get_type_str(type_attr, rev=False):
    if not rev:
        return type_attr["base_type"] + "*"*type_attr["level"]
    else:
        return "*"*type_attr["level"] + type_attr["base_type"]

