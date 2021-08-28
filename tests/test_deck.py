# Quickly test the deck generator

import pandakota


lhs = pandakota.input.methods.LatinHypercubeSampling(400, 42)
deck = pandakota.input.Deck(functions=['f'], method=lhs)
n1 = pandakota.input.NormalUncertainVariable('nuv', 1.0, 0.05)
n2 = pandakota.input.NormalUncertainVariable(
	key='NormalVariable', mean=-1.234e6, std_dev=.00001
)
u = pandakota.input.UniformUncertainVariable('u', -3.33, 0.33)
input_vars = (n1, n2, u)
for _var in input_vars:
	deck.add_variable(_var)
deck.gradients = pandakota.input.derivatives.Gradients(
	gradient_type=pandakota.input.derivatives.DERIVATIVE_NUMERIC
)

REF_METHOD = """\
method
	id_method = "UQ"
	sampling
		sample_type = lhs
		seed = 42
		samples = 400
"""

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

REF_RESPONSES = """\
responses
	response_functions  1
	descriptors         f
	numerical_gradients
	no_hessians
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
	

def test_method_generation():
	assert deck._format_method() == REF_METHOD, \
		"Method generation test failed."


def test_variable_generation():
	assert deck._format_variables() == REF_VARIABLES, \
		"Variable generation test failed."


def test_response_generation():
	assert deck._format_responses() == REF_RESPONSES, \
		"Response function generation test failed."
