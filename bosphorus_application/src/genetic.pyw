# coding=utf-8
"""Genetic

"""
from deap import algorithms, base, creator, tools
from intervals import AbsoluteUncertainty, Interval, IntervalExpression, LeftEndpoint, RightEndpoint
import random


# Start parameters
gene_pool_size = 10
chromosome_size = 101
percentage = 1
# Mutate parameters
mut_parameter = 1
# Select parameters
# k = 10
# Algorithm parameters
cx_pb = 0.5
mut_pb = 1
n_gen = 5
verbose = False

def get_cost(time, comb, state, cost):
    probe_cost = 10

    answers = [index for index, x in enumerate(comb) if x]
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

    return deploy_cost + yes_cost + no_cost

# Custom genetic algorithms
def gen_gene(to_true_gen_pb: int):
    """

    :type to_true_gen_pb: int
    :param to_true_gen_pb:
    :return:
    """
    return random.randint(1, 100) <= to_true_gen_pb
def eval_probes(chromosome: list, state, cost, time):
    """

    :type state: intervals.IntervalExpression
    :param state:
    :type chromosome: list
    :param chromosome:
    :return:
    """
    # current = time.time()
    # Get all genes from chromosome
    genes = [index for index, value in enumerate(chromosome) if value]

    # When there is an unacceptable amount of probes
    if len(genes) > 4:
        return 9000.0,

    return get_cost(time, chromosome, state, cost),
def cx_biased_one_point(chromosome_1: list, chromosome_2: list):
    """

    :type chromosome_1: list
    :param chromosome_1:
    :param chromosome_2:
    :return:
    """
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
def mut_biased_flip_bit(chromosome: list, max_number_of_flips: int):
    """

    :type chromosome: list
    :param max_number_of_flips:
    :param chromosome:
    :return:
    """
    number_of_flips = random.randint(-max_number_of_flips, max_number_of_flips)

    flip_signal = number_of_flips > 0

    # for each number of flips
    for x in range(abs(number_of_flips)):
        # break loop if all genes are flipped
        if all(y == flip_signal for y in chromosome):
            break

        # repeat until gene is the opposite of its flip
        y = random.randrange(len(chromosome))
        while chromosome[y] == flip_signal:
            y = random.randrange(len(chromosome))
        # flip value
        chromosome[y] = type(chromosome[y])(not chromosome[y])

    return chromosome,

creator.create(
    'FitnessMax',
    base.Fitness,
    weights=(1.0,)
)
creator.create(
    'Chromosome',
    list,
    fitness=creator.FitnessMax
)

toolbox = base.Toolbox()
toolbox.register(
    'gene',
    gen_gene,
    to_true_gen_pb=percentage
)
toolbox.register(
    'chromosome',
    tools.initRepeat,
    creator.Chromosome,
    toolbox.gene,
    n=chromosome_size
)
toolbox.register(
    'gene_pool',
    tools.initRepeat,
    list,
    toolbox.chromosome
)
toolbox.register(
    'mate',
    cx_biased_one_point
)
toolbox.register(
    'mutate',
    mut_biased_flip_bit,
    max_number_of_flips=mut_parameter
)
toolbox.register(
    'select',
    tools.selWorst
)

def get_genetic_result(state, cost, time, n_top):
    global toolbox

    #print(state)

    gene_pool = toolbox.gene_pool(
        n=gene_pool_size
    )

    toolbox.register(
        'evaluate',
        eval_probes,
        state=state,
        cost=cost,
        time=time
    )

    return sorted(
        algorithms.eaSimple(
            population=gene_pool,
            toolbox=toolbox,
            cxpb=cx_pb,
            mutpb=mut_pb,
            ngen=n_gen,
            verbose=verbose
        )[0],
        key=lambda g: eval_probes(g, state, cost, time)
    )[:n_top]

def test():
    pass
    #print(eval_probes([0]*23 + [1] + [0]*14 + [1] + [0]*6 + [1] + [0]*55, domain()))
    #xs = genetic_algorithm()
    #list(sorted([eval_probes(x) for x in xs]))