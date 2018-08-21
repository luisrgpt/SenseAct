# coding=utf-8

from random import randint, choice
from intervals import Interval

class Parameters:
    red_interval = ((40, True), (45, True))
    yellow_interval = ((45, True), (70, False))
    red_cost = 1000
    yellow_cost = 50

    appr = Interval([((0, False), (100, True))])
    bounds = ((0, False), (100, True))

    alert_costs = [(red_interval, red_cost), (yellow_interval, yellow_cost)]
    computation_rate = 5
    decay_unit = ((-1, False), (1, True))
    @staticmethod
    def method(location):
        while True:
            yield location
            if location is 0 or location is 100:
                return

            velocity = choice([-location, location])
            norm = abs(velocity)

            normalized_vector = velocity / norm

            location = location + normalized_vector
    argument = randint(0, 100)

    m_stagnation = 10
    m_flips = 1

    n_pool = 100
    m_tops = 5
    n_sel = 1
    n_precisions = [
        (3, 0),
        (5, 1)
    ]
    n_costs = {3: 10, 5: 1}

    k_mat = 0.1
    k_mut = 0.1

    backend_location = 0

    probability_distributions = {3: [1]*7, 5: [1]*11}
    byzantine_fault_tolerance = 0

    @classmethod
    def __repr__(cls):
        return (
            '{ alerts: ' +
            str(Interval([cls.red_interval])) + ' -> ' + str(cls.red_cost) + ' , ' +
            str(Interval([cls.yellow_interval])) + ' -> ' + str(cls.yellow_cost) +
            '}'
        )
