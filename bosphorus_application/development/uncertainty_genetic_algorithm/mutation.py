from uncertainty_math import Interval
from random import random

def mutation(
    chromosome: list,
    useful_probes_range: Interval,
    n_answer_intervals: int,
    mutation_probability_of_flipping_bit: float
):
  n_probes = sum(chromosome)

  for ((x_lower, x_open), (x_upper, x_closed)) in useful_probes_range:
    for n in range(x_lower, x_upper + 1):
      r = random()

      if not chromosome[n] and mutation_probability_of_flipping_bit * (
          n_probes + 1) / n_answer_intervals < r:
        chromosome[n] = True
      elif chromosome[n] and mutation_probability_of_flipping_bit * (
          1 - n_probes / n_answer_intervals) < r:
        chromosome[n] = False
