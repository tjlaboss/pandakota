# Quickly test the deck generator

import pandakota


deck = pandakota.input.Deck()
n1 = pandakota.input.NormalUncertainVariable('nuv', 1.0, 0.05)
n2 = pandakota.input.NormalUncertainVariable(
	key='NormalVariable', mean=-1.234e6, std_dev=.00001
)
u = pandakota.input.UniformUncertainVariable('u', -3.33, 0.33)
input_vars = (n1, n2, u)
for _var in input_vars:
	deck.add_variable(_var)

REF_VARIABLES = """\
variables

	normal_uncertain  2
		descriptors     "nuv"   "NormalVariable"
		means            1.0     -1234000.0
		std_deviations   0.05    1e-05

	uniform_uncertain  1
		descriptors     "u"
		lower_bounds     -3.33
		upper_bounds     0.33
"""

def test_variables():
	for var in input_vars:
		assert deck[var.key] is var
	for descriptor, var in deck.items():
		assert var in input_vars
	assert deck.get('Z~Z') is None


def test_invalid_variable_name():
	badboy = pandakota.input.StateVariable("boy ain't good", str, "b")
	try:
		deck.add_variable(badboy)
	except AssertionError:
		pass
	else:
		raise AssertionError("Failed to catch bad variable name.")


def test_wrong_variable_type():
	try:
		pandakota.input.StateVariable("badgirl", int, "bee")
	except TypeError:
		pass
	else:
		raise AssertionError("Failed to catch wrong variable type.")


def test_variable_generation():
	assert deck._format_variables() == REF_VARIABLES, \
		"Variable generation test failed."
