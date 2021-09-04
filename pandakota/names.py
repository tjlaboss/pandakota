"""
Names

Simple name spaces
"""


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
	study = "dakota_study"
	plots = "plots"
	convergence = "converge"
	iterations = "iters"

