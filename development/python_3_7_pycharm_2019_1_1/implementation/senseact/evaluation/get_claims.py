from itertools import \
  repeat

def get_claims(
    chromosome,
    boundaries,
    extended_boundaries,
    amount: int,
    settings,
):

  minimum, maximum = boundaries
  extended_minimum, extended_maximum = extended_boundaries

  # Get relevant positions
  length: float = extended_maximum - extended_minimum
  positions = len(settings['probe']['types']) * [
    extended_minimum + chromosome_position / (amount - 1) * length
    for chromosome_position in range(amount)
  ]
  chromosome_types = (
    y
    for x in settings['probe']['types'].keys()
    for y in repeat(x, amount)
  )

  # Get claims
  claims = {}
  for position, flipped, radius in zip(positions, chromosome, chromosome_types):
    if flipped:
      proclaim_position = float(max(minimum, position - radius))
      disclaim_position = float(min(position + radius, maximum))

      claims[proclaim_position] = claims.setdefault(proclaim_position, 0) + 1
      claims[disclaim_position] = claims.setdefault(disclaim_position, 0) - 1

  return claims
