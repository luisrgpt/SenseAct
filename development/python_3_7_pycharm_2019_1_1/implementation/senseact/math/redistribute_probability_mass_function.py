from senseact.math import float_range

def redistribute_probability_mass_function(
  probability_mass_function: dict,
  incident_intervals,
  settings
):

  new_probability_mass_function = {
    position: 0.0
    for position in float_range(
      minimum=settings['boundaries'][0],
      maximum=settings['boundaries'][1] - settings['scale'],
      scale=settings['scale'],
    )
  }

  ratio = len(tuple(float_range(minimum=-settings['target']['speed'], maximum=settings['target']['speed'], scale=settings['scale'])))
  for (minimum, _), (maximum, _) in incident_intervals:
    for position in float_range(minimum=minimum, maximum=maximum - settings['scale'], scale=settings['scale']):

      a_fraction = round(probability_mass_function[position] / ratio, 12)
      remainder = 0.0
      for new_position in float_range(
        minimum=position - settings['target']['speed'],
        maximum=position + settings['target']['speed'] - settings['scale'],
        scale=settings['scale']
      ):

        new_position = max(
          new_position,
          settings['boundaries'][0]
        )
        new_position = min(
          new_position,
          settings['boundaries'][1] - settings['scale']
        )
        new_probability_mass_function[new_position] += a_fraction
        remainder += a_fraction

      new_position = position + settings['target']['speed']
      new_position = min(
        new_position,
        settings['boundaries'][1] - settings['scale']
      )
      new_probability_mass_function[new_position] += probability_mass_function[position] - remainder

  return new_probability_mass_function
