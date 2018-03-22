def get_certainty_cost(
    certainty,
    cost_table,
    settings,
):

  certainty_cost = 0
  for (minimum, maximum), partial_certainty_probability in certainty:

    # Get alert cost
    alert_cost = next(
      alert_cost
      for (alert_minimum, alert_maximum), alert_cost in settings['alert']['types']
      if minimum < alert_maximum and alert_minimum < maximum
    )
    certainty_cost += partial_certainty_probability * alert_cost

    # Get wait cost
    minimum = round(minimum - settings['target']['speed'], 12)
    maximum = round(maximum + settings['target']['speed'], 12)
    wait_cost = cost_table[minimum, maximum][()]
    certainty_cost += partial_certainty_probability * wait_cost

  return certainty_cost
