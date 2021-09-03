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
	return TEMPLATE.format(dakota_root, dakota_python)
