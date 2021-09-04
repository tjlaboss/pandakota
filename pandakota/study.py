"""
Study

Module that runs and manages DAKOTA studies
"""
import os
import sys
import typing
import subprocess
import pandakota.input


# Default Directories
DD_STUDY = "dakota_study"
DD_PLOT = "plots"
DD_CONVERGENCE = "converge"
DD_ITERATIONS = "iters"
# File name formats
INP = "dak.in"
OUT = "dak.out"
TAB = "dak.tab"
INP_FMT = "dak_{}.in"
OUT_FMT = "dak_{}.out"
TAB_FMT = "dak_{}.tab"
RST_FMT = "Restart{}.rst"


class Study:
	"""A DAKOTA study to be run
	
	Parameters:
	-----------
	deck: pandakota.input.Deck
	
	concurrency: int or None
		Level of concurrency
	
	asynchronous: bool
		Whether to run samples asynchronously
	
	bin_path: str
		Path to DAKOTA executable
		
	"""
	def __init__(
			self,
			deck: pandakota.input.Deck,
			concurrency: int=None,
			asynchronous: bool=True,
			bin_path: str="dakota"
	):
		self._deck = deck
		self.concurrency = concurrency
		self.asynchronous = asynchronous
		self._bin_path = bin_path
		#
		self._workdir = "."
		self._dakota_dir = os.path.join(self._workdir, DD_STUDY)
		self._plot_dir = os.path.join(self._workdir, DD_PLOT)
		#
		self._last_restart = None
	
	def _get_execlist(
			self,
			dak_in: str,
			dak_out: str,
			dak_rst: str
	) -> typing.List[str]:
		execlist = [self._bin_path, "-i", dak_in, "-o", dak_out]
		if self._last_restart:
			execlist += ["-read_restart", self._last_restart]
		execlist += ["-write_restart", dak_rst]
		return execlist
	
	def _execute_process(
			self,
			dakota_in: str,
			deck_text: str,
			exec_list: typing.List[str]
	) -> subprocess.Popen:
		"""Execute DAKOTA, returning the process.

		Parameters:
		-----------
		dakota_in: str
			Path to write the DAKOTA input deck to.
			
		dedeck_textck: str
			Text body of the DAKOTA input deck.
			
		exec_list: list
			Execution list to pass to subprocess.Popen.
			
		Returns:
		--------
		if wait is True -> int
			Exit code for the DAKOTA execution subprocess.
			
		if wait is False -> subprocess.Popen
			Opened process instance.
		"""
		
		with open(dakota_in, 'w') as f:
			f.write(deck_text)
		print(f"DAKOTA deck written to: {dakota_in}")
		# Execute incremented DAKOTA deck
		orig = os.getcwd()
		os.chdir(self._dakota_dir)
		print(f"Executing:\n\t{self._dakota_dir}$  {' '.join(exec_list)}")
		proc = subprocess.Popen(
			args=exec_list,
			stdout=sys.stdout,
			stderr=sys.stderr
		)
		os.chdir(orig)
		print(f"Launched process: {proc.pid}")
		return proc
	
	def _execute_wait(
			self,
			dakota_in: str,
			deck_text: str,
			exec_list: typing.List[str],
	) -> int:
		"""Execute DAKOTA, wait, and return the exit code."""
		proc = self._execute_process(dakota_in, deck_text, exec_list)
		exitcode = proc.wait()
		if not exitcode:
			print("...DAKOTA execution is complete.")
		else:
			print("...DAKOTA execution FAILED.", file=sys.stderr)
		return exitcode
	
	def run_dakota(self):
		"""Run the initial samples"""
		first_restart = RST_FMT.format(0)
		execlist = self._get_execlist(INP, OUT, first_restart)
		text = self._deck.get_deck(
			executioner=" ".join(execlist),
			asynchronous=self.asynchronous,
			concurrency=self.concurrency,
		)
		stat = self._execute_wait(
			dakota_in=os.path.join(self._dakota_dir, INP),
			deck_text=text,
			exec_list=execlist,
		)
		pass
	
	