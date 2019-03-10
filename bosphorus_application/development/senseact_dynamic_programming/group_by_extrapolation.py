def group_by_extrapolation(excluded, useless_partitions):
  extrapolation_groups = {}
  for x in reversed(sorted(
      Interval([boundaries]).range(),
      key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(
        x[1][1])
  )):
    if x not in excluded:
      incident_intervals = extrapolate(
        incident_intervals=x,
        excluded=excluded,
        partitions=useless_partitions
      )
      extrapolation_groups[x] = incident_intervals
      excluded += incident_intervals
  return extrapolation_groups
