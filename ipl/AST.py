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
