from senseact.evaluation import \
  evaluate
from senseact.genetic_algorithm.evolve import \
  evolve
from senseact.genetic_algorithm.generate import \
  generate

def search(
    population_elite,
    boundaries,
    extended_boundaries,
    amount: int,
    cost_table,
    settings,
):
  population = generate(
    population_elite=population_elite,
    boundaries=boundaries,
    amount=amount,
    settings=settings['genetic_algorithm']['generate'],
  )
  population_fitness = evaluate(
    population=population,
    boundaries=boundaries,
    extended_boundaries=extended_boundaries,
    amount=amount,
    cost_table=cost_table,
    settings=settings['scenario'],
  )
  prev_best = min(population_fitness)
  stagnation_counter = 0
  while stagnation_counter < settings['genetic_algorithm']['stopping_condition'] and prev_best != 0:
    population = evolve(
      population_fitness=population_fitness,
      settings=settings['genetic_algorithm'],
    )
    population_fitness = evaluate(
      population=population,
      boundaries=boundaries,
      extended_boundaries=extended_boundaries,
      amount=amount,
      cost_table=cost_table,
      settings=settings['scenario'],
    )
    # Update test
    next_best = min(population_fitness)
    stagnation_counter = 0 if next_best < prev_best else stagnation_counter + 1
    prev_best = next_best

  population = sorted(population_fitness, key=lambda x: population_fitness[x])

  return population[:settings['genetic_algorithm']['generate']['population']['elite_size']]
