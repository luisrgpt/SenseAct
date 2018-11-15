# coding=utf-8
############################################################










############################################################
from random import randint, choice
from intervals import Interval
############################################################










############################################################
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
    max_size_of_population = 50
    elite_chromosomes = 5
    generation_number_of_initial_probes = [
        (3, 1),
        (5, 1)
    ]
    selection_max_number_of_fit_chromosomes = 2
    selection_base_logarithm = 2
    crossover_probability_of_crossover = 0.1
    mutation_probability_of_mutation = 0.1
    mutation_probability_of_flipping_bit = 0.1

    alert_cost = 0
    probe_cost = 0
    answer_intervals = Interval([((0, False), (100, True))])
    action_history = []
    turn = 0

    boundaries = ((0, False), (100, True))
    alert_catalog = [
        (
            red_interval,
            red_cost
        ),

        (
            yellow_interval,
            yellow_cost
        )
    ]
    probe_catalog = {3: 10, 5: 1}
    probe_success_rate_area = {3: [1]*7, 5: [1]*11}
    #   alert_catalog = {
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
    #   probe_catalog = {
    #       'expensive': {
    #           uncertainty: 3,
    #           cost: 10,
    #           generation_number_of_initial_probes: 1,
    #           probe_success_rate_area: [1]*7,
    #       },
    #
    #       'cheap': {
    #           uncertainty: 5,
    #           cost: 1,
    #           generation_number_of_initial_probes: 1,
    #           probe_success_rate_area: [1]*11,
    #       }
    #   }
    trajectory_speed = 1
    cost_table_quality = 5
    byzantine_fault_tolerance = 0
