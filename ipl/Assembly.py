import pprint

class Assembly:

    def initialise(self, symbol_table, ast):
        self.symbol_table = symbol_table
        self.ast = ast
        self.instructions_map = {'PLUS': 'add', 'MINUS':'sub', 'MUL':'mul', 'DIV':'div', 'UMINUS':'negu'}
        self.logical_ops = {'LT':'<', 'GT':'>', 'LE':'<=', 'GE':'>=', 'EQ':'seq', 'NE':'sne', 'AND':'&&', 'OR':'||'}
        self.code = []

    def add_stat(self, string):
        self.code.append(string)


    def size_table(self, func_name):
        return 0

    def get_free_register(self):
        # return free register
        # remove from free list
        if len(self.free_registers) > 0:
            reg = self.free_registers.pop()

        return reg

    def set_register_free(self, register):
        self.free_registers.append(register)

        

    def gen_assembly_stat(self, statement):

        #self.add_stat(statement)
        print(statement.stat_type, statement.tokens)
        stat_type = statement.stat_type
        tokens = statement.tokens
        if statement.stat_type == "ASGN":
            # RHS
            rh_var = tokens[-1]
            print(rh_var)
            if rh_var.stat_type == "CONST":
                r_reg = self.get_free_register()
                val = rh_var.tokens[0]
                instrn = "li $%s, %s" % (r_reg, val)
                print(instrn)
                self.code.append(instrn)
            # more cases

            # LHS
            lh_var = tokens[0]
            print(lh_var)
            print(lh_var.stat_type)
            print(lh_var.tokens)
            deref_ct = lh_var.tokens[0].count("*")
            print(deref_ct)

            offset = 4 # get from symbol table
            l1_reg = self.get_free_register()
            self.code.append("lw $%s, %s($sp)" % (l1_reg, offset))

            l_prev = l1_reg
            for i in range(deref_ct-1):
                l_curr = self.get_free_register()
                self.code.append("lw $%s, 0($%s)" % (l_curr, l_prev))
                # mark l1_prev free
                self.set_register_free(l_prev)
                l_prev = l_curr

            self.code.append("sw $%s, 0($%s)" % (r_reg, l_curr))
            if int(r_reg[-1]) > int(l_curr[-1]):
                self.set_register_free(r_reg)
                self.set_register_free(l_curr)
            else:
                self.set_register_free(l_curr)
                self.set_register_free(r_reg)

            print(self.free_registers)


        pass

    def gen_func_code(self, blockid):

        self.free_registers = ["t" + str(x) for x in list(range(9, -1, -1))]
        self.free_registers.extend(["s" + str(x) for x in list(range(7, -1, -1))])
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