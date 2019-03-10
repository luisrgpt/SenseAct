from senseact_math import \
  interval_range

def store_well_known_costs(
    cost_table,
    time,
    zones,
    settings
):
  excluded = []

  for zone, alert_cost in zones:
    for well_known_interval in interval_range(zone):
      well_known_interval[0][0] -= settings.target.speed
      well_known_interval[1][0] += settings.target.speed
      (_, wait_cost), *_ = cost_table[well_known_interval]
      cost_table[time, well_known_interval] = [([], wait_cost + alert_cost)]
      excluded += [well_known_interval]

  return excluded
