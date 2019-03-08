from typing import \
  List
from random import \
  random

def mutate(
    chromosome: List[bool],
    probability: float,
    flip_probability: float
):
  random_event = random()
  if probability < random_event:
    return

  flipped_size = sum(chromosome)
  size = len(chromosome)
  flip_true_probability = flip_probability * (flipped_size + 1) / size
  flip_false_probability = flip_probability * (1 - flipped_size / size)

  for position, gene in enumerate(chromosome):
    random_event = random()

    chromosome[position] = \
      True if not gene and flip_true_probability < random_event else \
        False if gene and flip_false_probability < random_event else \
          gene
