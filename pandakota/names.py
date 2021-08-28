"""
Names

Simple name spaces
"""
from pandakota import _yaml


class NameSpace:
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)


class files(NameSpace):
	"""DAKOTA File Names"""
	inp = "dak.in"
	out = "dak.out"
	tab = "dak.tab"
	parameters = "params.in"
	results = "results.out"


class fmt_files(NameSpace):
	"""DAKOTA File Name Formatters"""
	inp = "dak_{}.in"
	out = "dak_{}.out"
	tab = "dak_{}.tab"
	rst = "Restart{}.rst"


class dd(NameSpace):
	"""DAKOTA Default Directories"""
	workdir = "."
	study = "dakota_study"
	plots = "plots"
	convergence = "converge"
	iterations = "iters"


class config(NameSpace):
	"""Config keys"""
	parser = _yaml.parser
	options = "options.yml"
	workdir = "workdir"

