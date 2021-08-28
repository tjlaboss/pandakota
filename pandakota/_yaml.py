"""YAML

Import Ruamel YAML if available, PyYaml otherwise. Simple as.
"""

try:
	from ruamel import yaml
	parser = "Ruamel"
except (ModuleNotFoundError, ImportError):
	import yaml
	parser = "PyYaml"
