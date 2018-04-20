import pprint
from heapq import heappush, heappop, heapify

dot_text_string = "The .text assembler directive indicates"
global_func_string = "The following is the code"

save_ra_string = "Save the return address"
save_fp_string = "Save the frame pointer"
update_fp_string = "Update the frame pointer"
space_locals_string = "Make space for the locals"

return_string = "Jump back to the called procedure"

func_actv_record_c_string = "setting up activation record for called function"
func_call_string = "function call"
func_actv_record_d_string = "destroying activation record of called function"
func_call_ret_val_string = "using the return value of called function"

return_addr_fp_space = 8

class Assembly:

    def initialise(self, symbol_table, ast):
        self.symbol_table = symbol_table
        self.ast = ast
        self.ops_map = {'PLUS': 'add', 'MINUS':'sub', 'MUL':'mul', 'DIV':'div', 'UMINUS':'negu'}
        self.logical_ops = {'LT':'<', 'GT':'>', 'LE':'<=', 'GE':'>=', 'EQ':'==', 'NE':'!=', 'AND':'&&', 'OR':'||'}
        self.code = []
        self.curr_temp = None
        self.return_block = False
        self.local_symbol_table = None
        self.cond_label = 0

    def add_stat(self, string, comment=None, indent=True):
        string = str(string)
        if string == "":
            indent = False
        if indent:
            string = "\t" + string
        if comment is not None:
            string += "\t# %s" % comment
        self.code.append(string)

    def add_raw_string(self, string):
        self.add_stat(string, None, False)

    def build_access_table(self, func_name):
        parameters = self.symbol_table.table[func_name]["parameters"]
        symbol_table = self.symbol_table.table[func_name]["symbol_table"]
        self.local_symbol_table = symbol_table

        offsets_dict = {}
        offset_so_far = 0
        
        for name, attr in sorted(symbol_table.items()):
            size = self.get_type_size(attr)
            offsets_dict[name] = offset_so_far + size
            offset_so_far += size

        offset_so_far += return_addr_fp_space

        for name, attr in parameters.items():
            size = self.get_type_size(attr)
            offsets_dict[name] = offset_so_far + size
            offset_so_far += size

        self.offsets = offsets_dict

    def size_table_params(self, func_name):
        param_size = sum( [ self.get_type_size(type_dict) for name, type_dict in self.symbol_table.table[func_name]["parameters"].items() ] )
        return param_size

    def size_table_locals(self, func_name):
        locals_size = sum( [ self.get_type_size(type_dict) for name, type_dict in self.symbol_table.table[func_name]["symbol_table"].items() ] )
        return locals_size

    def extract_var_name(self, string):

        deref_char = "*"
        ref_char = "&"

        pos1 = string.rfind(deref_char)
        pos2 = string.rfind(ref_char)

        index = max(pos1, pos2)        
        var_name = string[index+1:]

        return var_name

    def get_free_register(self, float_var):
        # return free register
        # remove from free list
        if not float_var:
            try:
                reg = heappop(self.free_registers)
            except IndexError:
                print("No free registers")
        else:
            try:
                reg = heappop(self.free_float_registers)
            except IndexError:
                print("No free registers")

        return reg

    def set_register_free(self, register):
        if register[0] != 'f':
            heappush(self.free_registers, register)
        else:
            heappush(self.free_float_registers, register)

        print("setting reg free ",register)
        #print(self.free_registers)

    def set_reg_list_free(self, reg_list):
        for reg in reg_list:
            self.set_register_free(reg)


    def get_offset(self, var_name):
        try:
            offset = self.offsets[var_name]
            return (True, offset)
        except KeyError:
            # global
            return (False, "global_" + var_name)

    def check_float(self, var_name):
        data_type = None
        try:
            data_type = self.local_symbol_table[var_name]    
            print("local type", data_type)     
        except KeyError:
            # global variable
            try:
                data_type = self.symbol_table[var_name]
            except KeyError:
                # temporary
                return False

        if data_type["base_type"] == "float":
            return True
        else:
            return False

    def gen_code_var(self, stat, lhs=False): # handle DEREF, ADDR and VAR statement types
        print("gen_code_var")
        print(stat)
        float_var = False

        if stat.stat_type == "CONST":
            val = stat.tokens[0]
            if val.find('.') != -1:
                float_var = True
            print(stat, float_var, type(val))

            reg = self.get_free_register(float_var)
            if not float_var:       
                self.add_stat("li $%s, %s" % (reg, val))
            else:
                self.add_stat("li.s $%s, %s" % (reg, val))

            return reg
        else:
            var_name = self.extract_var_name(stat.tokens[0])
            float_var = self.check_float(var_name)
            print("float_var ", var_name, float_var)
            lw_instrn = "lw"
            if float_var:
                lw_instrn = "l.s"

            local, offset = self.get_offset(var_name)
            #offset = self.offsets[var_name]
            if stat.stat_type == "VAR":
                print("var")
                reg = self.get_free_register(float_var)
                
                if local:    
                    self.add_stat("%s $%s, %s($sp)" % (lw_instrn, reg, offset))
                else:
                    self.add_stat("%s $%s, %s" % (lw_instrn, reg, offset))

                return reg
            else:
                deref_ct = stat.tokens[0].count("*")
                addr_ct = stat.tokens[0].count("&")
                net_deref = deref_ct - addr_ct
                if net_deref == 0: # VAR
                    reg = self.get_free_register(float_var)    
                    if local:    
                        self.add_stat("%s $%s, %s($sp)" % (lw_instrn, reg, offset))
                    else:
                        self.add_stat("%s $%s, %s" % (lw_instrn, reg, offset))

                    return reg
                elif net_deref > 0: # DEREF
                    deref_ct = net_deref
                    reg = self.get_free_register(False)
                    if local:
                        self.add_stat("lw $%s, %s($sp)" % (reg, offset))
                    else:
                        self.add_stat("lw $%s, %s" % (reg, offset))

                    reg_prev = reg
                    reg_curr = reg
                    dest_reg = None
                    if lhs:
                        derefs = deref_ct-1
                    else:
                        derefs = deref_ct

                    for i in range(derefs):
                        print("derefs lhs float_var", i, lhs, float_var)
                        float_reg = False
                        load_instrn = "lw"

                        if (not lhs) and (i == derefs-1) and float_var:
                            float_reg = True
                            load_instrn = "l.s"

                        reg_curr = self.get_free_register(float_reg)
                        self.add_stat("%s $%s, 0($%s)" % (load_instrn, reg_curr, reg_prev))
                        # mark reg_prev free
                        self.set_register_free(reg_prev)
                        reg_prev = reg_curr

                    return reg_curr

                else: # ADDR
                    print("addr")
                    print(stat)                  
                    reg = self.get_free_register(False)
                    if local:
                        self.add_stat("addi $%s, $sp, %s" % (reg, offset))
                    else:
                        self.add_stat("la $%s, %s" % (reg, offset))

                    return reg

        
    def gen_assembly_stat(self, statement):

        #self.add_stat(statement)
        print(statement.stat_type, statement.tokens)
        stat_type = statement.stat_type
        tokens = statement.tokens

        print("statement type", statement.stat_type)

        if statement.stat_type in set(["VAR", "CONST", "DEREF", "ADDR"]):
            reg = self.gen_code_var(statement)
            return reg

        elif statement.stat_type in self.ops_map: # TODO
            el1 = statement.tokens[-3]
            el2 = statement.tokens[-1]
            if el1.stat_type != "place":
                el1_reg = self.gen_code_var(el1)
            else:
                el1_reg = self.curr_temp

            if el2.stat_type != "place":
                el2_reg = self.gen_code_var(el2)
            else:
                el2_reg = self.curr_temp

            float_op = False
            if el1_reg[0] == 'f' or el2_reg[0] == 'f':
                float_op = True
         
            instrn = self.ops_map[statement.stat_type]
            if float_op:
                instrn = instrn + ".s"

            res_reg = self.get_free_register(float_op)
            self.add_stat("%s $%s, $%s, $%s" % (instrn, res_reg, el1_reg, el2_reg))
            self.set_reg_list_free([el1_reg, el2_reg])
        
            dest_reg = self.get_free_register(float_op)
            self.curr_temp = dest_reg
            if not float_op:
                self.add_stat("move $%s, $%s" % (dest_reg, res_reg))
            else:
                self.add_stat("mov.s $%s, $%s" % (dest_reg, res_reg))

            self.set_register_free(res_reg)
            print(self.free_registers)
            return dest_reg

        elif statement.stat_type in self.logical_ops:
            el1 = statement.tokens[-3]
            el2 = statement.tokens[-1]
            if el1.stat_type != "place":
                el1_reg = self.gen_code_var(el1)
            else:
                el1_reg = self.curr_temp

            if el2.stat_type != "place":
                el2_reg = self.gen_code_var(el2)
            else:
                el2_reg = self.curr_temp

            float_op = False
            if el1_reg[0] == 'f' or el2_reg[0] == 'f':
                float_op = True

            if not float_op:
                cond_reg = self.get_free_register()

                if statement.stat_type == "EQ":
                    self.add_stat("seq $%s, $%s, $%s" % (cond_reg, el1_reg, el2_reg))
                    self.set_reg_list_free([el1_reg, el2_reg])
                elif statement.stat_type == "NE":
                    self.add_stat("sne $%s, $%s, $%s" % (cond_reg, el1_reg, el2_reg))
                    self.set_reg_list_free([el1_reg, el2_reg])
                else: # LT, GT, LE, GE
                    if statement.stat_type == "GT" or statement.stat_type == "LE":
                        temp = el2_reg
                        el2_reg = el1_reg
                        el1_reg = temp
        
                    self.add_stat("slt $%s, $%s, $%s" % (cond_reg, el1_reg, el2_reg))
                    self.set_reg_list_free([el1_reg, el2_reg])
                    if statement.stat_type == "LE" or statement.stat_type == "GE":
                        neg_reg = self.get_free_register()
                        self.add_stat("not $%s, $%s" % (neg_reg, cond_reg))
                        self.set_register_free(cond_reg)
                        cond_reg = neg_reg

                dest_reg = self.get_free_register()
                self.curr_temp = dest_reg
                self.add_stat("move $%s, $%s" % (dest_reg, cond_reg))
                self.set_register_free(cond_reg)
            else: 
                # floating point comparison
                if statement.stat_type != "NE":
                    cmp_instrn = "c.lt.s"
                    if statement.stat_type == "EQ":
                        cmp_instrn = "c.eq.s"
                    elif statement.stat_type == "LE":
                        cmp_instrn = "c.le.s"
                    elif statement.stat_type == "GT":
                        temp = el2_reg
                        el2_reg = el1_reg
                        el1_reg = temp
                    elif statement.stat_type == "GE":
                        cmp_instrn = "c.le.s"
                        temp = el2_reg
                        el2_reg = el1_reg
                        el1_reg = temp

                    self.add_stat("%s $%s, $%s" % (cmp_instrn, el1_reg, el2_reg))
                    self.set_reg_list_free([el1_reg, el2_reg])
                    self.add_stat("bc1f L_CondFalse_%d" % (self.cond_label))
                    reg = self.get_free_register(False)
                    self.add_stat("li $%s, 1" % (reg))
                    self.add_stat("j L_CondEnd_%d" % (self.cond_label))
                    self.add_raw_string("L_CondFalse_%d:" % (self.cond_label))
                    self.add_stat("li $%s, 0" % (reg))
                    self.add_raw_string("L_CondEnd_%d:" % (self.cond_label))
                    dest_reg = self.get_free_register(False)
                    self.curr_temp = dest_reg
                    self.add_stat("move $%s, $%s" % (dest_reg, reg))
                    self.set_register_free(reg)

                    self.cond_label += 1

                else:
                    cmp_instrn = "c.eq.s"
                    self.add_stat("%s $%s, $%s" % (cmp_instrn, el1_reg, el2_reg))
                    self.set_reg_list_free([el1_reg, el2_reg])
                    self.add_stat("bc1f L_CondTrue_%d" % (self.cond_label))
                    reg = self.get_free_register(False)
                    self.add_stat("li $%s, 0" % (reg))
                    self.add_stat("j L_CondEnd_%d" % (self.cond_label))
                    self.add_raw_string("L_CondTrue_%d:" % (self.cond_label))
                    self.add_stat("li $%s, 1" % (reg))
                    self.add_raw_string("L_CondEnd_%d:" % (self.cond_label))
                    dest_reg = self.get_free_register(False)
                    self.curr_temp = dest_reg
                    self.add_stat("move $%s, $%s" % (dest_reg, reg))
                    self.set_register_free(reg)

                    self.cond_label += 1

            
        elif statement.stat_type == "ASGN":
            # RHS
            rh_var = tokens[-1]
            print(rh_var)
            print("rh_var.type ", rh_var.stat_type)
            if rh_var.stat_type == "place":
                r_reg = self.curr_temp
            else:
                r_reg = self.gen_code_var(rh_var)
                    
            # if rh_var.stat_type == "CONST":
            #     val = rh_var.tokens[0]
            #     r_reg = self.get_free_register()
            #     instrn = "li $%s, %s" % (r_reg, val)
            #     print(instrn)
            #     self.add_stat(instrn)
            # elif rh_var.stat_type == "VAR":
            #     r_reg = self.get_free_register()
            #     offset = self.offsets[rh_var.tokens[0]]
            #     self.add_stat("lw $%s, %s($sp)" % (r_reg, offset))
            # elif rh_var.stat_type == "ADDR":
                
            # elif rh_var.stat_type == "DEREF":
            #     r_reg = self.gen_deref(rh_var)

            # LHS
            lh_var = tokens[0]
            print(lh_var)
            print(lh_var.stat_type)
            print(lh_var.tokens)
            deref_ct = lh_var.tokens[0].count("*")
            print(deref_ct)
            sw_instrn = "sw"
            if r_reg[0] == 'f':
                sw_instrn = "s.s"

            if deref_ct == 0:
                local, l_offset = self.get_offset(lh_var.tokens[0])
                if local:
                    self.add_stat("%s $%s, %s($sp)" % (sw_instrn, r_reg, l_offset))
                else:
                    self.add_stat("%s $%s, %s" % (sw_instrn, r_reg, l_offset))

                self.set_register_free(r_reg)
            else:
                l_curr = self.gen_code_var(lh_var, True)
                if r_reg[0] != 'f':
                    self.add_stat("sw $%s, 0($%s)" % (r_reg, l_curr))
                else:
                    self.add_stat("s.s $%s, 0($%s)" % (r_reg, l_curr))

                # free registers
                self.set_reg_list_free([r_reg, l_curr])
            
            print(self.free_registers)

        elif statement.stat_type in [ "func_ret", "func_no_ret" ]:

            print("FCALLS", statement)

            func_name_index = 0
            if statement.stat_type == "func_ret":
                func_name_index = 2
            func_name = statement.tokens[func_name_index]
            param_size = self.size_table_params(func_name)
            func_ret_type = self.symbol_table[func_name]["return_type"]
            print(func_ret_type)

            self.add_stat("", comment=func_actv_record_c_string, indent=False)

            # set up arguments
            parameters = self.symbol_table[func_name]["parameters"]
            offset = - self.size_table_params(func_name)
            for i, (name, attr) in enumerate(parameters.items()):
                size = self.get_type_size(attr)
                offset += size

                reg = self.gen_code_var(statement.tokens[func_name_index + 1 + i])
                self.add_stat("sw $%s, %d($sp)" % (reg, offset))
                self.set_register_free(reg)

            self.add_stat("sub $sp, $sp, %d" % param_size)
            self.add_stat("jal %s" % func_name, func_call_string)
            self.add_stat("add $sp, $sp, %d" % param_size, func_actv_record_d_string)

            if statement.stat_type == "func_ret":
                if func_ret_type["base_type"] == "float" and func_ret_type["level"] == 0:
                    reg = self.get_free_register(True)
                    self.add_stat("move $%s, $f0" % reg, func_call_ret_val_string)
                    self.curr_temp = reg
                else:
                    reg = self.get_free_register(False)
                    self.add_stat("move $%s, $v1" % reg, func_call_ret_val_string)
                    self.curr_temp = reg

        pass

    def gen_func_prologue_code(self, func_name, locals_space):

        self.add_raw_string("# Prologue begins")
        self.add_stat("sw $ra, 0($sp)", save_ra_string)
        self.add_stat("sw $fp, -4($sp)", save_fp_string)
        self.add_stat("sub $fp, $sp, 8", update_fp_string)
        self.add_stat("sub $sp, $sp, %d" % ( 8 + locals_space ), space_locals_string)
        self.add_raw_string("# Prologue ends")

    def gen_func_code(self, blockid):

        self.free_registers = \
                ["s%d" % (x) for x in range(8)] + \
                ["t%d" % (x) for x in range(10)]

        self.free_float_registers = ["f%d" % (x) for x in range(10, 31, 2)]
                
        #self.free_registers.reverse()
        heapify(self.free_registers)
        heapify(self.free_float_registers)

        func_name = self.ast.functions[blockid]
        locals_space = self.size_table_locals(func_name)
        self.build_access_table(func_name)

        # directives
        self.add_stat(".text", dot_text_string)
        self.add_stat(".globl %s" % func_name, global_func_string)

        self.add_raw_string("%s:" % (func_name))

        # generate prologue
        self.gen_func_prologue_code(func_name, locals_space)

        # generate code for each block
        block = self.ast.blocks[blockid]

        while block.return_type == "false":

            self.add_raw_string("label%d:" % (blockid))

            if block.control_type:
                print("control blk")
                # generate stat for temporaries
                list_stat = block.list_stat
                for stat in list_stat[:-1]:
                    self.gen_assembly_stat(stat)

                self.add_stat("bne $%s, $0, label%d" % ( self.curr_temp, block.goto1 ))
                print("curr temp", self.curr_temp)
                self.set_register_free(self.curr_temp)
                self.add_stat("j label%d" % ( block.goto2 ))

            else:
                print("non-control blk")
                # generate statements
                list_stat = block.list_stat
                for stat in list_stat:
                    self.gen_assembly_stat(stat)

                self.add_stat("j label%d" % (block.goto1))

            blockid += 1
            block = self.ast.blocks[blockid]


        print(block.return_type)
        if block.return_type != "false":
            self.return_block = True

        self.add_raw_string("label%d:" % (blockid))
        list_stat = block.list_stat
        ret_reg = None
        for stat in list_stat:
            print(stat)
            reg = self.gen_assembly_stat(stat)
            if reg is not None:
                ret_reg = reg
            else:
                ret_reg = self.curr_temp

        if ret_reg is not None:
            if ret_reg[0] != 'f':
                self.add_stat("move $v1, $%s" % (ret_reg), "move return value to $v1")
            else:
                self.add_stat("mov.s $f0, $%s" % (ret_reg), "move return value to $f0")

       

        self.return_block = False
        #self.add_raw_string("label%d:" % (blockid))
        self.add_stat("j epilogue_%s" % (func_name))

        # generate epilogue
        self.gen_func_epilogue_code(func_name, locals_space)

        self.free_registers = []

    def gen_func_epilogue_code(self, func_name, locals_space):

        self.add_stat("")
        self.add_raw_string("# Epilogue begins")
        self.add_stat("epilogue_%s:" % (func_name), None, False)

        self.add_stat("add $sp, $sp, %d" % (8 + locals_space))
        self.add_stat("lw $fp, -4($sp)")
        self.add_stat("lw $ra, 0($sp)")
        self.add_stat("jr $ra", return_string)
        self.add_raw_string("# Epilogue ends")

    def generate_code(self):

        # generate code for global data and set headers
        self.gen_global_var_code()

        # process each function

        for blockid in self.ast.functions.keys():
            self.gen_func_code(blockid)


        pass

    def get_type_size(self, type_dict):
        val = 4
        if type_dict["base_type"] == "float" and type_dict["level"] == 0:
            val = 8
        return val

    def get_directive_and_val(self, type_dict):
        size = self.get_type_size(type_dict)
        val = 0
        typ = "word"
        if size == 8:
            typ = "space"
            val = 8
        return "." + typ, val

    def gen_global_var_code(self):

        self.add_stat("")
        self.add_stat(".data")

        for name, data in self.symbol_table.table.items():
            if data["type"] == "procedure":
                continue
            typ, val = self.get_directive_and_val(data)
            self.add_raw_string("global_%s: \t%s\t%d" % (name, typ, val))

        self.add_stat("")

    def print_code(self):
        # pp = pprint.PrettyPrinter(indent=4)

        # print("Functions:")
        # pp.pprint(self.ast.functions)
        
        # print("\nBlocks:")
        # pp.pprint(self.ast.blocks)

        # print("\nTemporaries:")
        # pp.pprint(self.ast.temporaries)

        # print("\nSymbol Table:")
        # pp.pprint(self.symbol_table.table)

        # print("\nCode:")
        for stat in self.code:
            print(stat)
