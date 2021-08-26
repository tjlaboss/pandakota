# Test reading and writing things related to the cantilever UQ LHS problem


import os

import functions
import pandakota
import pandas as pd
from assets import CANTILEVER_UQ_LHS


DAKOTA_OUT_PATH = os.path.join(CANTILEVER_UQ_LHS, "cantilever_uq_lhs.out")
with open(DAKOTA_OUT_PATH, 'r') as _f:
	TEXT = _f.read()


def _test_df(f, ref_csv, description):
	df = f(TEXT)
	df_ref = pd.read_csv(os.path.join(CANTILEVER_UQ_LHS, "ref", ref_csv), index_col=0)
	unequal, msg = functions.compare_dfs(df, df_ref)
	assert not unequal, f"{description} test failed: {msg}"


def test_read_pearson():
	_test_df(pandakota.reader.read_pearson_matrix, "ppcc.csv", "Pearson")


def test_read_spearman():
	_test_df(pandakota.reader.read_spearman_matrix, "sprcc.csv", "Spearman")


def test_read_moment():
	_test_df(pandakota.reader.read_moment_statistics, "ms.csv", "Moment Statistics")


def test_read_confidence():
	_test_df(pandakota.reader.read_confidence_intervals, "ci.csv", "Confidence Intervals")
