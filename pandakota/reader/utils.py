"""
utils

Useful helpers for DAKTOA reading
"""

import io
import pandas as pd


def string_to_stream(string: str) -> io.StringIO:
	return io.StringIO(string)


