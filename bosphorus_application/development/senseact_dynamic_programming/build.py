from senseact_dynamic_programming import \
  group_by_extrapolation, \
  group_by_proximity, \
  multi_search, \
  save_cost_table, \
  save_groupings, \
  save_readable_cost_table, \
  store_well_known_costs
from senseact_math import \
  Interval, \
  intersects
import time as \
  timer

def build(
    settings
):
  start = timer.time()

  cost_table = {
    x: [('', 0)]
    for x in Interval([settings.scenario.boundaries]).range()
  }

  (b_left, b_right) = settings.scenario.boundaries
  not_alert = [(x, 0) for x in ~Interval([x for x, _ in settings.alert.types])]
  alert_partitions = settings.scenario.alert.settings + not_alert
  useless_partitions = alert_partitions[:]
  useful_partitions = settings.scenario.alert.settings[:]
  for time in range(1, settings.dynamic_programming.time + 1):
    excluded = store_well_known_costs(
      cost_table=cost_table,
      time=time,
      zones=alert_partitions,
      settings=settings.scenario
    )
    extrapolation_groups = group_by_extrapolation(
      excluded=excluded,
      useless_partitions=useless_partitions
    )
    proximity_groups = group_by_proximity(
      groups=extrapolation_groups
    )
    end = timer.time()
    print('Dynamic Performance: ' + str(end - start))
    save_groupings(proximity_groups, extrapolation_groups, time)
    start = timer.time()

    for proximity_group in proximity_groups:
      multi_search(
        group=proximity_group,
        similar_intervals=extrapolation_groups,
        time=time,
        cost_table=cost_table,
        settings=settings
      )

    end = timer.time()
    print('Genetic Performance: ' + str(end - start))
    start = timer.time()
    save_readable_cost_table(cost_table, time)
    for x, _ in enumerate(useful_partitions):
      ((x_lower, x_open), (x_upper, x_closed)), x_cost = useful_partitions[x]
      x_range = (max((x_lower - target_settings, x_open), b_left),
                 min((x_upper + target_settings, x_closed), b_right))
      useful_partitions[x] = (x_range, x_cost)

      (x_left, x_right) = x_range
      deleted = 0
      for y in range(len(useless_partitions)):
        y -= deleted
        y_range, y_cost = useless_partitions[y]
        if y_cost < x_cost:
          (y_left, y_right) = y_range
          if x_right <= y_right and intersects(x_range, y_range):
            y_left = x_right
            useless_partitions[y] = ((y_left, y_right), y_cost)
          if y_left <= x_left and intersects(x_range, y_range):
            y_right = x_left
            useless_partitions[y] = ((y_left, y_right), y_cost)
          if x_left <= y_left and y_right <= x_right:
            del useless_partitions[y]
            deleted += 1
  save_cost_table(cost_table)

  return cost_table
