from senseact.genetic_algorithm.mutate import \
  mutate
from senseact.genetic_algorithm.select import \
  select

def evolve(
    population_fitness,
    settings
):
  population = sorted(population_fitness, key=lambda x: population_fitness[x])
  next_population_size = len(population)
  next_population = set(population[:settings['generate']['population']['saved_size']])

  while len(next_population) < next_population_size:
    chromosome = select(
      population=population,
      base_logarithm=settings['select']['base_logarithm'],
    )
    chromosome = mutate(
      chromosome=chromosome,
      flip_probability=settings['mutate']['flip_probability'],
    )

    next_population.add(chromosome)

  return next_population
