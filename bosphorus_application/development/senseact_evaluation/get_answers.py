from typing import \
  List

def get_answers(
    claims,
    minimum: float,
    maximum: float,
    probability_mass_function: List[float] = None
):
  chromosome_size = maximum - minimum

  # Store initial settings from claims for the following iteration
  (previous_position, (previous_claim, _)), *claims = sorted(claims.items())
  previous_endpoint = [previous_position, False]

  # Get certainties and uncertainties from claims
  certainty = []
  uncertainty = []
  for position, (claim, included) in claims:
    # Get endpoint from subset of claims
    endpoint = [position, included and claim < 0]

    # Get answer from previous and current settings
    answer_interval = [previous_endpoint, endpoint]
    answer_probability = (position - previous_position) / chromosome_size
    answer = (answer_interval, answer_probability)

    if previous_claim:
      certainty += [answer]
    else:
      uncertainty += [answer]

    # Store current settings from subset of claims for the following iteration
    previous_position = position
    previous_claim += claim
    previous_endpoint = endpoint if included else [position, True]
  return certainty, uncertainty
