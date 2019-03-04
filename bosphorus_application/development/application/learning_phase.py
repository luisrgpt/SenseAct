from uncertainty_dynamic_programming import build
from uncertainty_use_cases.submarine import Parameters

build(
  name=Parameters.name,

  boundaries=Parameters.boundaries,

  alert_catalog=Parameters.alert_catalog,
  trajectory_speed=Parameters.trajectory_speed,

  cost_table_quality=Parameters.cost_table_quality,
  stopping_condition=Parameters.stopping_condition,
  mutation_probability_of_flipping_bit=Parameters.mutation_probability_of_flipping_bit,

  max_size_of_population=Parameters.max_size_of_population,
  elite_chromosomes=Parameters.elite_chromosomes,
  selection_max_number_of_fit_chromosomes=Parameters.selection_max_number_of_fit_chromosomes,
  generation_number_of_initial_probes=Parameters.generation_number_of_initial_probes,
  sensor_catalog=Parameters.sensor_catalog,

  selection_base_logarithm=Parameters.selection_base_logarithm,
  crossover_probability_of_crossover=Parameters.crossover_probability_of_crossover,
  mutation_probability_of_mutation=Parameters.mutation_probability_of_mutation,

  sensor_success_rate_area=Parameters.sensor_success_rate_area,
  byzantine_fault_tolerance=Parameters.byzantine_fault_tolerance
)
