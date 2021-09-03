"""
Analysis Driver
"""


import abc
import typing


RESULT_TYPE = typing.Tuple[
	int,
	typing.Dict[str, typing.Dict],
]


class Driver(abc.ABC):
	"""Abstract Base Class for a DAKOTA analysis driver"""
	function_tag = "function"
	gradient_tag = "gradient"
	hessian_tag = "hessian"
	
	def __init__(self, eval_id, param_dict, **kwargs):
		self._eval_id = eval_id
		self.param_dict = param_dict
		self._logger = None
		self._logfile = None
		self._logstream = None
		self._loghandler = None
		self._procs = []  # List of objects with a .kill() method.
	
	@property
	def eval_id(self):
		return self._eval_id

	@abc.abstractmethod
	def write_inputs(self):
		"""Write inputs and do any setup before execution."""
		pass
	
	@abc.abstractmethod
	def run_analysis(self):
		"""Execute the analysis"""
		pass
	
	@abc.abstractmethod
	def get_results(self) -> RESULT_TYPE:
		"""Collect and return the results."""
		err_stat = 1
		error_result = {"Error": "No results to load."}
		results = {
			self.function_tag: error_result,
			self.gradient_tag: error_result,
			self.hessian_tag: error_result
		}
		return err_stat, results
		
		



