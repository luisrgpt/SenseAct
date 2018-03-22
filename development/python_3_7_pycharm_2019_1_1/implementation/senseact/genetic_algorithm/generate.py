from random import \
  random

def generate(
    population_elite,
    boundaries,
    amount: int,
    settings
):
  minimum, maximum = boundaries

  population_empty = {
    len(settings['chromosome']['types']) * amount * (False,),
  }
  population_random = set()
  for _ in range(len(population_elite) + 1, max(settings['population']['elite_size'] + 1, int((maximum - minimum) * settings['population']['size_ratio']))):

    # Generate random nucleus
    chromosome = ()
    for _, chromosome_initial_size in settings['chromosome']['types'].items():
      gene_probability = chromosome_initial_size / amount
      # Create random chromosome
      chromosome += tuple(random() <= gene_probability for _ in range(amount))

    population_random.add(chromosome)

  population = population_elite | population_empty | population_random

  return population
