"""
Analysis Driver
"""

import io
import os
import abc
import typing
import inspect
import logging
import fcntl
import atexit


RESULT_TYPE = typing.Tuple[
	int,
	typing.Dict[str, typing.Dict],
]


class Driver(abc.ABC):
	"""Abstract Base Class for a DAKOTA analysis driver"""
	# DAKOTA tags
	function_tag = "function"
	gradient_tag = "gradient"
	hessian_tag = "hessian"
	# Hacky module tags
	_cls_tag = "class"
	_mod_tag = "module"
	_pth_tag = "path"
	
	def __init__(self, eval_id, param_dict, **kwargs):
		self._eval_id = eval_id
		self.param_dict = param_dict
		self._logger: logging.Logger = None
		self._logfile: str = None
		self._logstream: io.StringIO = None
		self._loghandler: logging.StreamHandler = None
		self._procs = []  # List of objects with a .kill() method.
		# Remember that atexit is in reverse order.
		# Do not resiter 'self.kill' here without removing its logging statements.
		atexit.register(self._write_stream)
	
	@property
	def eval_id(self):
		return self._eval_id
	
	@classmethod
	def classToDict(cls) -> typing.Dict[str, str]:
		mod_fpath = inspect.getmodule(cls).__file__
		moddir, modfile = os.path.split(mod_fpath)
		module = os.path.splitext(modfile)[0]
		dict_out = {
			cls._cls_tag: cls.__name__,
			cls._mod_tag: module,
			cls._pth_tag: moddir
		}
		return dict_out
	
	def _write_stream(self):
		"""Write the stream to the communal log."""
		if self._logstream is None:
			return
		self._logstream.flush()
		with open(self._logfile, 'a') as f:
			fcntl.flock(f, fcntl.LOCK_EX)
			f.write(self._logstream.getvalue())
			fcntl.flock(f, fcntl.LOCK_UN)
		self._logstream.close()
	
	def _flush_stream(self):
		"""Renew the logstream. Write to the communal log and start a new one."""
		self._write_stream()
		self._logstream = io.StringIO()
		self._loghandler.setStream(self._logstream)
	
	def activate_collective_logging(self, logfile: str, logfmt=None):
		"""Set up logging for the communal log file."""
		self._logfile = logfile
		self._logstream = io.StringIO()
		self._loghandler = logging.StreamHandler(self._logstream)
		self._logger.addHandler(self._loghandler)
		if logfmt:
			self._loghandler.setFormatter(logging.Formatter(logfmt))
	
	def log(self, level: int, msg: str, *args, **kwargs):
		"""Log a message the driver level."""
		if self._logger is None:
			self._logger = logging.getLogger(self.__class__.__name__)
		self._logger.log(level, msg, *args, **kwargs)

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
		
	def kill(self):
		"""Kill any subprocesses.

		Warnings:
		---------
		If using individual log files, the logging will not work correctly here
		if we ``do atexit.register(self.kill)`` from within this object. It can
		and will overwrite the individual log file. This is not a problem when
		using collective logging.
		"""
		self.log(logging.INFO, f"Killing {self.__class__.__name__} {self.eval_id}")
		for proc in self._procs:
			proc.kill()
		self._procs = []
