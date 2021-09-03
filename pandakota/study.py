"""
Study

Module that runs and manages DAKOTA studies
"""
import os
import sys
import typing
import subprocess
import pandakota.input
from pandakota import driver
from pandakota import names
from pandakota import _yaml
from pandakota._version import __version__


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
	
	**config: **kwargs dict
		Configuration dictionary to be written to YAML.
		Keyword Args:
		-------------
		workdir: str
			Working directory for the study.
		
	"""
	def __init__(
			self,
			deck: pandakota.input.Deck,
			DriverClass: typing.Type,
			concurrency: int=None,
			asynchronous: bool=True,
			bin_path: str="dakota",
			**config
	):
		self._config = config
		self._deck = deck
		self.concurrency = concurrency
		self.asynchronous = asynchronous
		self._bin_path = bin_path
		#
		self._driver = None
		self.driver = DriverClass
		#
		self._workdir = config.get(names.config.workdir, names.dd.workdir)
		self._dakota_dir = os.path.join(self._workdir, names.dd.study)
		self._plot_dir = os.path.join(self._workdir, names.dd.plots)
		self._makedirs()
		#
		self._last_rst = None
		self._last_inp = None
		self._last_out = None
		self._last_tab = None
		self._last_df = None
		
	def __getitem__(self, item):
		return self._config[item]
	
	@property
	def driver(self) -> driver.Driver:
		return self._driver
	
	@driver.setter
	def driver(self, DriverClass: typing.Type):
		assert issubclass(DriverClass, driver.Driver), \
			"DriverClass must be a subclass of pandakota.Driver " \
			f"(not type: {type(DriverClass)})."
		self._driver = DriverClass
		self._config["driver"] = DriverClass.classToDict()
	
	def _makedirs(self):
		"""Make the nescessary directories."""
		for folder in (
			self._workdir,
			self._dakota_dir,
			self._plot_dir,
			# And more to come,
		):
			os.makedirs(folder, exist_ok=True)
	
	def _write_options_yaml(self, yaml_fname=names.config.options):
		"""Write the options yaml, obtained from YAML"""
		yaml_fpath = os.path.join(self._dakota_dir, yaml_fname)
		with open(yaml_fpath, 'w') as fyaml:
			fyaml.write(f"# Pandakota v{__version__} Options YAML\n")
			fyaml.write(f"#    dumped by: {_yaml.parser} v{_yaml.yaml.__version__}\n\n")
			_yaml.dump(self._config, fyaml)
		print(f"Options yaml written to: {yaml_fpath}")
	
	def _get_execlist(
			self,
			dak_in: str,
			dak_out: str,
			dak_rst: str
	) -> typing.List[str]:
		execlist = [self._bin_path, "-i", dak_in, "-o", dak_out]
		if self._last_rst:
			execlist += ["-read_restart", self._last_rst]
		execlist += ["-write_restart", dak_rst]
		return execlist
	
	def _execute_process(
			self,
			dakota_in: str,
			deck_text: str,
			exec_list: typing.List[str],
			dry=False
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
		
		dry: bool, optional
			Whether to do a dry run (write deck, nothing).
			
		Returns:
		--------
		proc: subprocess.Popen
			Opened process instance.
		"""
		
		with open(dakota_in, 'w') as f:
			f.write(deck_text)
		print(f"DAKOTA deck written to: {dakota_in}")
		# Write the driver options.
		self._write_options_yaml()
		# Deal with dry run case
		if dry:
			exec_list = ["echo", "Dry Run: $"] + exec_list
		# Execute DAKOTA deck
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
			dry=False
	) -> int:
		"""Execute DAKOTA, wait, and return the exit code."""
		proc = self._execute_process(dakota_in, deck_text, exec_list, dry)
		exitcode = proc.wait()
		if not exitcode:
			print("...DAKOTA execution is complete.")
		else:
			print("...DAKOTA execution FAILED.", file=sys.stderr)
		return exitcode
	
	def run_dakota(self, dry_run=False):
		"""Run the initial samples
		
		Parameters:
		-----------
		dry_run: bool, optioanl
			Whether to do a "dry run": generate everything,
			but do not actually execute DAKOTA.
			[Default: False]
		
		"""
		first_restart = names.fmt_files.rst.format(0)
		execlist = self._get_execlist(
			dak_in=names.files.inp,
			dak_out=names.files.out,
			dak_rst=first_restart
		)
		text = self._deck.get_deck(
			executioner=" ".join(execlist),
			asynchronous=self.asynchronous,
			concurrency=self.concurrency,
		)
		stat = self._execute_wait(
			dakota_in=os.path.join(self._dakota_dir, names.files.inp),
			deck_text=text,
			exec_list=execlist,
			dry=dry_run
		)
		# Load results
		self._last_rst = first_restart
		self._last_inp = os.path.join(self._dakota_dir, names.files.inp)
		self._last_out = os.path.join(self._dakota_dir, names.files.out)
		self._last_tab = os.path.join(self._dakota_dir, names.files.tab)
		self._last_df = None  # TODO: Read Tabular Results
	
	