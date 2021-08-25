# Assets
#
# Absolute paths to test assets


import os as _os

TEST_DIR = _os.path.dirname(_os.path.abspath(__file__))
CASE_DIR = _os.path.join(TEST_DIR, "cases")

CANTILEVER_UQ_LHS = _os.path.join(CASE_DIR, "cantilever_uq_lhs")
