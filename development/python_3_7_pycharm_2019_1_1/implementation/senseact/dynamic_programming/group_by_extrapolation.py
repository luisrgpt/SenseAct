from senseact.math.float_range import \
  float_range

def group_by_extrapolation(
    time,
    excluded,
    settings
):

  extrapolation_groups = {}
  for minimum in float_range(
      minimum=settings['boundaries'][0],
      maximum=settings['boundaries'][1],
      scale=settings['scale'],
  ):
    for maximum in float_range(
        minimum=minimum,
        maximum=settings['boundaries'][1],
        scale=settings['scale'],
    ):

      if (minimum, maximum) not in excluded:

        extrapolation_keys = None
        extrapolation_minimum = None
        extrapolation_cost = None
        extrapolation_zone = None

        for (zone_minimum, zone_maximum), alert_cost in settings['alert']['types']:

          decay = (time - 1) * settings['target']['speed']

          if settings['boundaries'][0] < zone_minimum:
            zone_minimum = round(zone_minimum + decay, 12)

          if zone_maximum < settings['boundaries'][1]:
            zone_maximum = round(zone_maximum - decay, 12)

          if zone_maximum <= zone_minimum:
            continue

          if zone_minimum <= minimum < zone_maximum:
            extrapolation_zone = (zone_minimum, zone_maximum)
            extrapolation_minimum = zone_maximum - settings['scale']
            extrapolation_cost = alert_cost
            break

        for (zone_minimum, zone_maximum), alert_cost in settings['alert']['types']:

          decay = (time - 1) * settings['target']['speed']

          if settings['boundaries'][0] < zone_minimum:
            zone_minimum = round(zone_minimum + decay, 12)

          if zone_maximum < settings['boundaries'][1]:
            zone_maximum = round(zone_maximum - decay, 12)

          if zone_maximum <= zone_minimum:
            continue

          if zone_minimum < maximum <= zone_maximum and extrapolation_zone != (zone_minimum, zone_maximum):

            extrapolation_maximum = zone_minimum + settings['scale']

            if extrapolation_cost is None:
              extrapolation_keys = (
                (minimum, extrapolation_maximum),
              )

            elif extrapolation_cost == alert_cost:
              extrapolation_keys = (
                (extrapolation_minimum, extrapolation_maximum),
              )

            else:
              extrapolation_keys = (
                (extrapolation_minimum, maximum),
                (minimum, extrapolation_maximum),
              )

            break

        if not extrapolation_keys:
          extrapolation_keys = (
            (minimum, maximum),
          )

        for extrapolation_key in extrapolation_keys:

          extrapolation_groups.setdefault(extrapolation_key, ())

          if (minimum, maximum) in extrapolation_groups[extrapolation_key]:
            continue

          extrapolation_groups[extrapolation_key] += (
            (minimum, maximum),
          )

  return extrapolation_groups
