from .crossover import crossover
from .generation import generation
from .mutation import mutation

from uncertainty_math import Interval
from uncertainty_evaluation import evaluation

from random import random
from math import log
from copy import deepcopy

def search(
    t_answer_intervals: tuple,
    time: int,
    cost_table: dict,
    max_size_of_population: int,
    elite_chromosomes: int,
    selection_max_number_of_fit_chromosomes: int,
    boundaries: tuple,
    alert_catalog: list,
    trajectory_speed: float,
    mutation_probability_of_flipping_bit: float,
    stopping_condition: float,
    generation_number_of_initial_probes: list,
    sensor_catalog: dict,

    selection_base_logarithm: float,
    crossover_probability_of_crossover: float,
    mutation_probability_of_mutation: float,

    elite: list,

    sensor_success_rate_area: dict,
    byzantine_fault_tolerance: int
):
  next_unit_time = time - 1
  answer_intervals, g_answer_intervals = t_answer_intervals

  n_boundaries = boundaries[1][0] - boundaries[0][0]
  n_genes = n_boundaries + 1
  n_answer_intervals = answer_intervals[1][0] - answer_intervals[0][0]

  boundaries_distributions = [[0] * n_boundaries for _ in
                              enumerate(g_answer_intervals)]
  for x, ((g_lower, _), (g_upper, _)) in enumerate(g_answer_intervals):
    pb_dist = 1 / (g_upper - g_lower)
    for y in range(g_lower, g_upper):
      boundaries_distributions[x][y] = pb_dist

  (answer_intervals_lower, _), (answer_intervals_upper, _) = answer_intervals
  i_boundaries = Interval([boundaries])
  useful_probes_range = Interval([x for x, _ in alert_catalog])
  useful_probes_range &= Interval([(
    (answer_intervals_lower - (time - 1), False),
    (
      answer_intervals_upper + (time - 1), True))])
  useful_probes_range = {
    u: (useful_probes_range + (0, u - 1)) & i_boundaries
    for u, _ in generation_number_of_initial_probes
  }
  n_useful_probes = {
    u: useful_probes_range[u].size() + len(useful_probes_range[u]) for u, _ in
    generation_number_of_initial_probes}

  dynamic_fitness = {}

  zero_probes = [
    [(u, [False] * n_genes) for u, _ in generation_number_of_initial_probes]]

  # Generate and evaluate
  pool = [
           [(u,
             generation(useful_probes_range[u], n_genes, n, n_useful_probes[u]))
            for u, n in generation_number_of_initial_probes]
           for _ in range(max_size_of_population - len(elite) - 1)
         ] + elite + deepcopy(zero_probes)
  fitness = []
  for nucleus in pool:
    fitness_key = tuple(
      (u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in
      nucleus)
    if fitness_key not in dynamic_fitness:
      dynamic_fitness[fitness_key] = evaluation(
        next_unit_time=next_unit_time,
        cost_table=cost_table,
        alert_catalog=alert_catalog,
        trajectory_speed=trajectory_speed,
        nucleus=nucleus,
        sensor_catalog=sensor_catalog,
        problem=(answer_intervals, boundaries_distributions[-1])
      )
    fitness += [dynamic_fitness[fitness_key]]

  # Select
  pool = [pool[x] for x, _ in sorted(enumerate(fitness), key=lambda x: x[1])]
  fitness.sort()

  # Update test
  prev_best = fitness[selection_max_number_of_fit_chromosomes - 1]
  stagnation_counter = 0

  # Test
  while stagnation_counter < stopping_condition and fitness[0] != 0:
    old_pool = pool

    pool = pool[:selection_max_number_of_fit_chromosomes]
    for _ in range(selection_max_number_of_fit_chromosomes,
                   max_size_of_population, 2):
      # Select
      nucleus1 = deepcopy(old_pool[
                            min(-int(log(random(), selection_base_logarithm)),
                                len(old_pool))])
      nucleus2 = deepcopy(old_pool[
                            min(-int(log(random(), selection_base_logarithm)),
                                len(old_pool))])

      for (y, _), useful_probes in zip(enumerate(nucleus1),
                                       useful_probes_range.values()):
        # Crossover
        if random() < crossover_probability_of_crossover:
          crossover(nucleus1[y][1], nucleus2[y][1])

        # Mutation
        if random() < mutation_probability_of_mutation:
          mutation(nucleus1[y][1], useful_probes, n_answer_intervals,
                   mutation_probability_of_flipping_bit)
          mutation(nucleus2[y][1], useful_probes, n_answer_intervals,
                   mutation_probability_of_flipping_bit)

      # Accept
      pool += [nucleus1, nucleus2]

    # Evaluate
    fitness = []
    for nucleus in pool:
      fitness_key = tuple(
        (u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in
        nucleus)
      if fitness_key not in dynamic_fitness:
        dynamic_fitness[fitness_key] = evaluation(
          next_unit_time=next_unit_time,
          cost_table=cost_table,
          alert_catalog=alert_catalog,
          trajectory_speed=trajectory_speed,
          nucleus=nucleus,
          sensor_catalog=sensor_catalog,
          problem=(answer_intervals, boundaries_distributions[-1])
        )
      fitness += [dynamic_fitness[fitness_key]]

    # Select
    pool = [pool[x] for x, _ in sorted(enumerate(fitness), key=lambda x: x[1])]
    fitness.sort()

    # Update test
    next_best = fitness[selection_max_number_of_fit_chromosomes - 1]
    if prev_best == next_best:
      stagnation_counter += 1
      fitness_key = tuple(
        (u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in
        pool[selection_max_number_of_fit_chromosomes - 1])
    else:
      stagnation_counter = 0
    prev_best = next_best

  elite[:] = pool[:elite_chromosomes]

  for x in g_answer_intervals:
    cost_table[(time, x)] = []

  for nucleus in elite:
    results = evaluation(
      next_unit_time=next_unit_time,
      cost_table=cost_table,
      alert_catalog=alert_catalog,
      trajectory_speed=trajectory_speed,
      nucleus=nucleus,
      sensor_catalog=sensor_catalog,
      problem=(g_answer_intervals, boundaries_distributions),
    )
    comb = [(u, [pos for pos, cond in enumerate(comb) if cond]) for u, comb in
            nucleus]
    for x, y in zip(g_answer_intervals, results):
      cost_table[(time, x)] += [(comb, y)]
