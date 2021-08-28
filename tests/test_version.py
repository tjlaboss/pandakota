from pandakota import __version__, __version_info__

def test_version():
	assert isinstance(__version__, str)
	assert isinstance(__version_info__, tuple)
	for i, v in enumerate(__version__.split('.')):
		assert int(v) == __version_info__[i]
