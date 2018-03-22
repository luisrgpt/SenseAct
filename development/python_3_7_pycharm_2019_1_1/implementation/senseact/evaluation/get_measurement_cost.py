from itertools import \
  repeat

def get_measurement_cost(
    chromosome,
    amount,
    settings,
):

  type_costs = (
    y
    for x in settings['probe']['types'].values()
    for y in repeat(x, amount)
  )

  measurement_cost = 0
  for flipped, type_cost in zip(chromosome, type_costs):
    if flipped:
      measurement_cost += type_cost

  return measurement_cost
