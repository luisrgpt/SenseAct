from senseact_dynamic_programming import build
from senseact_use_cases.submarine import Parameters

build(
  name=Parameters.name,

  boundaries=Parameters.boundaries,

  alert_settings=Parameters.alert_settings,
  target_settings=Parameters.target_settings,

  cost_table_quality=Parameters.cost_table_quality,
  stopping_condition=Parameters.stopping_condition,
  mutate_probability_of_flipping_bit=Parameters.mutate_probability_of_flipping_bit,

  population_size=Parameters.population_size,
  population_elite_size=Parameters.population_elite_size,
  population_saved_size=Parameters.population_saved_size,
  nucleus_settings=Parameters.nucleus_settings,
  sensor_settings=Parameters.sensor_settings,

  select_base_logarithm=Parameters.select_base_logarithm,
  crossover_probability=Parameters.crossover_probability,
  mutate_probability_of_mutate=Parameters.mutate_probability_of_mutate,

  sensor_success_rate_area=Parameters.sensor_success_rate_area,
  byzantine_fault_tolerance=Parameters.byzantine_fault_tolerance
)
