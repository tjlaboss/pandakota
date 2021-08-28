"""Methods

DAKOTA Methods
"""

import abc
import os
import typing


class Method(abc.ABC):
	"""Abstract Base Class for all methods"""
	requires_gradients = False
	requires_hessians = False
	def __init__(self):
		self._id_method = self.__class__.__name__
		self._refinements: typing.List[int] = []
	
	def __str__(self):
		return self.to_string()
	
	@property
	def refinements(self):
		return self._refinements
	
	def add_refinement(self, refinement_samples: int):
		self._refinements.append(refinement_samples)
	
	@abc.abstractmethod
	def to_string(self) -> str:
		ret = "method"
		ret += f'\n\tid_method = "{self._id_method}"'
		return ret


class Sampling(Method):
	"""Abstract Base Class for all sampling methods"""
	sample_type = None
	def __init__(self, nsamples: int, seed: int):
		super().__init__()
		assert isinstance(nsamples, int) and nsamples > 0, "nsamples must be an integer > 0."
		assert isinstance(seed, int), "seed must be an integer"
		self._nsamples = nsamples
		self._seed = seed
		self._id_method = "UQ"
	
	@property
	def nsamples(self):
		return self._nsamples
	
	def to_string(self) -> str:
		ret = super().to_string()
		ret += "\n\tsampling"
		ret += f"\n\t\tsample_type = {self.sample_type}"
		ret += f"\n\t\tseed = {self._seed}"
		ret += f"\n\t\tsamples = {self._nsamples}"
		if self._refinements:
			ret += "\n\t\t\trefinement_samples = " + " ".join(([str(r) for r in self._refinements]))
		return ret


class MonteCarloSampling(Sampling):
	"""Random sampling"""
	sample_type = "random"
	def __init__(self, nsamples: int, seed: int):
		super().__init__(nsamples, seed)


class LatinHypercubeSampling(Sampling):
	"""LHS"""
	sample_type = "lhs"
	def __init__(self, nsamples: int, seed: int):
		super().__init__(nsamples, seed)
	
	def add_refinement(self, refinement_samples: int=None):
		if not self._refinements:
			allowed = self._nsamples
		else:
			allowed = 2*self._refinements[-1]
		if refinement_samples is None:
			refinement_samples = allowed
		if refinement_samples != allowed:
			raise ValueError("LHS Refinement Samples must be exactly double the previous number of samples.")
		return super().add_refinement(refinement_samples)


