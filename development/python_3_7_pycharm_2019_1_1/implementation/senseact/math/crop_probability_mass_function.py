from senseact.math.float_range import \
  float_range

def crop_probability_mass_function(
  probability_mass_function,
  interval,
  settings,
):

  new_positions = []
  for (minimum, _), (maximum, _) in interval:
    if minimum == maximum:
      new_positions += \
        [minimum] if settings['boundaries'][0] <= minimum else \
        [minimum - settings['scale']] if minimum <= settings['boundaries'][1] else \
        [minimum - settings['scale'], minimum]
    else:
      for position in float_range(minimum=minimum, maximum=maximum - settings['scale'], scale=settings['scale']):
        new_positions += [position]

  new_probability_mass_function = {
    position: 0.0
    for position in float_range(
      minimum=settings['boundaries'][0],
      maximum=settings['boundaries'][1] - settings['scale'],
      scale=settings['scale'],
    )
  }

  conditional_event_probability = round(
    sum(
      probability_mass_function[position]
      for position in new_probability_mass_function
    ),
    12,
  )

  # Get conditional probabilities
  total_probability = 0.0
  for position in new_positions:

    new_probability_mass_function[position] = round(probability_mass_function[position] / conditional_event_probability, 12)
    total_probability += new_probability_mass_function[position]

  current_total = round(total_probability, 10)

  # Adjust probabilities so that the sum of all possible probabilities is 1
  while not 0.99 < current_total < 1.01:

    missing_probability = 1.0 - current_total
    total_probability = 0.0
    for position in new_positions:
      new_probability_mass_function[position] += round(missing_probability * new_probability_mass_function[position], 12)
      total_probability += new_probability_mass_function[position]
    current_total = round(total_probability, 10)

  return new_probability_mass_function