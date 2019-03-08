from typing import \
  List
from senseact_genetic_algorithm import \
  generate, \
  evolve
from senseact_evaluation import \
  evaluate

def search(
    population,
    minimum: int,
    maximum: int,
    amount: int,
    cost_table,
    settings,
    probability_mass_function: List[float] = None,
):
  population = generate(
    population=population,
    minimum=minimum,
    maximum=maximum,
    amount=amount,
    settings=settings.genetic_algorithm.generate
  )
  population_fitness = evaluate(
    population=population,
    minimum=minimum,
    maximum=maximum,
    amount=amount,
    cost_table=cost_table,
    settings=settings.scenario,
    probability_mass_function=probability_mass_function
  )
  prev_best = min(population_fitness)
  stagnation_counter = 0
  while stagnation_counter < settings.genetic_algorithm.stopping_condition and \
      population_fitness[0] != 0:
    population = evolve(
      population=population,
      population_fitness=population_fitness,
      settings=settings.genetic_algorithm
    )
    population_fitness = evaluate(
      population=population,
      minimum=minimum,
      maximum=maximum,
      cost_table=cost_table,
      settings=settings.scenario,
      probability_mass_function=probability_mass_function
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
  population[:] = \
    population[:settings.genetic_algorithm.generate.population.elite_size]
