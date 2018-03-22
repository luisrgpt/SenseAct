from senseact.math import float_range

def get_answers_non_uniform(
    claims,
    boundaries,
    probability_mass_function: dict,
    settings,
):

  minimum, maximum = boundaries

  claims[minimum] = claims.setdefault(minimum, 0)
  claims[maximum] = claims.setdefault(maximum, -1)

  # Store initial settings from claims for the following iteration
  (previous_position, previous_claim), *claims = sorted(claims.items())

  # Get certainties and uncertainties from claims
  certainty = list()
  uncertainty = list()
  for position, claim in claims:

    # Get answer from previous and current settings
    answer_interval = (previous_position, position)
    answer_probability = round(sum(probability_mass_function.setdefault(x, 0.0) for x in float_range(minimum=previous_position, maximum=position - settings['scale'], scale=settings['scale'])), 12)
    answer = (answer_interval, answer_probability)

    if previous_claim:
      certainty += [answer]

    else:
      uncertainty += [answer]

    # Store current settings from subset of claims for the following iteration
    previous_position = position
    previous_claim += claim

  return certainty, uncertainty
