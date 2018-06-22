# coding=utf-8
"""Dynamic

"""
from itertools import chain
from genetic import get_cost
from time import sleep

def dynamic(time, state, cost, gen, current_time):
    while True:
        for t in range(1, time):
            for x, top5 in zip(chain.from_iterable(state), gen):
                cost[str((t, x))] = {str(y): get_cost(t, y, state, cost) for y in top5}

                #print(str((t, x)) + ": " + str(list(cost[str((t, x))].values())))
            current_time += 1
        yield cost
