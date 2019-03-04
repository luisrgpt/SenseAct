def get_measurement_cost(
    nucleus,
    sensor_catalog
):
  measurement_cost = 0
  for radius, comb in nucleus:
    # Get sensor cost
    sensor_cost = sensor_catalog[radius]

    # Increment measurement cost with sensor cost
    for center, probe_is_inserted_in_this_position in enumerate(comb):
      if probe_is_inserted_in_this_position:
        measurement_cost += sensor_cost

  return measurement_cost
