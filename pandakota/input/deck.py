"""
Deck

Class for DAKOTA input decks
"""

import typing
import collections
import pandakota.input.variables as v


class Deck:
	"""DAKOTA Input deck builder
	
	The duck-typed deck that quacks like a dict
	
	"""
	def __init__(self):
		self._all_variable_keys: typing.Set[str] = set()
		# self._state_variables: typing.Dict[str, v.StateVariable] = dict()
		# self._normal_uncertain_variables: typing.Dict[str, v.NormalUncertainVariable] = dict()
		# self._uniform_uncertain_variables: typing.Dict[str, v.UniformUncertainVariable] = dict()
		self._typed_variables = {_t: typing.Dict[str, _t] for _t in v.TYPED_VARIABLES}
		self._chained_variables = collections.ChainMap(*self._typed_variables.values())
	
	def __iter__(self):
		return iter(self._all_variable_keys)
	
	def __getitem__(self, item):
		return self._chained_variables[item]
	
	def get(self, item, default=None):
		return self._chained_variables.get(item, default)
	
	def items(self):
		return {k: self[k] for k in self}.items()
	
	@property
	def state_variables(self):
		return self._typed_variables[v.StateVariable]
	
	@property
	def normal_uncertain_variables(self):
		return self._typed_variables[v.NormalUncertainVariable]
	
	@property
	def uniform_uncertain_variables(self):
		return self._typed_variables[v.UniformUncertainVariable]
	
	def _validate_descriptor(self, descriptor: str):
		"""Make sure the variable name is unique, and add it to the registry"""
		assert isinstance(descriptor, str)
		forbidden_chars = [c for c in (' ', '"', "'", ',') if c in descriptor]
		assert not any(forbidden_chars), \
			f"The descriptor must not contain the characters: {descriptor}"
		assert descriptor not in self._all_variable_keys, \
			f"A variable with the name {descriptor} already exists."
		self._all_variable_keys.add(descriptor)
	
	
	def add_variable(self, var: v.Variable):
		self._validate_descriptor(var.key)
		self._typed_variables[type(var)][var.key] = var
	
	def add_normal_uncertain_variable(
			self, descriptor: str, mean: float, std_deviation: float
	):
		"""Add a 'normal_uncertain' variable to the DAKOTA input.

		Parameters:
		-----------
		descriptor: str
			Unique name of the variable.
			
		mean: float
			Mean value of its uncertainty distribution
		
		std_deviation: float
			Standard deviation of its uncertainty distribution
		"""
		ncv = v.NormalUncertainVariable(descriptor, mean, std_deviation)
		self.add_variable(ncv)
	
	def add_uniform_uncertain_variable(
			self, descriptor: str, lower_bound: float, upper_bound: float
	):
		"""Add a 'uniform_uncertain' variable to the DAKOTA input.

		Parameters:
		-----------
		descriptor: str
			Unique name of the variable.
			
		lower_bound: float
			Lower bound of its uncertainty distribution.
		
		upper_bound: float
			Upper bound of its uncertainty distribution.
		"""
		ucv = v.UniformUncertainVariable(descriptor, lower_bound, upper_bound)
		self.add_variable(ucv)
		
	def _format_variable_type(self, VariableClass: typing.Type[v.Variable]) -> str:
		# This won't work for state variables...
		these_variables = self._typed_variables[VariableClass]
		proplines = {}
		for var in these_variables.values():
			for prop, val in var.justify().items():
				propline = proplines.get(prop, prop.ljust(16))
				proplines[prop] = propline + val
		header = f"\n\t{VariableClass.block_name}  {len(these_variables)}"
		sep = "\n\t\t"
		block = header + sep + sep.join(proplines.values()) + "\n"
		return block