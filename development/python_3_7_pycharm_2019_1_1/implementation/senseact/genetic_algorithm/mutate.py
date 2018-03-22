from random import \
  random

def mutate(
    chromosome,
    flip_probability: float
):
  flipped_size = sum(chromosome,)
  size = len(chromosome,)

  enumerated_chromosome = list(enumerate(chromosome,),)
  #shuffle(enumerated_chromosome,)
  for position, gene in enumerated_chromosome:
    random_event = random()

    flip_true_probability = flip_probability * (flipped_size + 1) / size
    flip_false_probability = flip_probability * (1 - flipped_size / size)

    if not gene and random_event <= flip_true_probability:
      chromosome = chromosome[:position] + (True,) + chromosome[position + 1:]
      flipped_size += 1

    if gene and random_event <= flip_false_probability:
      chromosome = chromosome[:position] + (False,) + chromosome[position + 1:]
      flipped_size -= 1

  return chromosome
