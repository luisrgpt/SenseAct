def group_by_proximity(
    extrapolation,
):
  extrapolation = sorted(extrapolation, key=lambda x: x[1] - x[0])

  # Identify all possible common denominators
  proximity = {}
  key_pairs = ()
  key_pairs_set = set()
  for minimum, maximum in extrapolation:

    lower_key = (minimum, False)
    upper_key = (maximum, True)
    proximity[lower_key] = proximity.setdefault(lower_key, 0) + 1
    proximity[upper_key] = proximity.setdefault(upper_key, 0) + 1
    key_pairs += ((lower_key, upper_key),)
    key_pairs_set.add((lower_key, upper_key))

  # Group by common denominators. Remove the least frequent common denominators
  proximity_groups = {}
  while key_pairs_set:

    proximity_key, _ = max(proximity.items(), key=lambda x: x[1])
    removed_key_pair_set = set()
    for key_pair, extrapolation_key in zip(key_pairs, extrapolation):
      if proximity_key in key_pair:

        proximity_groups.setdefault(proximity_key, ())
        proximity_groups[proximity_key] +=  (extrapolation_key,)
        proximity[key_pair[0]] -= 1
        proximity[key_pair[1]] -= 1
        removed_key_pair_set.add(key_pair)
    key_pairs_set -= removed_key_pair_set

  return proximity_groups.values()
