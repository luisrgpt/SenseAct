from senseact.evaluation import \
  evaluate
from senseact.genetic_algorithm import \
  search

no_probe = (False,)

def fill_cost_table(
    cost_table: dict,
    time: int,
    proximity_groups,
    extrapolation_groups: dict,
    settings
):
  current_cost_table = cost_table[time - 1]
  largest_range = max(settings['scenario']['probe']['types'])
  len_probe_types = len(settings['scenario']['probe']['types'])
  for proximity_group in proximity_groups:

    common_minimum = proximity_group[0][0] == proximity_group[-1][0]

    population = {()}
    chromosome_length = 0
    for minimum, maximum in proximity_group:

      extended_minimum = max(minimum - largest_range, settings['scenario']['boundaries'][0])
      extended_maximum = min(maximum + largest_range, settings['scenario']['boundaries'][1])

      amount = int((extended_maximum - extended_minimum) / settings['scenario']['scale']) + 1

      middle = int(chromosome_length / len_probe_types)
      difference = no_probe * (amount - middle)
      chromosome_length = amount * len_probe_types

      population_elite = set()
      if common_minimum:
        for chromosome in population:
          chromosome_elite = ()
          for x in range(len_probe_types):
            chromosome_elite += chromosome[x * middle:(x + 1) * middle] + difference
          population_elite.add(chromosome_elite)

      else:
        for chromosome in population:
          chromosome_elite = ()
          for x in range(len_probe_types):
            chromosome_elite += difference + chromosome[x * middle:(x + 1) * middle]
          population_elite.add(chromosome_elite)

      population = search(
        population_elite=population_elite,
        boundaries=(minimum, maximum),
        extended_boundaries=(extended_minimum, extended_maximum),
        amount=amount,
        cost_table=current_cost_table,
        settings=settings,
      )

      middle = amount
      for similar_minimum, similar_maximum in extrapolation_groups[minimum, maximum]:

        difference_minimum = no_probe * int(extended_minimum - settings['scenario']['boundaries'][0])
        difference_maximum = no_probe * int(settings['scenario']['boundaries'][1] - extended_maximum)

        amount = int((settings['scenario']['boundaries'][1] - settings['scenario']['boundaries'][0]) / settings['scenario']['scale']) + 1

        population_elite = set()
        for chromosome in population:
          chromosome_elite = ()
          for x in range(len_probe_types):
            chromosome_elite += difference_minimum + chromosome[x * middle:(x + 1) * middle] + difference_maximum
          population_elite.add(chromosome_elite)

        population_fitness = evaluate(
          population=population_elite,
          boundaries=(similar_minimum, similar_maximum),
          extended_boundaries=settings['scenario']['boundaries'],
          amount=amount,
          cost_table=current_cost_table,
          settings=settings['scenario'],
        )

        decayed_minimum = round(similar_minimum - settings['scenario']['target']['speed'], 12)
        decayed_maximum = round(similar_maximum + settings['scenario']['target']['speed'], 12)

        cost_table[time][similar_minimum, similar_maximum] = {
          **cost_table[time].setdefault((similar_minimum, similar_maximum), {}),
          **population_fitness,
        }

        if decayed_minimum < settings['scenario']['boundaries'][0]:
          cost_table[time][decayed_minimum, similar_maximum] = {
            **cost_table[time].setdefault((decayed_minimum, similar_maximum), {}),
            **population_fitness,
          }

        if settings['scenario']['boundaries'][1] < decayed_maximum:
          cost_table[time][similar_minimum, decayed_maximum] = {
            **cost_table[time].setdefault((similar_minimum, decayed_maximum), {}),
            **population_fitness,
          }

        if decayed_minimum < settings['scenario']['boundaries'][0] and settings['scenario']['boundaries'][
          1] < decayed_maximum:
          cost_table[time][decayed_minimum, decayed_maximum] = {
            **cost_table[time].setdefault((decayed_minimum, decayed_maximum), {}),
            **population_fitness,
          }

        if similar_minimum == 0.0:
          cost_table[time][-similar_minimum, similar_maximum] = {
            **cost_table[time].setdefault((-similar_minimum, similar_maximum), {}),
            **population_fitness,
          }

        if similar_maximum == 0.0:
          cost_table[time][similar_minimum, -similar_maximum] = {
            **cost_table[time].setdefault((similar_minimum, -similar_maximum), {}),
            **population_fitness,
          }

        if decayed_minimum < settings['scenario']['boundaries'][0] and similar_maximum == 0.0:
          cost_table[time][decayed_minimum, -similar_maximum] = {
            **cost_table[time].setdefault((decayed_minimum, -similar_maximum), {}),
            **population_fitness,
          }

        if similar_minimum == 0.0 and settings['scenario']['boundaries'][1] < decayed_maximum:
          cost_table[time][-similar_minimum, decayed_maximum] = {
            **cost_table[time].setdefault((-similar_minimum, decayed_maximum), {}),
            **population_fitness,
          }

        if similar_minimum == 0.0 and similar_maximum == 0.0:
          cost_table[time][-similar_minimum, -similar_maximum] = {
            **cost_table[time].setdefault((-similar_minimum, -similar_maximum), {}),
            **population_fitness,
          }

  for key in cost_table[time]:
    cost_table[time][key][()] = min(
      cost_table[time][key].values()
    )