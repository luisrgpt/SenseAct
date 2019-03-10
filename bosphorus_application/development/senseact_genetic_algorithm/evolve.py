from senseact_genetic_algorithm import \
  select, \
  crossover, \
  mutate

def evolve(
    population,
    population_fitness,
    settings
):
  population = [
    population[x]
    for x, _ in sorted(enumerate(population_fitness), key=lambda x: x[1])
  ]
  next_population = population[:settings.generate.saved_size]
  for _ in range(settings.generate.saved_size, settings.generate.size, 2):
    nuclei = 2 * [
      select(
        population=population,
        base_logarithm=settings.select.base_logarithm
      )
    ]
    for chromosome_type, chromosome_1, _, chromosome_2 in zip(*nuclei):
      crossover(
        chromosome_1=chromosome_1,
        chromosome_2=chromosome_2,
        probability=settings.crossover.probability
      )
      for chromosome in [chromosome_1, chromosome_2]:
        mutate(
          chromosome=chromosome,
          probability=settings.mutate.probability,
          flip_probability=settings.mutate.flip_probability,
        )
    next_population += nuclei
  return next_population
