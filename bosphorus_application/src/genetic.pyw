# coding=utf-8
from intervals import AbsoluteUncertainty, Interval, IntervalExpression, LeftEndpoint, RightEndpoint
from random import random

n_genes = 1001
n_pool = 10
n_gen = 5
max_flips = 1
pb_gen = 0.01
pb_mate = 0.5
not_pb_mutate = 0.9

def evaluate(comb, state, cost, time):
    probe_cost = 10
    answers = [index for index, x in enumerate(comb) if x]

    # When there is an unacceptable amount of probes
    if len(answers) > 4:
        return 9000.0

    yes_intervals = [
        Interval(
            left=LeftEndpoint(x - 3, False, True),
            right=RightEndpoint(x + 3, False, True)
        ) for x in answers
    ]
    no_space = ~IntervalExpression(yes_intervals) & state

    len_state = sum(len(x) for x in state)
    minus_1 = time - 1

    deploy_cost = probe_cost * len(answers)
    yes_cost = sum(
        len(x) / len_state * min(cost[str((minus_1, (x + AbsoluteUncertainty(0, 1)) & state[0]))].values())
        for x in yes_intervals
    )
    no_cost = sum(
        len(x) / len_state * min(cost[str((minus_1, (x + AbsoluteUncertainty(0, 1)) & state[0]))].values())
        for x in no_space
    )

    return (deploy_cost + yes_cost + no_cost),
def mate(chromosome_1: list, chromosome_2: list):
    # Check if both chromosomes are identical
    if chromosome_1 == chromosome_2:
        return chromosome_1, chromosome_2

    # Identify first difference
    min_point = None
    for min_point in range(len(chromosome_1)):
        if chromosome_1[min_point] != chromosome_2[min_point]:
            break

    # Identify last difference
    max_point = None
    for max_point in range(len(chromosome_1) - 1, -1, -1):
        if chromosome_1[max_point] != chromosome_2[max_point]:
            break

    # Check if both chromosomes differ at one and only one gene
    if min_point == max_point:
        return chromosome_1, chromosome_2

    cx_point = random.randint(min_point, max_point)
    chromosome_1[cx_point:], chromosome_2[cx_point:] = chromosome_2[cx_point:], chromosome_1[cx_point:]

    return chromosome_1, chromosome_2
def mutate(chromosome: list, max_flips: int):
    n_flips = random.randint(-max_flips, max_flips)

    flip_signal = n_flips > 0

    # for each number of flips
    for x in range(abs(n_flips)):
        # break loop if all genes are flipped
        if all(y == flip_signal for y in chromosome):
            break

        # repeat until gene is the opposite of its flip
        y = random.randrange(len(chromosome))
        while chromosome[y] == flip_signal:
            y = random.randrange(len(chromosome))
        # flip value
        chromosome[y] = type(chromosome[y])(not chromosome[y])

    return chromosome
def search(state, cost, time, n_tops):
    # Generate and evaluate
    pool = [[random() < pb_gen for _ in range(n_genes)] for _ in range(n_pool)]
    fitness = [evaluate(x, state, cost, time) for x in pool]
    prob = [random() for _ in pool]
    for _ in range(n_gen):
        # Mate, mutate and evaluate
        pool += [x for even, odd, pb in zip(pool[::2], pool[1::2], prob) if pb < pb_mate for x in mate(even, odd)]
        pool += [mutate(x, max_flips) for x, pb in zip(pool, prob) if not_pb_mutate <= pb]
        fitness += [evaluate(x, state, cost, time) for x in pool[n_pool:]]
        # Select
        pool = [x for _, x in sorted(zip(fitness, pool))][:n_pool]
        fitness = [x for x in sorted(fitness)][:n_pool]
        prob = [random() for _ in pool]
    # Return top N
    return pool[:n_tops]