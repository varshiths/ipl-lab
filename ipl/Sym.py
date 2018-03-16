import pprint

class Sym:
	def __init__(self):
		self.table = {}
		self.add_procedure('global')

	def add_entry(self, entry_attr, procedure_name):
		entry_name = entry_attr["name"]
		entry_attr.pop("name")

		if procedure_name not in self.table.keys():
			raise Exception("Procedure_name does not exist")
		if entry_name in self.table[procedure_name]['symbol_table'].keys():
			raise Exception("Redeclaration of variable")

		self.table[procedure_name]['symbol_table'][entry_name] = entry_attr

	def add_procedure(self, procedure_name, ret_type=None, list_of_parameters=list()):
		if procedure_name in self.table.keys():
			raise Exception("Redeclaration of procedure")

		self.table[procedure_name] = {
			'return_type': ret_type, 
			'symbol_table':{}, 
			'parameters':list_of_parameters
		}

	def print_symbol_table(self):

		pp = pprint.PrettyPrinter(indent=4)

		pp.pprint(self.table)
		pass




		
		
