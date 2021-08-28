"""Methods

DAKOTA Methods
"""

import abc
import typing


def _check_input(
		attr: str, 
		allowed: typing.Iterable, 
		candidate, 
		enforce_lowercase: bool=True,
		populated_prereqs: typing.Dict=None
):
	"""Check an attribute for validity. If invalid, raise an error.

	Parameters:
	-----------
	attr: str
		Name of the attribute we will be setting
	allowed: Iterable
		List, set, etc. of valid values for the variable
	candidate: object
		Candidate value for the attribute
	enforce_lowercase: bool; optional
		If `candidate` is a string, whether to force it to be lowercase.
		[Default: True]
	populated_prereqs: dict; optional
		If provided, a dictionary of {prereq_attr : value} pairs,
		where every `value` must be truthy in order to set `attr`.
		[Default: None --> no prerequisites.]

	Returns:
	--------
	candidate: object
		The submitted `candidate`, possibly in lower-case.
	"""
	if not candidate:
		return candidate
	if isinstance(candidate, str) and enforce_lowercase:
		candidate = candidate.lower()
	assert candidate in allowed, f"{attr} must be one of: {allowed}"
	if populated_prereqs:
		missing_prereqs = [k for k, v in populated_prereqs.items() if not v]
		assert not missing_prereqs, \
			f"{attr} {repr(candidate)} requires the following attributes to be set: {missing_prereqs}"
	return candidate
	
	
def _check_numeric_input(
		attr: str,
		candidate: float,
		lower: float=0.0,
		upper: float=1.0,
		allow_lower: bool=False,
		allow_upper: bool=False
) -> (float, None):
	"""Check that a numeric attribute fits between the allowed bounds.

	The default range is (0, 1) (exclusive).

	Parameters:
	-----------
	attr: str
		Name of the attribute we are setting.
	candidate: float
		Candidate value for the attribute.
	lower: float; optional
		Minimum of the allowed range.
		[Default: 0]
	upper: float; optional
		Maximum of the allowed range.
		[Default: 1]
	allow_lower: bool; optional
		Whether to include the minimum in the allowed values.
		[Default: False]
	allow_upper: bool; optional
		Whether to include the maximum in the allowed values.
		[Default: False]

	Returns:
	--------
	candidate: float
		The candidate value
	"""
	assert upper > lower, "Upper bound must be greater than lower bound."
	if candidate is None:
		return candidate
	err_fmt = "{candidate} is not in the allowed range: {a}{min_allowed}, {max_allowed}{z}"
	if allow_lower and allow_upper:
		if lower <= candidate <= upper:
			return candidate
		a = '['
		z = ']'
		raise ValueError(err_fmt.format(**locals()))
	if allow_lower and not allow_upper:
		if lower <= candidate < upper:
			return candidate
		a = '['
		b = ')'
		raise ValueError(err_fmt.format(**locals()))
	if not allow_lower and allow_upper:
		if lower < candidate <= upper:
			return candidate
		a = '('
		b = ']'
		raise ValueError(err_fmt.format(**locals()))
	if not allow_lower and not allow_upper:
		if lower < candidate < upper:
			return candidate
		a = '('
		b = ')'
		raise ValueError(err_fmt.format(**locals()))


class Method(abc.ABC):
	"""Abstract Base Class for all methods"""
	requires_gradients = False
	requires_hessians = False
	def __init__(self):
		self._id_method = self.__class__.__name__
		self._refinements: typing.List[int] = []
	
	def __str__(self):
		return self.to_string()
	
	@property
	def refinements(self):
		return self._refinements
	
	def add_refinement(self, refinement_samples: int):
		self._refinements.append(refinement_samples)
	
	@abc.abstractmethod
	def to_string(self) -> str:
		ret = "method"
		ret += f'\n\tid_method = "{self._id_method}"'
		return ret


class Sampling(Method):
	"""Abstract Base Class for all sampling methods"""
	sample_type = None
	def __init__(self, nsamples: int, seed: int):
		super().__init__()
		assert isinstance(nsamples, int) and nsamples > 0, "nsamples must be an integer > 0."
		assert isinstance(seed, int), "seed must be an integer"
		self._nsamples = nsamples
		self._seed = seed
		self._id_method = "UQ"
	
	@property
	def nsamples(self):
		return self._nsamples
	
	def to_string(self) -> str:
		ret = super().to_string()
		ret += "\n\tsampling"
		ret += f"\n\t\tsample_type = {self.sample_type}"
		ret += f"\n\t\tseed = {self._seed}"
		ret += f"\n\t\tsamples = {self._nsamples}"
		if self._refinements:
			ret += "\n\t\t\trefinement_samples = " + " ".join(([str(r) for r in self._refinements]))
		return ret


