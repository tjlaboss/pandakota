"""
Variables

Module containing DAKOTA variable classes
"""
import abc

class Variable(abc.ABC):
	"""Abstract Base Class for DAKOTA input variable
	
	Parameters:
	-----------
	stream: str
		Text of the partial matrix
	"""
	def __init__(self, key: str, dtype: type):
		self.key = key
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
