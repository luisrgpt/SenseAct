from senseact_math import \
  intersects

def get_certainty_cost(
    certainty,
    cost_table,
    settings
):
  certainty_cost = 0
  for certainty_interval, partial_certainty_probability in certainty:
    # Get alert cost
    alert_cost = next(
      alert_cost
      for alert_interval, alert_cost in settings.alert.types
      if intersects(certainty_interval, alert_interval)
    )
    certainty_cost += partial_certainty_probability * alert_cost
    # Get wait cost
    certainty_interval[0][0] -= settings.target.speed
    certainty_interval[1][0] += settings.target.speed
    (_, wait_cost), *_ = cost_table[certainty_interval]
    certainty_cost += partial_certainty_probability * wait_cost
  return certainty_cost
