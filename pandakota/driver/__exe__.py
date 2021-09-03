#! /usr/bin/env python
"""
Callable Analysis Driver for DAKOTA
"""

import argparse
import typing
import os.path
import logging
from numpy import NaN
import dakota.interfacing as di
import pandakota.names
from pandakota._yaml import yaml, ParserError
import atexit


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


def create_driver(params: di.Parameters) -> pandakota.Driver:
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
	

def write_results(
		driver: pandakota.Driver,
		estat: int,
		results_dict: typing.Dict,
		results_out: di.Results
):
	# Load the results.
	funcvals = {"eval_id": driver.eval_id}
	funcvals.update(results_dict[driver.function_tag])
	gradvals = results_dict.get(driver.gradient_tag)
	hessvals = results_dict.get(driver.hessian_tag)
	
	logfmt = f"{driver.__class__.__name__}:\ti: {driver.eval_id}"
	logfmt += "\tn: {var}\t{q}: {val}"
	results_items = list(results_out.items())
	n = len(results_items)
	
	for var, response in results_items:
		__get_result(
			estat, var, logfmt, driver, response, funcvals, gradvals, hessvals, n
		)
	results_out.write()


def __get_result(
		estat: int,
		var: str,
		logfmt: str,
		driver: pandakota.Driver,
		response: di.Response,
		funcvals: typing.Dict,
		gradvals: typing.Dict,
		hessvals: typing.Dict,
		n: int
):
	if response.asv.function:
		if estat:
			response.function = NaN
		else:
			logtxt = logfmt.format(q="value", var=var, val=funcvals[var])
			driver.log(level=logging.INFO, msg=logtxt)
			response.function = funcvals[var]
	if response.asv.gradient:
		if estat:
			response.gradient = [NaN]*n
		else:
			logtxt = logfmt.format(q="gradient", var=var, val=gradvals[var])
			driver.log(level=logging.INFO, msg=logtxt)
			response.gradient = gradvals[var]
	if response.asv.hessian:
		if estat:
			response.hessian = [[NaN]*n]*n
		else:
			logtxt = logfmt.format(q="hessian", var=var, val=hessvals[var])
			driver.log(level=logging.INFO, msg=logtxt)
			response.hessian = hessvals[var]


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
	params_in, results_out = di.read_parameters_file(args.params, args.results)
	driver = create_driver(params_in)
	atexit.register(driver.kill)  # Register case.kill outside the object to handle individual log files correctly.
	estat, results_dict = run(driver)
	write_results(driver, estat, results_dict, results_out)


if __name__ == "__main__":
	main()

