from typing import \
  List
from random import \
  random, \
  randrange

def crossover(
    chromosome_1: List[bool],
    chromosome_2: List[bool],
    probability: float
):
  random_event = random()
  if probability < random_event:
    return

  chromosome_size = len(chromosome_1)
  position = randrange(chromosome_size)
  chromosome_1[position:], chromosome_2[position:] = \
    chromosome_2[position:], chromosome_1[position:]
