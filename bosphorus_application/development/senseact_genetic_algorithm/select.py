from random import \
  random
from math import \
  log
from copy import \
  deepcopy

def select(
    population,
    base_logarithm: float
):
  return deepcopy(
    population[
      min(
        -int(log(random(), base_logarithm)),
        len(population)
      )
    ]
  )
