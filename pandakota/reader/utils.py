"""
utils

Useful helpers for DAKTOA reading
"""

import io
import pandas as pd


def string_to_stream(string: str) -> io.StringIO:
	return io.StringIO(string)


def snip_text(text: str, start: str, end="\n\n", allow_eof=False) -> str:
	"""Crude text snipping function.
	
	Parameters:
	-----------
	text: str
		Text corpus to snip from
	
	start: str
		String that precedes the output text.
		Excluded from output.
	
	end: str; optional
		String that follows the output text.
		Excluded from output.
		[Default: "\n\n"]
	
	allow_eof: bool; optional
		Whether the end of 'text' is an allowable end.
		If True, will snip from 'start' to the end of the string
		if 'end' is not found in the text.
		[Default: False]
	
	Returns:
	--------
	str
		Snipped text
	"""
	c0 = text.find(start)
	if c0 == -1:
		raise ValueError(f"Starting string {repr(start)} was not found in text.")
	c1 = text[c0:].find(end)
	if c1 == -1:
		if not allow_eof:
			raise ValueError(f"Ending string {repr(end)} was not found in text.")
		return text[c0:]
	return text[c0:c0+c1]

