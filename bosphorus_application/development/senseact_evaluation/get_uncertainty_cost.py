from senseact_math import \
  intersects

def get_uncertainty_cost(
    uncertainty,
    cost_table,
    settings
):
  # Get alert cost from uncertainty and alert catalog
  alert_cost = next(
    alert_cost
    for alert_interval, alert_cost in settings.alert.types
    for partial_uncertainty_interval, _ in uncertainty
    if intersects(partial_uncertainty_interval, alert_interval)
  )
  total_uncertainty_probability = sum(
    partial_uncertainty_probability
    for _, partial_uncertainty_probability in uncertainty
  )
  uncertainty_cost = total_uncertainty_probability * alert_cost

  # Get wait cost from uncertainty, cost table, trajectory speed and next unit
  # time
  for uncertainty_interval, partial_uncertainty_probability in uncertainty:
    uncertainty_interval[0][0] -= settings.target.speed
    uncertainty_interval[1][0] += settings.target.speed
    (_, wait_cost), *_ = cost_table[uncertainty_interval]
    uncertainty_cost += partial_uncertainty_probability * wait_cost

  return uncertainty_cost
