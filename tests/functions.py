# Functions
#
# Useful testing functions
import pandas as pd
import numpy as np


def compare_dfs(df1: pd.DataFrame, df2: pd.DataFrame, ignore_index=False, **kwargs) -> [int, str]:
	if "equal_nan" not in kwargs:
		kwargs["equal_nan"] = True
	if df1.shape != df2.shape:
		return 4, f"DF shapes are unequal: {df1.shape} != {df2.shape}"
	if not ignore_index and any(df1.columns != df2.columns):
		return 3, f"DF columns are unequal: {df1.columns} != {df2.columns}"
	if not ignore_index and any(df1.index != df2.index):
		return 2, "DF indices are unequal."
	df_equal = pd.DataFrame(np.isclose(df1, df2, **kwargs), index=df1.index, columns=df1.columns)
	cols_equal = df_equal.all()
	if cols_equal.all():
		return 0, "The DFs are equal."
	unequal = df1.columns[~cols_equal]
	df3 = pd.DataFrame(index=df1.index)
	for col in unequal:
		df3[col + " (1)"] = df1[col]
		df3[col + " (2)"] = df2[col]
	return 1, f"The following columns are unequal:\n{unequal}\n{df3}"
	