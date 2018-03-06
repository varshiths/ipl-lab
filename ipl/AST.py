binary_ops = {'PLUS':'+', 'MINUS':'-', 'UMINUS':'-', 'MUL':'*', 'DIV':'/', 'LESS':'<', 'GRT':'>', 'LESS_EQ':'<=', 'GRT_EQ':'>=', 'EQ':'==', 'NEQ':'!=', 'AND':'&&',
	        'OR':'||', 'B_AND':'&', 'B_OR':'|', 'NOT':'!'}

def tabs(n):
    return "\t"*n

class ASTNode:

    blocks = {}
    def __init__(self, label, children):
        self.label = label
        self.children = children

    def print_tree(self, ntabs=0):
        if self.label == "VAR" or self.label == "CONST":
            print(tabs(ntabs), end='')            
            print(self.label, "(", self.children[0].label, ")", sep='')
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
    		return self.children[0].label
    	elif self.label == "DEREF":
    		return "*" + self.children[0].statement()
    	elif self.label == "ADDR":
    		return "&" + self.children[0].statement()
    	elif self.label == "ASGN":
    		return (self.children[0]).statement() + "=" + (self.children[1]).statement()
    	elif self.label in binary_ops.keys():
    		return (self.children[0]).statement() + binary_ops[self.label] + (self.children[1]).statement()

	def control_flow_graph_node(self, node):
		if node is not None:
			if node.label == "BLOCK":
				if len(node.children) == 0:
					return
				else:
					curr_block = len(blocks.keys())
					blocks[curr_block] = []
					for i, child in enumerate(node.children):
						if child is not None:
							if child.label != "IF" and child.label != "WHILE":
								blocks[curr_block].append(child.statement())
								if i == len(node.children)-1:
									return [curr_block]
							else:
								if len(blocks[curr_block]) == 0:
									del blocks[curr_block]
								else:
									blocks[curr_block].append(curr_block+1)

								block_list = control_flow_graph(child)

								if i == len(node.children)-1:
									return block_list
								else:
									next_block = len(blocks.keys())
									for blk in block_list:
										blocks[blk].append(next_block)

							curr_block = len(blocks.keys())
							blocks[curr_block] = []

			elif node.label == "IF":
				curr_block = len(blocks.keys())
				blocks[curr_block] = []

				cond = node.children[0].statement()
				true_blk = curr_block + 1
				a = control_flow_graph(node.children[1])
				false_blk = len(blocks.keys())
				b = control_flow_graph(node.children[2])

				blocks[curr_block] = ["if(" + cond + ")"]
				blocks[curr_block].append(true_blk)
				blocks[curr_block].append(false_blk)

				a.extend(b)
				return a

			elif node.label == "WHILE":
				curr_block = len(blocks.keys())
				blocks[curr_block] = []
				cond = node.children[0].statement()
				true_blk = curr_block + 1
				control_flow_graph(node.children[1])
				blocks[true_blk].append(curr_block)

				blocks[curr_block] = ["if(" + cond + ")"]
				blocks[curr_block].append(true_blk)
				
				return [curr_block]


    def get_control_graph(self):

    	end_list = self.control_flow_graph_node()

    	for blk in end_list:
    		blocks[blk].append("End")

    	print(blocks)