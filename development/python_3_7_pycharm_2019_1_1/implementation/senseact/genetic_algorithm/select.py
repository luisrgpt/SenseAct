from math import \
  log
from random import \
  random

def select(
    population,
    base_logarithm: float,
):
  return population[
    min(
      -int(log(random(), base_logarithm,),),
      len(population,) - 1
    )
  ]
