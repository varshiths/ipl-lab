import pprint

class Sym:
	def __init__(self):
		self.table = {}

	def __getitem__(self, item):
         return self.table[item]

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

		self.table[entry_name] = {
			'type': "variable", 
			'attr': entry_attr
		}

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




		
		
