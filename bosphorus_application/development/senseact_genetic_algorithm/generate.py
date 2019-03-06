from random import \
  random

def generate(
    population_elite,
    minimum: int,
    maximum: int,
    settings
):
  chromosome_useful_size = maximum - minimum

  population_empty = [
    [
      (chromosome_type, [False] * settings.chromosome.size)
      for chromosome_type, _ in settings.chromosome.types
    ]
  ]
  population_random = []
  for _ in range(settings.population.elite_size + 1, settings.population.size):
    # Generate random nucleus
    nucleus = []
    for chromosome_type, chromosome_initial_size in settings.chromosome.types:
      chromosome_minimum = minimum - chromosome_type
      chromosome_maximum = maximum - chromosome_type
      gene_probability = chromosome_initial_size / chromosome_useful_size
      # Create random chromosome
      chromosome_genes = [
        chromosome_minimum <= gene <= chromosome_maximum and
        random() < gene_probability
        for gene in range(settings.chromosome.size)
      ]
      chromosome = (chromosome_type, chromosome_genes)

      nucleus += [chromosome]
    population_random += [nucleus]
  return population_elite + population_empty + population_random
