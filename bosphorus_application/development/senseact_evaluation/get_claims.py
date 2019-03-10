def get_claims(
    nucleus,
    minimum: float,
    maximum: float,
    amount: int
):
  # Get relevant positions
  chromosome_size: float = maximum - minimum
  positions = [
    minimum + chromosome_size * chromosome_position / (amount - 1)
    for chromosome_position in range(amount)
  ]

  # Get claims
  claims = {}
  for radius, chromosome in nucleus:
    for position, flipped in zip(positions, chromosome):
      if flipped:
        proclaim_position = max(minimum, position - radius)
        disclaim_position = min(position + radius, maximum)
        if proclaim_position not in claims:
          claims[proclaim_position] = [0, True]
        if disclaim_position not in claims:
          claims[disclaim_position] = [0, True]
        if claims[disclaim_position][0] > 0:
          claims[proclaim_position][1] = False
        claims[proclaim_position][0] += 1
        claims[disclaim_position][0] -= 1

  return claims
