"""Derivatives

Gradients (first derivative) and Hessians (second derivatives)
"""

# Gradient and Hessian settings
DERIVATIVE_NONE = "no"
DERIVATIVE_NUMERIC = "numerical"
DERIVATIVE_ANALYTIC = "analytic"
DERIVATIVE_MIXED = "mixed"
GRADIENT_TYPES = {DERIVATIVE_NONE, DERIVATIVE_NUMERIC, DERIVATIVE_ANALYTIC, DERIVATIVE_MIXED}
SOURCE_DAKOTA = "dakota"
SOURCE_VENDOR = "vendor"
GRADIENT_SOURCES = {SOURCE_DAKOTA, SOURCE_VENDOR}
TYPE_CENTRAL = "central"
TYPE_FORWARD = "forward"
INTERVAL_TYPES = {TYPE_CENTRAL, TYPE_FORWARD}
HESSIAN_QUASI = "quasi"
HESSIAN_TYPES = {HESSIAN_QUASI} | GRADIENT_TYPES
QUASI_BFGS = "bfgs"
QUASI_SR1 = "sr1"
HESSIAN_QUASI_APPROXIMATIONS = {QUASI_BFGS, QUASI_SR1}
SCALING_RELATIVE = "relative"
SCALING_ABSOLUTE = "absolute"
SCALING_BOUNDS = "bounds"
HESSIAN_STEP_SCALINGS = {SCALING_RELATIVE, SCALING_ABSOLUTE, SCALING_BOUNDS}



import abc
import typing


def _format_id(
		id_list: typing.Iterable[int],
		key: str
):
	if not id_list:
		return ""
	return f"\n\t\t{key} " + " ".join([str(x) for x in id_list])


def _format_fd_step_size(
		fd_list: typing.Iterable[float],
		key: str
) -> str:
	if not fd_list:
		return ""
	return f"\n\t\t{key} " + " ".join([str(x) for x in fd_list])


class Derivatives(abc.ABC):
	"""Abstract Bace Class for Derivatives"""
	order = None
	key = "derivatives  # this class is not meant to be instantiated directly"
	
	def __init__(
			self,
			derivative_type: str,
			fd_step_size: typing.Iterable[float],
			id_numerical: typing.Iterable[int],
			id_analytic: typing.Iterable[int]
	):
		if derivative_type == DERIVATIVE_NONE:
			derivative_type = None
		self._derivative_type = derivative_type
		self._fd_step_size = fd_step_size
		self._id_numerical = id_numerical
		self._id_analytic = id_analytic
	
	def __str__(self):
		return self.to_string()
	
	def _no(self) -> str:
		return f"\t{DERIVATIVE_NONE}_{self.key}"
	
	def to_string(self) -> str:
		if not self._derivative_type:
			return self._no()
		ret = f"\n\t{self._derivative_type}_{self.key}"
		ret += _format_id(self._id_analytic, f"id_analytic_{self.key}")
		ret += _format_id(self._id_numerical, f"id_numerical_{self.key}")
		return ret


class Gradients(Derivatives):
	"""First Derivatives"""
	order = 1
	key = "gradients"
	
	def __init__(
			self,
			gradient_type: str,
			method_source: str=None,
			interval_type: str=None,
			fd_step_size: typing.Iterable[float]=None,
			id_numerical: typing.Iterable[int]=None,
			id_analytic: typing.Iterable[int]=None
	):
		assert gradient_type in {None} | GRADIENT_TYPES, \
			f"gradient_type must be one of {GRADIENT_TYPES}"
		assert method_source in {None} | GRADIENT_SOURCES, \
			f"method_source must be one of {GRADIENT_SOURCES}"
		assert interval_type in {None} | INTERVAL_TYPES, \
			f"interval_type must be one of {INTERVAL_TYPES}"
		super().__init__(gradient_type, fd_step_size, id_numerical, id_analytic)
		self._method_source = method_source
		self._interval_type = interval_type
	
	@property
	def gradient_type(self):
		return self._derivative_type
	
	@gradient_type.setter
	def gradient_type(self, gtype: str):
		self._derivative_type = gtype
	
	def to_string(self):
		if not self.gradient_type:
			return self._no()
		ret = super().to_string()
		if self._method_source:
			ret += f"\n\t\tmethod_source {self._method_source}"
		if self._interval_type:
			ret += f"\n\t\tinterval_type {self._interval_type}"
		ret += _format_fd_step_size(self._fd_step_size, "fd_gradient_step_size")
		return ret


class Hessians(Derivatives):
	"""Second Derivatives"""
	order = 2
	key = "hessians"
	
	def __init__(
			self,
			hessian_type: str,
			interval_type: str=None,
			step_scaling: str=None,
			quasi_approximation: str=None,
			fd_step_size: typing.Iterable[float]=None,
			id_numerical: typing.Iterable[int]=None,
			id_analytic: typing.Iterable[int]=None,
			id_quasi: typing.Iterable[int]=None,
			damped: bool=False
	):
		assert hessian_type in {None} | HESSIAN_TYPES, \
			f"hessian_type must be one of {HESSIAN_TYPES}"
		assert interval_type in {None} | INTERVAL_TYPES, \
			f"interval_type must be one of {INTERVAL_TYPES}"
		assert step_scaling in {None} | HESSIAN_STEP_SCALINGS, \
			f"step_scaling must be one of {HESSIAN_STEP_SCALINGS}"
		assert quasi_approximation in {None} | HESSIAN_QUASI_APPROXIMATIONS, \
			f"quasi_approximation must be one of {HESSIAN_QUASI_APPROXIMATIONS}"
		if hessian_type in (HESSIAN_QUASI, DERIVATIVE_MIXED) and id_quasi:
			assert quasi_approximation, f"quasi_approximation is required using quasi hessians."
		else:
			assert not quasi_approximation, \
				f"quasi_approximation may only be used when hessian_type={HESSIAN_QUASI}."
		if damped:
			assert quasi_approximation == QUASI_BFGS, \
				f"damped BFGS is may only be used when quasi_approximation={QUASI_BFGS}."
		super().__init__(hessian_type, fd_step_size, id_numerical, id_analytic)
		self._interval_type = interval_type
		self._step_scaling = step_scaling
		self._id_quasi = id_quasi
		self._quasi_approximation = quasi_approximation
		self._damped = bool(damped)
	
	@property
	def hessian_type(self):
		return self._derivative_type
	
	@hessian_type.setter
	def hessian_type(self, htype: str):
		self._derivative_type = htype
	
	def to_string(self) -> str:
		if not self.hessian_type:
			return self._no()
		ret = super().to_string()
		if self._id_quasi:
			ret += _format_id(self._id_quasi, f"id_quasi_{self.key}") + " " + self._quasi_approximation
			if self._damped:
				ret += " damped"
		if self._step_scaling:
			ret += f"\n\t\t{self._step_scaling}"
		ret += _format_fd_step_size(self._fd_step_size, "fd_hessian_step_size")
		return ret
