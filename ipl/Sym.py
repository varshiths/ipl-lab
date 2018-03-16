class Sym:
	def __init__(self):
		self.table = {}
		self.add_procedure('global', None)

	def add_entry(self, entry_name, entry_attr, procedure_name):
		if procedure_name not in table.keys():
			raise Exception("Procedure_name does not exist")
		if entry_name in self.table[procedure_name]['symbol_table'].keys():
			raise Exception("Redeclaration of variable")

		self.table[procedure_name]['symbol_table'][entry_name] = entry_attr

	def add_procedure(self, procedure_name, ret_type):
		if procedure_name in self.table.keys():
			raise Exception("Redeclaration of procedure")

		self.table[procedure_name] = {'return_type': ret_type, 'symbol_table':{}}




		
		
