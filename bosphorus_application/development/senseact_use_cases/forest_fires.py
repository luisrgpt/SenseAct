from random import randint, choice
from senseact_math import Interval

class Parameters:
  name = 'forest_fires'

  red_interval = ((40, True), (45, False))
  yellow_interval = ((45, False), (70, False))
  red_cost = 1000
  yellow_cost = 50

  @staticmethod
  def trajectory(location):
    while True:
      yield location

      if location == 0:
        velocity = 1
      elif location == 100:
        velocity = -1
      else:
        velocity = choice([-location, location])
      norm = abs(velocity)

      normalized_vector = velocity / norm

      location = location + normalized_vector

  initial_position = randint(0, 100)

  stopping_condition = 10

  max_number_of_probes = 8
  population_size = 50
  population_elite_size = 5
  nucleus_settings = [
    (3, 1),
    (5, 1)
  ]
  population_saved_size = 2
  select_base_logarithm = 2
  crossover_probability = 0.1
  mutate_probability_of_mutate = 0.1
  mutate_probability_of_flipping_bit = 0.1

  alert_cost = 0
  sensor_cost = 0
  incident_intervals = Interval([((0, False), (100, True))])
  action_history = []
  turn = 0

  boundaries = ((0, False), (100, True))
  alert_settings = [
    (
      red_interval,
      red_cost
    ),

    (
      yellow_interval,
      yellow_cost
    )
  ]
  sensor_settings = {3: 10, 5: 1}
  sensor_success_rate_area = {3: [1] * 7, 5: [1] * 11}
  #   alert_settings = {
  #       'red': {
  #           interval: ((40, True), (45, False)),
  #           cost: 50,
  #       },
  #
  #       'yellow': {
  #           interval: ((45, False), (70, False)),
  #           cost: 1000,
  #       }
  #   }
  #   sensor_settings = {
  #       'expensive': {
  #           uncertainty: 3,
  #           cost: 10,
  #           nucleus_settings: 1,
  #           sensor_success_rate_area: [1]*7,
  #       },
  #
  #       'cheap': {
  #           uncertainty: 5,
  #           cost: 1,
  #           nucleus_settings: 1,
  #           sensor_success_rate_area: [1]*11,
  #       }
  #   }
  target_settings = 1
  cost_table_quality = 5
  byzantine_fault_tolerance = 0
