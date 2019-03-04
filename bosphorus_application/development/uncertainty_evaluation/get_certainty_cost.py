from uncertainty_math import intersects

def get_certainty_cost(
    certainty,
    alert_catalog,
    cost_table,
    next_unit_time,
    trajectory_speed
):
  certainty_cost = 0
  for certainty_interval, partial_certainty_probability in certainty:
    # Get alert cost
    alert_cost = next(
      alert_cost
      for alert_interval, alert_cost in alert_catalog
      if intersects(certainty_interval, alert_interval)
    )
    certainty_cost += partial_certainty_probability * alert_cost

    # Get wait cost
    certainty_interval[0][0] -= trajectory_speed
    certainty_interval[1][0] += trajectory_speed
    wait_cost = cost_table[(next_unit_time, certainty_interval)][0][1]
    certainty_cost += partial_certainty_probability * wait_cost

  return certainty_cost
