from uncertainty_typing import Claim, Problem

def get_answers(
    claims: Claim,
    problem: Problem
):
  problem_interval, problem_pmf = problem
  ((problem_minimum, _), (problem_maximum, _)) = problem_interval
  problem_length = problem_maximum - problem_minimum

  # Get value of last position from claims
  last_position = len(claims) - 1

  # Store initial settings from claims for next iteration
  proclaim, disclaim = claims[0]
  previous_position = 0
  previous_claim = proclaim - disclaim
  previous_endpoint = (0, False)

  # Get certainties and uncertainties from claims
  current_claim = 0
  certainty = []
  uncertainty = []
  for position, proclaim, disclaim in enumerate(claims[1:], 1):
    # Get endpoint from subset of claims
    claim_variation = proclaim - disclaim
    current_claim += claim_variation
    claim_is_negative = current_claim < previous_claim
    endpoint = \
      (position, True) if position is last_position else \
        (position, claim_is_negative) if claim_variation else \
          (position, False) if proclaim else \
            None

    if not endpoint:
      continue

    # Get answer from previous and current settings
    answer_interval = (previous_endpoint, endpoint)
    answer_probability = (position - previous_position) / problem_length
    answer_uncertainty = previous_claim is 0
    answer = (answer_interval, answer_probability, answer_uncertainty)

    if previous_claim:
      certainty += [answer]
    else:
      uncertainty += [answer]

    # Store current settings from subset of claims for next iteration
    previous_position = position
    previous_claim = current_claim
    previous_endpoint = \
      (position, True) if proclaim else \
        endpoint

  return certainty, uncertainty
