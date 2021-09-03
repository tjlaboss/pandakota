#! /usr/bin/env python
"""
Callable Analysis Driver for DAKOTA
"""

import os.path
import pandakota.names
from pandakota._yaml import yaml, ParserError
import argparse
import typing


def load_options() -> typing.Dict:
	"""Load the Pandakota Options Dictionary"""
	fullpath = os.path.abspath(pandakota.names.config.options)
	try:
		with open(pandakota.names.config.options, 'r') as fyaml:
			options = yaml.load(fyaml, Loader=yaml.FullLoader)
	except ParserError as e:
		errstr = f"Error parsing YAML: {e}. {fullpath} does not appear to be a valid YAML file."
		raise ParserError(errstr)
	except ImportError as e:
		raise ImportError(f"Failed to import pandakota.Driver from {fullpath}: {e}")
	return options


def main():
	descript = f"Generic analysis_driver script for Pandakota v{pandakota.__version__}"
	parser = argparse.ArgumentParser(description=descript)
	parser.add_argument(
		"params",
		default=pandakota.names.files.parameters,
		help="Path to DAKOTA parameters (input) file"
	)
	parser.add_argument(
		"results",
		default=pandakota.names.files.results,
		help="Path to DAKOTA results (output) file"
	)
	args = parser.parse_args()
	raise NotImplementedError("Have not implemented main() yet.")


if __name__ == "__main__":
	main()

