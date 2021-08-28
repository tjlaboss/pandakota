"""Test the Study class"""
import io
import sys
import shutil
import pandakota

mc = pandakota.input.methods.MonteCarloSampling(100, 42)
deck = pandakota.input.Deck(functions=['f'], method=mc)
deck.add_variable(pandakota.input.NormalUncertainVariable('x', +1.0, 0.05))
deck.add_variable(pandakota.input.NormalUncertainVariable('y', -1.0, 0.07))


class FileIO(io.StringIO):
	def __init__(self, number, *args, **kwargs):
		self.number = number
		super().__init__(*args, **kwargs)
		
	def fileno(self) -> int:
		return self.number


def test_echo():
	sys.stdout = FileIO(1)
	stu = pandakota.Study(deck, bin_path="echo", workdir=".test_echo/")
	stu.run_dakota()
	solution = "# Usage:\n#   echo -i dak.in -o dak.out -write_restart Restart0.rst"
	with open(f"{stu._dakota_dir}/dak.in", 'r') as fin:
		text = fin.read()
	assert solution in text, "echo test failed"
	shutil.rmtree(stu._workdir)
