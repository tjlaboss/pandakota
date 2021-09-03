#! /usr/bin/env python
"""
Callable Analysis Driver for DAKOTA
"""

# import pandakota
import pandakota.names
import argparse


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

