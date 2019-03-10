from senseact_genetic_algorithm import \
  search
from senseact_evaluation import \
  evaluate

def multi_search(
    group,
    similar_intervals: dict,
    time: int,
    cost_table: dict,
    settings
):
  population = []
  for minimum, maximum in group:
    search(
      population=population,
      minimum=minimum,
      maximum=maximum,
      amount=maximum - minimum + 1,
      cost_table=cost_table,
      settings=settings
    )
    for similar_interval in similar_intervals[minimum, maximum]:
      ((minimum, not_left_bounded), (maximum, right_bounded)) = similar_interval
      useful_minimum = minimum + not_left_bounded
      useful_maximum = maximum - (not right_bounded)
      population_fitness = evaluate(
        population=population,
        minimum=useful_minimum,
        maximum=useful_maximum,
        amount=useful_maximum - useful_minimum + 1,
        cost_table=cost_table,
        settings=settings.scenario
      )
      cost_table[similar_interval] = []
      cost_table[time, similar_interval] = []
      for cost_table_value in zip(population, population_fitness):
        cost_table_value = [cost_table_value]
        cost_table[similar_interval] += cost_table_value
        cost_table[time, similar_interval] += cost_table_value