class MonteCarloSampling(Sampling):
	"""Random sampling"""
	sample_type = "random"
	def __init__(self, nsamples: int, seed: int):
		super().__init__(nsamples, seed)


class LatinHypercubeSampling(Sampling):
	"""LHS"""
	sample_type = "lhs"
	def __init__(self, nsamples: int, seed: int):
		super().__init__(nsamples, seed)
	
	def add_refinement(self, refinement_samples: int=None):
		if not self._refinements:
			allowed = self._nsamples
		else:
			allowed = 2*self._refinements[-1]
		if refinement_samples is None:
			refinement_samples = allowed
		if refinement_samples != allowed:
			raise ValueError("LHS Refinement Samples must be exactly double the previous number of samples.")
		return super().add_refinement(refinement_samples)


class Optimize(Method):
	"""Abstract Base Class for all optimization methods"""
	optimize_type = None
	
	def __init__(
			self,
			max_iterations: int,
			max_function_evaluations: int,
			convergence_tolerance: float
	):
		super().__init__()
		self._id_method = "Optimize"
		if max_function_evaluations is not None and max_iterations is not None:
			assert max_function_evaluations > max_iterations, \
				"The maximum number of function evaluations must exceed the maximum number of iterations."
		self._max_iterations = max_iterations
		self._max_function_evaluations = max_function_evaluations
		self._convergence_tolerance = convergence_tolerance
	
	@property
	def max_iterations(self):
		return self._max_iterations
	
	@property
	def max_function_evaluations(self):
		return self._max_function_evaluations
	
	@property
	def convergence_tolerance(self):
		return self._convergence_tolerance
	
	def to_string(self) -> str:
		ret = super().to_string()
		ret += f"\n\t\t{self.optimize_type}"
		ret += f"\n\t\t\tmax_iterations = {self._max_iterations}"
		ret += f"\n\t\t\tmax_function_evaluations = {self._max_function_evaluations}"
		ret += f"\n\t\t\tconvergence_tolerance = {self._convergence_tolerance}"
		return ret


class NcsuDirectOptimize(Optimize):
	optimize_type = "ncsu_direct"
	
	def __init__(
			self, 
			max_iterations: int, 
			max_function_evaluations: int, 
			convergence_tolerance: int,
			solution_target: float=None, 
			min_boxsize_limit: float=None, 
			volume_boxsize_limit: float=None
	):
		super().__init__(max_iterations, max_function_evaluations, convergence_tolerance)
		self._solution_target = solution_target
		self._min_boxsize_limit = min_boxsize_limit
		self._volume_boxsize_limit = volume_boxsize_limit
	
	@property
	def solution_target(self):
		return self._solution_target
	
	@property
	def min_boxsize_limit(self):
		return self._min_boxsize_limit
	
	@property
	def volume_boxsize_limit(self):
		return self._volume_boxsize_limit
	
	def to_string(self) -> str:
		ret = super().to_string()
		for var in ("solution_target", "min_boxsize_limit", "volume_boxsize_limit"):
			val = getattr(self, "_" + var, None)
			if val:
				ret += f"\n\t\t\t{var} = {val}"
		return ret


