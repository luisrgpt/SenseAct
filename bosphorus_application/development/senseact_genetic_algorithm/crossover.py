from typing import \
  List
from random import \
  random, \
  randint

def crossover(
    chromosome_1: List[bool],
    chromosome_2: List[bool],
    minimum: int,
    maximum: int,
    probability: float
):
  random_event = random()
  if probability < random_event:
    return

  position = randint(minimum, maximum)
  chromosome_1[position:], chromosome_2[position:] = \
    chromosome_2[position:], chromosome_1[position:]
