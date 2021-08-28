"""Methods

DAKOTA Methods
"""

import abc
import os


class Method(abc.ABC):
	"""Abstract Base Class for all methods"""
	requires_gradients = False
	requires_hessians = False
	
	def __init__(self):
		self._id_method = self.__class__.__name__
		self._refinements = []
	
	def __str__(self):
		return self.to_string()
	
	@property
	def id_method(self):
		return self._id_method
	
	def to_string(self) -> str:
		ret = "method"
		ret += '\n\tid_method = "{}"'.format(self._id_method)
		return ret
