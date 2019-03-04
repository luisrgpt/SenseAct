from uncertainty_math import Interval
from random import random

def generation(
    useful_probes_range: Interval,
    n_genes: int,
    generation_number_of_initial_probes: int,
    n_useful_probes: int
):
  pb_gen = generation_number_of_initial_probes / n_useful_probes
  return [
    x in useful_probes_range and random() < pb_gen
    for x in range(n_genes)
  ]
