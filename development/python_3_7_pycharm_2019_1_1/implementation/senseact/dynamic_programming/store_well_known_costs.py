from senseact.math.float_range import \
  float_range

def store_well_known_costs(
    cost_table,
    time,
    settings
):

  excluded = {}
  for (zone_minimum, zone_maximum), alert_cost in settings['alert']['types']:
    for minimum in float_range(minimum=zone_minimum, maximum=zone_maximum, scale=settings['scale']):

      decayed_minimum = round(minimum - settings['target']['speed'], 12)
      decayed_maximum = round(minimum + settings['target']['speed'], 12)
      wait_cost = cost_table[decayed_minimum, decayed_maximum][()]

      excluded_value = {
        (): wait_cost + alert_cost,
      }
      excluded[minimum, minimum] = excluded_value

      if minimum == settings['boundaries'][0]:
        excluded[decayed_minimum, minimum] = excluded_value

      if minimum == settings['boundaries'][1]:
        excluded[minimum, decayed_maximum] = excluded_value

      if minimum == 0.0:
        excluded[-minimum, -minimum] = excluded_value
        excluded[-minimum, minimum] = excluded_value

    for minimum in float_range(minimum=zone_minimum, maximum=zone_maximum - settings['scale'], scale=settings['scale']):

      maximum = minimum + settings['scale']

      decayed_minimum = round(minimum - settings['target']['speed'], 12)
      decayed_maximum = round(maximum + settings['target']['speed'], 12)
      wait_cost = cost_table[decayed_minimum, decayed_maximum][()]

      excluded_value = {
        (): wait_cost + alert_cost,
      }
      excluded[minimum, maximum] = excluded_value

      if decayed_minimum < settings['boundaries'][0]:
        excluded[decayed_minimum, maximum] = excluded_value

      if settings['boundaries'][1] < decayed_maximum:
        excluded[minimum, decayed_maximum] = excluded_value

      if decayed_minimum < settings['boundaries'][0] and settings['boundaries'][1] < decayed_maximum:
        excluded[decayed_minimum, decayed_maximum] = excluded_value

      if minimum == 0.0:
        excluded[-minimum, maximum] = excluded_value

      if maximum == 0.0:
        excluded[minimum, -maximum] = excluded_value

      if minimum == 0.0 and maximum == 0.0:
        excluded[-minimum, -maximum] = excluded_value

    decay = (time - 1) * settings['target']['speed']

    if settings['boundaries'][0] < zone_minimum:
      zone_minimum = round(zone_minimum + decay, 12)

    if zone_maximum < settings['boundaries'][1]:
      zone_maximum = round(zone_maximum - decay, 12)

    if zone_maximum <= zone_minimum:
      continue

    for minimum in float_range(minimum=zone_minimum, maximum=zone_maximum, scale=settings['scale']):
      for maximum in float_range(minimum=round(minimum + settings['scale'], 12), maximum=zone_maximum, scale=settings['scale']):

        decayed_minimum = round(minimum - settings['target']['speed'], 12)
        decayed_maximum = round(maximum + settings['target']['speed'], 12)
        wait_cost = cost_table[decayed_minimum, decayed_maximum][()]

        excluded_value = {
          (): wait_cost + alert_cost,
        }
        excluded[minimum, maximum] = excluded_value
        if decayed_minimum < settings['boundaries'][0]:
          excluded[decayed_minimum, maximum] = excluded_value

        if settings['boundaries'][1] < decayed_maximum:
          excluded[minimum, decayed_maximum] = excluded_value

        if decayed_minimum < settings['boundaries'][0] and settings['boundaries'][1] < decayed_maximum:
          excluded[decayed_minimum, decayed_maximum] = excluded_value

        if minimum == 0.0:
          excluded[-minimum, maximum] = excluded_value

        if maximum == 0.0:
          excluded[minimum, -maximum] = excluded_value

        if minimum == 0.0 and maximum == 0.0:
          excluded[-minimum, -maximum] = excluded_value

  return excluded
