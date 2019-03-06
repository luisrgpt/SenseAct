from typing import \
  List
from senseact_genetic_algorithm import \
  generate, \
  evolve
from senseact_evaluation import \
  evaluate

def search(
    population_elite,
    minimum: int,
    maximum: int,
    probability_mass_function: List[float],
    cost_table,
    settings
):
  population = generate(
    population_elite=population_elite,
    minimum=minimum,
    maximum=maximum,
    settings=settings.genetic_algorithm.generate
  )
  population_fitness = evaluate(
    population=population,
    minimum=minimum,
    maximum=maximum,
    probability_mass_function=probability_mass_function,
    cost_table=cost_table,
    settings=settings.scenario
  )
  prev_best = min(population_fitness)
  stagnation_counter = 0
  while stagnation_counter < settings.genetic_algorithm.stopping_condition and \
      population_fitness[0] != 0:
    population = evolve(
      population=population,
      population_fitness=population_fitness,
      minimum=minimum,
      maximum=maximum,
      settings=settings.genetic_algorithm
    )
    population_fitness = evaluate(
      population=population,
      minimum=minimum,
      maximum=maximum,
      probability_mass_function=probability_mass_function,
      cost_table=cost_table,
      settings=settings.scenario
    )
    # Update test
    next_best = min(population_fitness)
    stagnation_counter = 0 if next_best < prev_best else stagnation_counter
    stagnation_counter += 1
    prev_best = next_best

  population = [
    population[x]
    for x, _ in sorted(enumerate(population_fitness), key=lambda x: x[1])
  ]
  population_elite[:] = population[:len(population_elite)]
