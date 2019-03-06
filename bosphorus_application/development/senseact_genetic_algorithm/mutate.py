from typing import \
  List
from random import \
  random

def mutate(
    chromosome: List[bool],
    minimum: int,
    maximum: int,
    probability: float,
    flip_probability: float
):
  random_event = random()
  if probability < random_event:
    return

  flipped_size = sum(chromosome)
  useful_size = maximum - minimum
  flip_true_probability = flip_probability * (flipped_size + 1) / useful_size
  flip_false_probability = flip_probability * (1 - flipped_size / useful_size)

  for position in range(minimum, maximum + 1):
    random_event = random()
    gene = chromosome[position]

    chromosome[position] = \
      True if not gene and flip_true_probability < random_event else \
        False if gene and flip_false_probability < random_event else \
          gene
