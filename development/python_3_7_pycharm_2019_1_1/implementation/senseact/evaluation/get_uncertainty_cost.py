def get_uncertainty_cost(
    uncertainty,
    cost_table,
    settings,
):

  # Get alert cost from uncertainty and alert catalog
  alert_cost = next(
    alert_cost
    for (alert_minimum, alert_maximum), alert_cost in settings['alert']['types']
    for (minimum, maximum), _ in uncertainty
    if minimum < alert_maximum and alert_minimum < maximum
  )
  total_uncertainty_probability = sum(
    partial_uncertainty_probability
    for _, partial_uncertainty_probability in uncertainty
  )
  uncertainty_cost = total_uncertainty_probability * alert_cost

  # Get wait cost from uncertainty, cost table, trajectory speed and next unit time
  for (minimum, maximum), partial_uncertainty_probability in uncertainty:

    minimum = round(minimum - settings['target']['speed'], 12)
    maximum = round(maximum + settings['target']['speed'], 12)
    wait_cost = cost_table[minimum, maximum][()]
    uncertainty_cost += partial_uncertainty_probability * wait_cost

  return uncertainty_cost
