def get_measurement_cost(
    nucleus,
    settings
):
  measurement_cost = 0
  for chromosome_type, chromosome in nucleus:
    # Get sensor cost
    sensor_cost = settings.types[chromosome_type]
    # Increment measurement cost with sensor cost
    for _, is_flipped in enumerate(chromosome):
      if is_flipped:
        measurement_cost += sensor_cost
  return measurement_cost
