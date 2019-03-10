def group_by_extrapolation(excluded):
  extrapolation_groups = {}
  for well_known_interval in interval_range(zone):
    if x not in excluded:
      incident_intervals = extrapolate(
        incident_intervals=x,
        excluded=excluded,
        partitions=useless_partitions
      )
      extrapolation_groups[x] = incident_intervals
      excluded += incident_intervals
  return extrapolation_groups
