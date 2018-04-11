import pprint

class Assembly:

    def initialise(self, symbol_table, ast):
        self.symbol_table = symbol_table
        self.ast = ast

    def generate_code(self):
        pass

    def print_code(self):
        pp = pprint.PrettyPrinter(indent=4)

        pp.pprint(self.ast.functions)
        pp.pprint(self.ast.blocks)
        pp.pprint(self.ast.temporaries)