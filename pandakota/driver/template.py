"""
Driver Template
"""

TEMPLATE = """\
#! /bin/sh
# Dakota Configuration
export DAKOTA={dakota_root}
export PYTHONPATH=$PYTHONPATH:{dakota_python}
# Pass arguments to Python
/usr/bin/env python "$@"
"""


def get_driver_sh(
		dakota_root: str,
		dakota_python="$DAKOTA/share/dakota/Python",
) -> str:
	"""Get the contents of the driver shell script.
	
	Parameters:
	-----------
	dakota_root: str
		Path to the root DAKOTA installation.
	
	dakota_python: str, optional
		Path to the DAKOTA Python libraries.
		Defaults to {dakota_root}/share/dakota/Python
	
	Returns:
	--------
	The script with those paths
	"""
	return TEMPLATE.format(**locals())
