import pprint

class Sym:
    def __init__(self):
        self.table = {}

    def __getitem__(self, item):
        return self.table[item].copy()

    def keys(self):
        return self.table.keys()

    def get_entry(self, entry_name, scope):

        ntype = None
        exists = True

        if scope != "global":
            if entry_name in self.table[scope]["symbol_table"].keys():
                ntype = self.table[scope]["symbol_table"][entry_name]
            else:
                scope = "global"
        if scope == "global":
            if entry_name in self.table.keys():
                ntype = self.table[entry_name]
                ntype.pop("type")
            else:
                exists = False

        return ntype.copy(), exists

    def add_entry(self, entry_attr, procedure_name):

        if procedure_name == "global":
            self._add_global_entry(entry_attr)
            return

        entry_name = entry_attr["name"]
        entry_attr.pop("name")

        if procedure_name not in self.table.keys():
            raise Exception("Procedure_name does not exist")
        if entry_name in self.table[procedure_name]['symbol_table'].keys():
            raise Exception("Redeclaration of variable")

        self.table[procedure_name]['symbol_table'][entry_name] = entry_attr

    def _add_global_entry(self, entry_attr):

        entry_name = entry_attr["name"]
        entry_attr.pop("name")

        if entry_name in self.table.keys():
            raise Exception("Redeclaration of global entity")

        self.table[entry_name] = entry_attr
        self.table[entry_name]["type"] = "variable"

    def add_procedure(self, procedure_name, ret_type=None, list_of_parameters=list(), prototype=False):
        if procedure_name in self.table.keys():
            if self.table[procedure_name]["prototype"] == False:
                raise Exception("Redeclaration of procedure")

        self.table[procedure_name] = {
            'type': "procedure", 
            'prototype': prototype, 
            'return_type': ret_type, 
            'symbol_table':{}, 
            'parameters':list_of_parameters
        }

    def print_table(self):

        pp = pprint.PrettyPrinter(indent=4)

        pp.pprint(self.table)
        pass