class JegaOptimize(Optimize):
	"""Abstract Base Class for JEGA methods"""
	optimize_type = "jega  # TODO: Change to 'soga' or 'moga'."
	replacement_types = {"elitist", "roulette_wheel", "unique_roulette_wheel"}
	convergence_types = set()
	initialization_types = {"simple_random", "unique_random", "flat_file"}
	crossover_types = {"multi_point_binary", "multi_point_real", "multi_point_parameterized_binary", "shuffle_random"}
	mutation_types = {"replace_uniform", "bit_random", "offset_uniform", "offset_cauchy", "offset_normal"}
	type_rate_pairs = {"crossover_type": "crossover_rate", "mutation_type": "mutation_rate"}
	
	def __init__(
			self,
			max_iterations: int,
			max_function_evaluations: int,
			convergence_tolerance: float,
			population_size: int,
			seed: int,
			replacement_type: str=None,
			convergence_type: str=None,
			initialization_type: str=None,
			crossover_type: str=None,
			crossover_rate: float=None,
			mutation_type: str=None,
			mutation_rate: float=None,
			num_parents: int=None,
			num_offspring: int=None,
			flat_file_path: str=None
	):
		super().__init__(max_iterations, max_function_evaluations, convergence_tolerance)
		self._population_size = population_size
		assert isinstance(seed, int), "seed must be an integer"
		self._seed = seed
		self._flat_file_path = flat_file_path  # consider enforcing the existence of the file at instantiation
		self._replacement_type = self.check_replacement_type(replacement_type)
		self._convergence_type = self.check_convergence_type(convergence_type)
		self._initialization_type = self.check_initialization_type(initialization_type, flat_file_path)
		self._crossover_type = self.check_crossover_type(crossover_type)
		self._crossover_rate = crossover_rate
		if self._crossover_type != "shuffle_random":
			assert num_parents is None and num_offspring is None, \
				"Parameters 'num_parents' and 'num_offspring' may only be set for crossover_type 'shuffle_random'."
		self._num_parents = num_parents
		self._num_offspring = num_offspring
		self._mutation_type = self.check_mutation_type(mutation_type)
		self._mutation_rate = mutation_rate
	
	@property
	def population_size(self):
		return self._population_size
	
	@property
	def seed(self):
		return self._seed
	
	@classmethod
	def check_replacement_type(cls, rt: str):
		return _check_input("replacement_type", cls.replacement_types, rt)
	
	@classmethod
	def check_convergence_type(cls, ct: str):
		return _check_input("convergence_type", cls.convergence_types, ct)
	
	@classmethod
	def check_initialization_type(cls, it: str, flat_file_path: str):
		prereqs = {}
		if it and it.lower() == "flat_file":
			prereqs["flat_file_path"] = flat_file_path
		return _check_input("initialization_type", cls.initialization_types, it, populated_prereqs=prereqs)
	
	@classmethod
	def check_crossover_type(cls, cot: str):
		return _check_input("crossover_type", cls.crossover_types, cot)
	
	@classmethod
	def check_mutation_type(cls, mt: str):
		return _check_input("mutation_type", cls.mutation_types, mt)
	
	def to_string(self) -> str:
		ret = super().to_string()
		for var in (
				"seed", "population_size", "replacement_type", "convergence_type", "initialization_type",
				"crossover_type", "mutation_type"
		):
			val = getattr(self, "_" + var, None)
			rate_var = self.type_rate_pairs.get(var, None)
			rate_val = getattr(self, "_" + rate_var) if rate_var is not None else None
			if val:
				ret += f"\n\t\t\t{var} = {val}"
			if rate_val is not None:
				ret += f"\n\t\t\t\t{rate_var} = {rate_val}"
			if var == "crossover_type" and val == "shuffle_random":
				if self._num_parents:
					ret += f"\n\t\t\t\tnum_parents = {self._num_parents}"
				if self._num_offspring:
					ret += f"\n\t\t\t\tnum_offspring = {self._num_offspring}"
			if var == "initialization_type" and val == "flat_file":
				ret += " " + self._flat_file_path
		return ret


class SogaOptimize(JegaOptimize):
	optimize_type = "soga"
	replacement_types = JegaOptimize.replacement_types | {"favor_feasible"}
	convergence_types = JegaOptimize.convergence_types | {"best_fitness_tracker", "average_fitness_tracker"}


class MogaOptimize(JegaOptimize):
	optimize_type = "moga"
	replacement_types = JegaOptimize.replacement_types | {"below_limit"}
	convergence_types = JegaOptimize.convergence_types | {"metric_tracker", "percent_change", "num_generations"}
	
	def __init__(self, *args, niching_type=None, postprocessor_type=None, **kwargs):
		super().__init__(*args, **kwargs)
		if niching_type is not None:
			raise NotImplementedError("MOGA:niching_type")
		if postprocessor_type is not None:
			raise NotImplementedError("MOGA:postprocessor_type")


class OptppOptimize(Optimize):
	"""Abstract Base Class for Opt++ family of local optimizers"""
	optimize_type = "optpp  # TODO: change to one of the optpp_* methods"
	merit_functions = {"el_bakry", "argaez_tapia", "van_shanno"}
	
	def __init__(
			self,
			max_iterations: int,
			max_function_evaluations: int,
			convergence_tolerance: float,
			max_step: float=None,
			gradient_tolerance: float=None,
			speculative: bool=False,
			merit_function: str=None
	):
		super().__init__(max_iterations, max_function_evaluations, convergence_tolerance)
		self._max_step = max_step
		self._gradient_tolerance = gradient_tolerance
		self._speculative = speculative
		self._merit_function = self.check_merit_function(merit_function)
	
	@classmethod
	def check_merit_function(cls, mf: str):
		return _check_input("merit_function", cls.merit_functions, mf)
	
	def to_string(self) ->  str:
		ret = super().to_string()
		for var in ("max_step", "gradient_tolerance", "merit_function"):
			val = getattr(self, "_" + var, None)
			if val:
				ret += f"\n\t\t\t{var} = {val}"
		if self._speculative:
			ret += "\n\t\t\tspeculative  # Use speculative increments"
		return ret


