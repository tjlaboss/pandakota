#! /usr/bin/env python
"""
Callable Analysis Driver for DAKOTA
"""

import argparse
import typing
import os.path
import logging
import dakota.interfacing as di
import pandakota.names
from pandakota._yaml import yaml, ParserError


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


def create_driver(params) -> pandakota.Driver:
	log_queue = []
	options = load_options()
	eval_id = int(params.eval_id)
	driver_dict = options[pandakota.names.config.driver]
	DriverClass = pandakota.Driver.classFromDict(driver_dict)
	log_queue.append((logging.INFO, f"Using class: {DriverClass.__name__}"))
	driver = DriverClass(eval_id, params._variables, **options)
	while log_queue:
		driver.log(*log_queue.pop(0))  # FIFO
	return driver


def run(driver: pandakota.Driver) -> pandakota.driver.driver.RESULT_TYPE:
	driver.write_inputs()
	driver.run_analysis()
	return driver.get_results()
	


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
	params, results = di.read_parameters_file(args.params, args.results)
	driver = create_driver(params)
	run(driver)
	raise NotImplementedError("Have not implemented main() yet.")


if __name__ == "__main__":
	main()

