def get_answers(
    claims,
    boundaries,
):

  minimum, maximum = boundaries

  chromosome_size = maximum - minimum

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
    answer_probability = round(position - previous_position, 12) / chromosome_size
    answer = (answer_interval, answer_probability)

    if previous_claim:
      certainty += [answer]

    else:
      uncertainty += [answer]

    # Store current settings from subset of claims for the following iteration
    previous_position = position
    previous_claim += claim

  return certainty, uncertainty