class OptppPdsOptimize(OptppOptimize):
	"""Simplex-based derivative-free optimization"""
	optimize_type = "optpp_pds"
	
	def __init__(
			self,
			max_iterations: int,
			max_function_evaluations: int,
			convergence_tolerance: float,
			search_scheme_size=None
	):
		super(OptppPdsOptimize, self).__init__(max_iterations, max_function_evaluations, convergence_tolerance)
		if search_scheme_size is not None:
			assert isinstance(search_scheme_size, int), "search_scheme_size must be an integer."
		self._search_scheme_size = search_scheme_size
	
	def to_string(self) -> str:
		ret = super().to_string()
		if self._search_scheme_size:
			ret += f"\n\t\t\t{'search_scheme_size'} = {self._search_scheme_size}"
		return ret


class OptppCgOptimize(OptppOptimize):
	"""Conjugate gradient optimization"""
	optimize_type = "optpp_cg"
	requires_gradients = True
	
	def __init__(
			self,
			max_iterations: int,
			max_function_evaluations: int,
			convergence_tolerance: float,
			max_step: float=None,
			gradient_tolerance: float=None,
			speculative: bool=False
	):
		# No merit_function. Otherwise, same as parent class
		super().__init__(
			max_iterations, max_function_evaluations, convergence_tolerance, max_step, gradient_tolerance,
			speculative, merit_function=None
		)


class OptppNewtonOptimize(OptppOptimize):
	"""The optpp_newton method, and base class for other Opt++ Newton methods"""
	optimize_type = "optpp_newton"
	search_methods = {"value_based_line_search", "gradient_based_line_search", "trust_region", "tr_pds"}
	requires_gradients = True
	requires_hessians = True
	
	def __init__(
			self,
			*args,
			search_method: str=None,
			centering_parameter: float=None,
			steplength_to_boundary: float=None,
			**kwargs):
		super().__init__(*args, **kwargs)
		self._search_method = self.check_search_method(search_method)
		self._centering_parameter = _check_numeric_input(
			"centering_parameter", centering_parameter, allow_lower=True, allow_upper=True
		)
		self._steplength_to_boundary = _check_numeric_input("steplength_to_boundary", steplength_to_boundary)
	
	@classmethod
	def check_search_method(cls, sm):
		return _check_input("search_method", cls.search_methods, sm)
	
	def to_string(self) -> str:
		ret = super().to_string()
		for var in ("search_method", "centering_parameter", "steplength_to_boundary"):
			val = getattr(self, "_" + var, None)
			if val:
				ret += f"\n\t\t\t{var} = {val}"
		return ret


class OptppQNewtonOptimize(OptppNewtonOptimize):
	"""Quasi-Newton optimization method"""
	optimize_type = "optpp_q_newton"
	requires_gradients = True
	requires_hessians = False


class OptppGNewtonOptimize(OptppNewtonOptimize):
	"""Newton optimization method based on least-squares calibration"""
	optimize_type = "optpp_g_newton"
	requires_gradients = False
	requires_hessians = False


class OptppFdNewtonOptimize(OptppNewtonOptimize):
	"""Finite Difference Newton optimization method"""
	optimize_type = "optpp_fd_newton"
	requires_gradients = True
	requires_hessians = False


class NlpqlSqpOptimize(Optimize):
	"""NLPQL Sequential Quadratic Program"""
	optimize_type = "nlpql_sqp"


class ColinyCobylaOptimize(Optimize):
	"""Constrained Optimization BY Linear Approximations"""
	optimize_type = "coliny_cobyla"
	
	def __init__(
			self,
			max_iterations: int,
			max_function_evaluations: int,
			convergence_tolerance: float,
			initial_delta: float=None,
			variable_tolerance: float=None,
			solution_target: float=None
	):
		super().__init__(max_iterations, max_function_evaluations, convergence_tolerance)
		self._initial_delta = initial_delta
		self._variable_tolerance = _check_numeric_input("variable_tolerance", variable_tolerance)
		self._solution_target = solution_target
	
	def to_string(self) -> str:
		ret = super().to_string()
		for var in ("initial_delta", "variable_tolerance", "solution_target"):
			val = getattr(self, "_" + var, None)
			if val:
				ret += f"\n\t\t\t{var} = {val}"
		return ret
