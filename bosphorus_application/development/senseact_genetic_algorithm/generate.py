from random import \
  random

def generate(
    population,
    minimum: int,
    maximum: int,
    amount: int,
    settings
):
  chromosome_size = maximum - minimum

  population_empty = [
    [
      (chromosome_type, amount * [False])
      for chromosome_type, _ in settings.chromosome.types
    ]
  ]
  population_random = []
  for _ in range(settings.population.elite_size + 1, settings.population.size):
    # Generate random nucleus
    nucleus = []
    for chromosome_type, chromosome_initial_size in settings.chromosome.types:
      gene_probability = chromosome_initial_size / chromosome_size
      # Create random chromosome
      chromosome_genes = [random() < gene_probability for _ in range(amount)]
      chromosome = (chromosome_type, chromosome_genes)

      nucleus += [chromosome]
    population_random += [nucleus]
  population += population_empty + population_random
  return population
