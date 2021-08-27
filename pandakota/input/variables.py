"""
Variables

Module containing DAKOTA variable classes
"""
import abc
import typing

class Variable(abc.ABC):
	"""Abstract Base Class for DAKOTA input variable
	
	Parameters:
	-----------
	key: str
		Unique alphanumeric name of the variable
		(underscores are OK).
	
	dtype: type
		Required data type
	"""
	def __init__(self, key: str, dtype: type):
		self.key = key  # TODO: ensure valid key names
		self._dtype = dtype
		self._element = None
		
	@property
	def dtype(self):
		return self._dtype
	
	@dtype.setter
	def dtype(self, d: type):
		self._dtype = d
	
	@property
	def element(self):
		return self._element
	
	@element.setter
	def element(self, e):
		if not isinstance(e, self._dtype):
			raise TypeError(f"{self.key} must be type {self._dtype.__name__}.")
		self._set_element(e)
	
	@abc.abstractmethod
	def _set_element(self, e):
		pass
	
	@abc.abstractmethod
	def _get_strings(self) -> typing.Tuple[str]:
		pass


class StateVariable(Variable):
	"""Discrete state DAKOTA input variable

	Parameters:
	-----------
	key: str
		Unique alphanumeric name of the variable

	dtype: type
		Must be one of: {str, float, int}

	"""
	def __init__(self, key, dtype, element):
		super().__init__(key, dtype)
		self.element = element
	
	@classmethod
	def fromVariable(cls, other):
		"""Cast another variable as a StateVariable"""
		return cls(other.key, other.dtype, other.element)
	
	def _set_element(self, e):
		self._element = e
	
	def _get_strings(self):
		namestr = '"{}"'.format(self.key)
		if self.dtype is str:
			elemstr = '"{}"'.format(self.element)
		else:
			elemstr = ' {} '.format(self.element)
		return namestr, elemstr


