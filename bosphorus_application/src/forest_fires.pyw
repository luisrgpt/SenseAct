# coding=utf-8

from random import randint, choice
from intervals import Interval

class Parameters:
    red_interval = ((40, False), (45, True))
    yellow_interval = ((45, True), (70, True))
    red_cost = 1000
    yellow_cost = 50

    approximation = Interval([((0, False), (100, True))])
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

    pb_neg = 0.7
    m_flips = 2
    m_tops = 5

    backend_location = 0
