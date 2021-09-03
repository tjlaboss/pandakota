"""YAML

Import Ruamel YAML if available, PyYaml otherwise. Simple as.
"""

RUAMEL = "Ruamel"
PYYAML = "PyYAML"

try:
	from ruamel import yaml
	from ruamel.yaml.parser import ParserError
	parser = RUAMEL
except (ModuleNotFoundError, ImportError):
	import yaml
	from yaml.parser import ParserError
	parser = PYYAML


def dump(data, stream, **kwargs):
	"""Wrapper to handle the divergent dumping"""
	if parser == RUAMEL:
		yaml.YAML(**kwargs).dump(data, stream)
	else:
		yaml.dump(data, stream, **kwargs)
