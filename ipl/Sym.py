import pprint
from collections import OrderedDict

class Sym:
    def __init__(self):
        self.table = {}
        self.prototype_params = {}

    def __getitem__(self, item):
        return self.table[item].copy()

    def keys(self):
        return self.table.keys()

    def get_entry(self, entry_name, scope):

        ntype = None
        exists = True

        if scope != "global":
            if entry_name in self.table[scope]["symbol_table"].keys():
                ntype = self.table[scope]["symbol_table"][entry_name].copy()

            elif entry_name in self.table[scope]["parameters"].keys():
                ntype = self.table[scope]["parameters"][entry_name].copy()

            else:
                scope = "global"
                
        if scope == "global":
            if entry_name in self.table.keys():
                ntype = self.table[entry_name].copy()
                ntype.pop("type")
            else:
                exists = False

        return ntype, exists

    def add_entry(self, entry_attr, procedure_name):

        if procedure_name == "global":
            self._add_global_entry(entry_attr)
            return

        entry_name = entry_attr["name"]
        entry_attr.pop("name")

        if procedure_name not in self.table.keys():
            raise Exception("Procedure_name does not exist")
        if entry_name == procedure_name:
            raise Exception("Reuse of function name")
        if entry_name in self.table[procedure_name]['symbol_table'].keys():
            raise Exception("Redeclaration of variable")
        if entry_attr["base_type"] == "void" and entry_attr["level"] == 0:
            raise Exception("Declaration of variable as void")

        self.table[procedure_name]['symbol_table'][entry_name] = entry_attr

    def _add_global_entry(self, entry_attr):

        entry_name = entry_attr["name"]
        entry_attr.pop("name")

        if entry_name in self.table.keys():
            raise Exception("Redeclaration of global entity")
        if entry_attr["base_type"] == "void" and entry_attr["level"] == 0:
            raise Exception("Declaration of variable as void")

        self.table[entry_name] = entry_attr
        self.table[entry_name]["type"] = "variable"

    def add_procedure(self, procedure_name, ret_type=None, list_of_parameters=list(), prototype=False):
        dict_parameters = OrderedDict()

        for param in list_of_parameters:
            param_name = param["name"]
            
            if param_name in dict_parameters.keys():
                raise Exception("Duplicate parameter name")                
            else:
                param_dict = {
                    "base_type" : param["base_type"],
                    "level" : param["level"]
                }
                dict_parameters[param_name] = param_dict

        if procedure_name in self.table.keys():

            dict_parameters_old = self.table[procedure_name]["parameters"].copy()
            self.prototype_params[procedure_name] = dict_parameters_old


            if  self.table[procedure_name]["prototype"] == True and \
                list(dict_parameters.values()) == list(dict_parameters_old.values()) and \
                self.table[procedure_name]["return_type"] == ret_type and \
                not prototype:
                pass
            else:
                raise Exception("Redeclaration of procedure")

        self.table[procedure_name] = {
            'type': "procedure", 
            'prototype': prototype, 
            'return_type': ret_type, 
            'symbol_table': {}, 
            'parameters': dict_parameters
        }

    def update_prototype_nature(self, procedure_name, prototype):
        self.table[procedure_name]["prototype"] = prototype

    def print_table(self):

        pp = pprint.PrettyPrinter(indent=4)

        #pp.pprint(self.table)
        self.print_table_formatted()
        pass

    def get_type_string(self, type_attr):
        return type_attr["base_type"] + "*"*type_attr["level"]

    def print_table_formatted(self):
        separator = "-----------------------------------------------------------------"
        print("Procedure table :-")
        print(separator)
        print("%s \t\t | %s \t\t | %s \t\t " % ("Name", "Return Type", "Parameter List"))
        print(separator)
        for key, val in sorted(self.table.items()):
            if key == "main":
                    continue
            if val["type"] == "procedure":
                if key in self.prototype_params:
                    parameter_types = OrderedDict((k, self.get_type_string(v)) for k, v in self.prototype_params[key].items())
                else:
                    parameter_types = OrderedDict((k, self.get_type_string(v)) for k, v in val["parameters"].items())

                param_str = ""
                ct = 0
                for name, type_str in parameter_types.items():
                    param_str += "%s %s" % (type_str, name)
                    if ct < len(parameter_types)-1:
                        param_str += ", "
                    ct += 1

                print("%s \t\t | %s \t\t | %s \t\t " % (key, self.get_type_string(val["return_type"]), param_str))

        print(separator)
        print("Variable table :-")
        print(separator)
        print("%s \t\t | %s \t\t | %s \t\t | %s \t\t" %("Name", "Scope", "Base Type", "Derived Type"))
        print(separator)

        for key, val in sorted(self.table.items()):
            if val["type"] == "variable":
                print("%s \t\t | %s \t\t | %s \t\t | %s \t\t " % (key, "global", val["base_type"], "*"*val["level"]))
            else:
                local_vars = list(val["symbol_table"].items())
                local_vars.extend(list(val["parameters"].items()))
                for key1, val1 in sorted(local_vars):
                    print("%s \t\t | %s \t\t | %s \t\t | %s \t\t " % (key1, "procedure " + key, val1["base_type"], "*"*val1["level"]))

        '''
        # sorted by variable name:
        all_variables = []
        for key, val in sorted(self.table.items()):
            #print("val", val)
            if val["type"] == "variable":
                val["scope"] = "global"
                all_variables.append((key, val))
            else:
                local_vars = list(val["symbol_table"].items())
                local_vars.extend(list(val["parameters"].items()))
                for l, v in local_vars:
                    v["scope"] = key
                all_variables.extend(local_vars)

        for var_name, attr in sorted(all_variables, key=lambda x: x[0]):
            print("%s \t\t | %s \t\t | %s \t\t | %s \t\t " % (var_name, "procedure " + attr["scope"], attr["base_type"], "*"*attr["level"]))'''

        print(separator)






