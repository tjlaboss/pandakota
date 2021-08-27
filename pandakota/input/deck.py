"""
Deck

Class for DAKOTA input decks
"""

import pandakota.input.variables as v

class Deck:
	"""DAKOTA Input deck builder
	
	"""
	def __init__(self):
		self._all_variables = set()
	
	def __iter__(self):
		return iter(self._all_variables)
	
	def __getitem__(self, item):
		if item not in self._all_variables:
			raise KeyError(item)
		# TODO: get the appropriate variable
		raise NotImplementedError(f"Deck[{item}]")
	
	def items(self):
		return {k: self[k] for k in self}.items()

