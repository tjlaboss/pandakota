"""
output

Read things from DAKOTA output files
"""
import pandas as pd
from pandakota.reader import utils


PPCC = "pearson"
SPRCC = "spearman"
MS = "statistics"
CI = "confidence"

NAMES = {
	PPCC: "Partial Correlation Matrix",
	SPRCC: "Partial Rank Correlation Matrix",
	MS: "Sample moment statistics",
	CI: "95% confidence intervals"
}


def read_partial_matrix(text: str) -> pd.DataFrame:
	"""Read a partial correlation matrix

	Parameters:
	-----------
	stream: str
		Text of the partial matrix

	Returns:
	--------
	pd.DataFrame
		DF of the partial correlation matrix
	"""
	try:
		stream = utils.string_to_stream(text)
		df = pd.read_csv(stream, delim_whitespace=True, skiprows=1, index_col=0).T
		stream.close()
	except (ValueError, pd.errors.EmptyDataError) as e:
		raise type(e)(f"Could not obtain read partial matrix from text: {e}")
	return df


def read_pearson_matrix(text, autosnip=True):
	"""Read the Pearson Partial Correlation Matrix

	Parameter:
	----------
	text: str
		Text containing the partial matrix
	
	autosnip: bool; optional
		Whether to detect the start and end of the
		partial correlation matrix block using pandakota defaults.
		[Default: True]

	Returns:
	--------
	pd.DataFrame
		DF of the partial correlation matrix
	"""
	if autosnip:
		text = utils.snip_text(text, start=NAMES[PPCC])
	return read_partial_matrix(text).T


def read_spearman_matrix(text, autosnip=True):
	"""Read the Spearman Partial Rank Correlation Matrix

	Parameter:
	----------
	text: str
		Text containing the partial matrix
	
	autosnip: bool; optional
		Whether to detect the start and end of the
		partial correlation matrix block using pandakota defaults.
		[Default: True]

	Returns:
	--------
	pd.DataFrame
		DF of the partial rank correlation matrix
	"""
	if autosnip:
		text = utils.snip_text(text, start=NAMES[SPRCC])
	return read_partial_matrix(text).T


def read_moment_statistics(text, autosnip=True):
	"""Read the sample moment statistics

	Parameter:
	----------
	text: str
		Text containing the moment statistics

	autosnip: bool; optional
		Whether to detect the start and end of the
		moment statistics block using pandakota defaults.
		[Default: True]

	Returns:
	--------
	pd.DataFrame
		DF of Mean, StdDev, Skewness, Kurtosis
	"""
	if autosnip:
		text = utils.snip_text(text, start=NAMES[MS])
	text = text.replace("Std Dev", "StdDev")
	return read_partial_matrix(text)


def read_confidence_intervals(text, autosnip=True):
	"""Read the 95-95 confidence intervals

	Parameter:
	----------
	text: str
		Text containing the 95% confidence intervals

	autosnip: bool; optional
		Whether to detect the start and end of the
		confidence intervals block using pandakota defaults.
		[Default: True]

	Returns:
	--------
	pd.DataFrame
		DF of LowerCI_Mean, UpperCI_Mean, LowerCI_StdDev, UpperCI_StdDev
	"""
	if autosnip:
		text = utils.snip_text(text, start=NAMES[CI])
	return read_partial_matrix(text)


READERS = {
	PPCC:  read_pearson_matrix,
	SPRCC: read_spearman_matrix,
	MS:    read_moment_statistics,
	CI:    read_confidence_intervals,
}
