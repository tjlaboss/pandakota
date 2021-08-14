"""
output

Read things from DAKOTA output files
"""
import pandas as pd
from . import utils


PPCC = "pearson"
SPRCC = "spearman"

NAMES = {
	PPCC: "Partial Correlation Coefficient",
	SPRCC: "Partial Rank Correlation Coefficient",
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

