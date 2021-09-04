"""
Study

Module that runs and manages DAKOTA studies
"""

import pandakota.input


class Study:
	"""A DAKOTA study to be run
	
	Parameters:
	-----------
	deck: pandakota.input.Deck
	
	concurrency: int or None
		Level of concurrency
	
	asynchronous: bool
		Whether to
	"""
	def __init__(
			self,
			deck: pandakota.input.Deck,
			concurrency: int=None,
			asynchronous: bool=True,
	):
		self._deck = deck
		self.concurrency = concurrency
		self.asynchronous = asynchronous
	
	
	def run_dakota(self):
		"""Run the initial samples"""
		text = self._deck.get_deck()
		pass
	
	