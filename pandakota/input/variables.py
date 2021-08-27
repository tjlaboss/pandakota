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
		self._element = e
	
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
	def __init__(self, key, dtype, nominal):
		super().__init__(key, dtype)
		self.element = nominal
	
	@property
	def nominal(self):
		return self.element
	
	@classmethod
	def fromVariable(cls, other):
		"""Cast another variable as a StateVariable"""
		return cls(other.key, other.dtype, other.element)
	
	def _get_strings(self):
		namestr = '"{}"'.format(self.key)
		if self.dtype is str:
			elemstr = '"{}"'.format(self.element)
		else:
			elemstr = ' {} '.format(self.element)
		return namestr, elemstr

class NormalUncertainVariable(Variable):
	"""DAKOTA input variable described by a normal distribution

	Parameters:
	-----------
	key: str
		Unique alphanumeric name of the variable

	mean: float
		Mean value of the normal distribution

	std_dev: float
		Standard deviation of the normal distribution

	"""
	def __init__(self, key: str, mean: float, std_dev: float):
		super().__init__(key, dtype=float)
		self.element = mean
		self.std_dev = std_dev
	
	@property
	def mean(self):
		return self.element
	
	def _get_strings(self):
		namestr = f'"{self.key}"'
		meanstr = f' {self.mean} '
		stdvstr = f' {self.std_dev} '
		return namestr, meanstr, stdvstr


class UniformUncertainVariable(Variable):
	"""DAKOTA input variable described by a uniform distribution

	Parameters:
	-----------
	key: str
		Unique alphanumeric name of the variable

	upper: float
		Upper limit of the uniform distribution

	lower: float
		Lower limit of the uniform distribution

	"""
	def __init__(self, key: str, lower: float, upper: float):
		super().__init__(key, dtype=float)
		self._lower = lower
		self._upper = upper
		
	@property
	def lower(self):
		return self._lower
	
	@lower.setter
	def lower(self, l):
		if l >= self._upper:
			raise ValueError(f"lower must be < upper ({self._upper}).")
		self._lower = l
		self.__reset_element()
	
	@property
	def upper(self):
		return self._upper
	
	@upper.setter
	def upper(self, u):
		if u <= self._lower:
			raise ValueError(f"upper must be > lower ({self._lower}).")
		self._upper = u
		self.__reset_element()
	
	def __reset_element(self):
		return 0.5*(self.upper + self.lower)
	
	def _get_strings(self):
		name_str = f'"{self.key}"'
		lowerstr = f' {self.lower} '
		upperstr = f' {self.upper} '
		return name_str, lowerstr, upperstr
