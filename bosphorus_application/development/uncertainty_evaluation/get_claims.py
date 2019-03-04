from uncertainty_typing import Claim

def get_claims(
    nucleus
) -> Claim:
  # Get maximum length from minimum and maximum position
  maximum_length = len(nucleus[0])

  # Get proclaims and disclaims from probes and maximum length
  proclaims = [0] * maximum_length
  disclaims = [0] * maximum_length
  for radius, comb in nucleus:
    for center, probe_is_inserted_in_this_position in enumerate(comb):
      if probe_is_inserted_in_this_position:
        proclaims[max(center - radius, 0)] += 1
        disclaims[min(center + radius, maximum_length - 1)] += 1

  return Claim(zip(proclaims, disclaims))
