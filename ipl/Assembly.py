import pprint

class Assembly:

    def initialise(self, symbol_table, ast):
        self.symbol_table = symbol_table
        self.ast = ast

        self.code = []

    def add_stat(self, string):
        self.code.append(string)

    def size_table(self, func_name):
        return 0

    def gen_assembly_stat(self, statement):

        self.add_stat(statement)

        pass

    def gen_func_code(self, blockid):

        self.free_registers = list(range(8))
        func_name = self.ast.functions[blockid]

        locals_space = self.size_table(func_name)

        # generate prologue
        self.add_stat("%s:" % (func_name))

        self.add_stat("sw $ra, 0($sp)")
        self.add_stat("sw $fp, -4($sp)")
        self.add_stat("sub $fp, $sp, 8")
        self.add_stat("sub $sp, $sp, %d" % ( locals_space ))

        # generate code for each block
        block = self.ast.blocks[blockid]

        while block.return_type == "false":

            self.add_stat("label%d:" % (blockid))

            if block.control_type:

                # generate stat for temporaries
                list_stat = block.list_stat
                for stat in list_stat:
                    self.gen_assembly_stat(stat)

                self.add_stat("bne $%s, $0, label%d" % ( "temp", block.goto1 ))
                self.add_stat("j label%d" % ( block.goto2 ))

            else:

                # generate statements
                list_stat = block.list_stat
                for stat in list_stat:
                    self.gen_assembly_stat(stat)

                self.add_stat("j label%d" % (block.goto1))

            blockid += 1
            block = self.ast.blocks[blockid]

        self.add_stat("label%d:" % (blockid))
        self.add_stat("j epilogue_%s" % (func_name))

        # generate epilogue
        self.add_stat("epilogue_%s:" % (func_name))

        self.add_stat("add $sp, $sp, %d" % (locals_space))
        self.add_stat("lw $fp, -4($sp)")
        self.add_stat("sw $ra, 0($sp)")
        self.add_stat("jr $ra")

        self.free_registers = []

        pass

    def generate_code(self):

        # generate code for global data and set headers

        # process each function

        for blockid in self.ast.functions.keys():
            self.gen_func_code(blockid)


        pass

    def print_code(self):
        pp = pprint.PrettyPrinter(indent=4)

        print("Functions:")
        pp.pprint(self.ast.functions)
        
        print("\nBlocks:")
        pp.pprint(self.ast.blocks)

        print("\nTemporaries:")
        pp.pprint(self.ast.temporaries)

        print("\nCode:\n")
        for stat in self.code:
            string = str(stat)
            if string[-1] == ":":
                print(string)
            else:
                print("\t", string)