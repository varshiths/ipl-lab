binary_ops = {'PLUS':'+', 'MINUS':'-', 'MUL':'*', 'DIV':'/', 'LT':'<', 'GT':'>', 'LE':'<=', 'GE':'>=', 'EQ':'==', 'NE':'!=', 'AND':'&&',
            'OR':'||', 'B_AND':'&', 'B_OR':'|'}

unary_ops = {'UMINUS':'-', 'NOT':'!'}
rev_unary_ops = {}
rev_binary_ops = {}
for key, val in binary_ops.items():
    rev_binary_ops[val] = key

for key, val in unary_ops.items():
    rev_unary_ops[val] = key

def tabs(n):
    return "\t"*n

class ASTNode:

    blocks = {}
    conditions = {}

    def __init__(self, label, children):
        self.label = label
        self.children = children

    def print_tree(self, ntabs=0):
        if self.label == "VAR" or self.label == "CONST":
            print(tabs(ntabs), end='')            
            print(self.label, "(", self.children[0].label, ")", sep='')
        elif self.label == "BLOCK":
            for child in self.children:
                child.print_tree(ntabs)
        else:
            print(tabs(ntabs), self.label, sep='')
            print(tabs(ntabs), "(", sep='')
            if len(self.children) != 0:
                for i, child in enumerate(self.children):
                    if child is not None:
                        child.print_tree(ntabs + 1)
                    if i != len(self.children)-1:
                        print(tabs(ntabs+1), ",", sep='')
            print(tabs(ntabs), ")", sep='')

    def statement(self):
        if self.label == "VAR" or self.label == "CONST":
            return [self.children[0].label]
        elif self.label == "DEREF":
            return ["*" + self.children[0].statement()[0]]
        elif self.label == "ADDR":
            return ["&" + self.children[0].statement()[0]]
        elif self.label == "ASGN":

            a_list = self.children[0].statement()
            b_list = self.children[1].statement()

            ret_list = []
            ret_list.extend(a_list[:-1])
            ret_list.extend(b_list[:-1])
            ret_list.append("%s %s %s" % (a_list[-1], "=", b_list[-1]))

            return ret_list

        elif self.label in binary_ops.keys():

            a_list = self.children[0].statement()
            b_list = self.children[1].statement()

            curr_cond = len(ASTNode.conditions.keys())
            ASTNode.conditions[curr_cond] = "t%d %s %s %s %s" % (curr_cond, "=", a_list[-1], binary_ops[self.label], b_list[-1])

            ret_list = []
            ret_list.extend(a_list[:-1])
            ret_list.extend(b_list[:-1])
            ret_list.append(ASTNode.conditions[curr_cond])

            ret_list.append("t%d" % curr_cond)

            return ret_list

        elif self.label in unary_ops.keys():
            
            a_list = self.children[0].statement()

            curr_cond = len(ASTNode.conditions.keys())
            ASTNode.conditions[curr_cond] = "t%d %s %s %s" % (curr_cond, "=", unary_ops[self.label], a_list[-1])

            ret_list = []
            ret_list.extend(a_list[:-1])
            ret_list.append(ASTNode.conditions[curr_cond])

            ret_list.append("t%d" % curr_cond)

            return ret_list



    def control_flow_graph_node(node):

        if node is not None:
            if node.label == "BLOCK":
                if len(node.children) == 0:
                    return []
                else:
                    curr_block = len(ASTNode.blocks.keys())
                    ASTNode.blocks[curr_block] = []
                    for i, child in enumerate(node.children):
                        if child is not None:
                            if child.label != "IF" and child.label != "WHILE":
                                ASTNode.blocks[curr_block].extend(child.statement())
                                if i == len(node.children)-1:
                                    return [curr_block]
                            else:
                                if len(ASTNode.blocks[curr_block]) == 0:
                                    del ASTNode.blocks[curr_block]
                                else:
                                    ASTNode.blocks[curr_block].append(curr_block+1)

                                block_list = ASTNode.control_flow_graph_node(child)

                                if i == len(node.children)-1:
                                    return block_list
                                else:
                                    next_block = len(ASTNode.blocks.keys())
                                    for blk in block_list:
                                        ASTNode.blocks[blk].append(next_block)

                                curr_block = len(ASTNode.blocks.keys())
                                ASTNode.blocks[curr_block] = []

            elif node.label == "IF":
                curr_block = len(ASTNode.blocks.keys())
                ASTNode.blocks[curr_block] = []

                cond_list = node.children[0].statement()
                true_blk = curr_block + 1
                a = ASTNode.control_flow_graph_node(node.children[1])
                false_blk = len(ASTNode.blocks.keys())
                b = ASTNode.control_flow_graph_node(node.children[2])

                ASTNode.blocks[curr_block] = ["if"]
                ASTNode.blocks[curr_block].extend(cond_list[:-1])
                ASTNode.blocks[curr_block].append("if(%s)" % (cond_list[-1]))

                end_list = []
                if len(a) == 0:
                    end_list.append(curr_block)
                else:
                    ASTNode.blocks[curr_block].append(true_blk)
                    end_list.extend(a)

                if len(b) == 0:
                    end_list.append(curr_block)
                else:
                    ASTNode.blocks[curr_block].append(false_blk)
                    end_list.extend(b)

                return end_list

            elif node.label == "WHILE":
                curr_block = len(ASTNode.blocks.keys())
                ASTNode.blocks[curr_block] = []

                cond_list = node.children[0].statement()
                true_blk = curr_block + 1
                a = ASTNode.control_flow_graph_node(node.children[1])

                ASTNode.blocks[curr_block] = ["if"]
                ASTNode.blocks[curr_block].extend(cond_list[:-1])
                ASTNode.blocks[curr_block].append("if(%s)" % (cond_list[-1]))

                if len(a) != 0:
                    ASTNode.blocks[curr_block].append(true_blk)
                    for blk in a:
                        ASTNode.blocks[blk].append(curr_block)
                else:
                    ASTNode.blocks[curr_block].append(curr_block)

                return [curr_block]


    def generate_flow_graph(self):
        ASTNode.blocks[0] = [None]

        end_list = ASTNode.control_flow_graph_node(self)

        last_blk_id = len(ASTNode.blocks.keys())
        for blk in end_list:
            ASTNode.blocks[blk].append(last_blk_id)

        ASTNode.blocks[last_blk_id] = [-1]

    def print_flow_graph(self):

        flow = ASTNode.blocks

        for key, value in sorted(flow.items(), key=lambda x: x[0])[1:]:
            print("<bb %d>" % key)
            if value[0] == "if":

                for stat in value[1:-3]:
                    print(stat)
                print("%s goto %s" % (value[-3], get_block_str(value[-2])))
                print("else goto %s" % (get_block_str(value[-1])))

            else:
                for statement in value[:-1]:
                    print(statement)
                next_block_num = get_block_str(value[-1])
                if next_block_num != "End":
                    print("goto %s" % (next_block_num))
                else:
                    print(next_block_num)

            print()
            
def get_block_str(block_id):
    if block_id != -1:
        ret_str = "<bb %d>" % block_id
    else:
        ret_str = "End"
    return ret_str