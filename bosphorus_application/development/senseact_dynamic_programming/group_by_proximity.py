def group_by_proximity(
    groups
):
  groups = sorted(groups, key=lambda x: x[1] - x[0])

  amounts = {}
  key_pairs = []
  key_pairs_size = 0
  for minimum, maximum in groups:
    lower_key = (minimum, False)
    upper_key = (maximum, True)
    amounts[lower_key] = amounts.setdefault(lower_key, 0) + 1
    amounts[upper_key] = amounts.setdefault(upper_key, 0) + 1
    key_pairs += [[lower_key, upper_key]]
    key_pairs_size += 1

  proximity_groups = {}
  for amount_key, amount_value in sorted(amounts.items(), key=lambda x: x[1]):
    if not key_pairs_size:
      break

    removed_keys = 0
    for position, (key_pair, group) in enumerate(zip(key_pairs, groups)):
      if not amount_value:
        break

      position -= removed_keys
      if any(group_key == amount_key for group_key in key_pair):
        proximity_groups.setdefault(amount_key, []).append(group)
        del key_pairs[position]
        removed_keys += 1
        amount_value -= 1
    key_pairs_size -= removed_keys

  return proximity_groups.values()
