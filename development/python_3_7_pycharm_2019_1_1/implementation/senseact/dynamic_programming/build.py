from time import \
  time as get_time

from senseact.dynamic_programming.fill_cost_table import \
  fill_cost_table
from senseact.dynamic_programming.group_by_extrapolation import \
  group_by_extrapolation
from senseact.dynamic_programming.group_by_proximity import \
  group_by_proximity
from senseact.dynamic_programming.store_well_known_costs import \
  store_well_known_costs
from senseact.math.float_range import \
  float_range

def build(
    settings
):

  decayed_boundary_minimum = round(settings['scenario']['boundaries'][0] - settings['scenario']['target']['speed'], 12)
  decayed_boundary_maximum = round(settings['scenario']['boundaries'][1] + settings['scenario']['target']['speed'], 12)
  cost_table = {
    0: {
      (x, y): {
        (): 0,
      }
      for x in float_range(
        minimum=decayed_boundary_minimum,
        maximum=decayed_boundary_maximum,
        scale=settings['scenario']['scale'],
      )
      for y in float_range(
        minimum=x if settings['scenario']['boundaries'][0] != x else decayed_boundary_minimum,
        maximum=decayed_boundary_maximum,
        scale=settings['scenario']['scale'],
      )
    },
  }

  performance_table = []

  for time in range(1, settings['scenario']['time'] + 1):

    start = get_time()

    cost_table[time] = store_well_known_costs(
      cost_table=cost_table[time - 1],
      time=time,
      settings=settings['scenario'],
    )
    extrapolation_groups = group_by_extrapolation(
      time=time,
      excluded=cost_table[time],
      settings=settings['scenario'],
    )
    proximity_groups = group_by_proximity(
      extrapolation=extrapolation_groups,
    )
    fill_cost_table(
      cost_table=cost_table,
      time=time,
      proximity_groups=proximity_groups,
      extrapolation_groups=extrapolation_groups,
      settings=settings,
    )

    end = get_time()
    print((time, end - start))
    performance_table += [(time, end - start)]

  return cost_table, performance_table
