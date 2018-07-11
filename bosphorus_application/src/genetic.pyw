# coding=utf-8
from intervals import AbsoluteUncertainty, Interval
from random import random, randint, randrange, choice

# Constants
m_flips = 1
pb_neg = 0.7

elites = {}

def generate(expression, limit, n_genes, pb_gen):
    return [
        limit[0][0][0] + 3 <= x <= limit[0][1][0] - 3 and x in expression and random() < pb_gen
        for x in range(n_genes)
    ]

def evaluate(time, expression, comb, cost_table, limit: Interval, alert_costs):
    #length = len([x for x in comb if x])
    #if length > 2:
    #    print(length)
    minus_1 = time - 1
    decay_unit = AbsoluteUncertainty(0, 1)
    n_interval = expression.size()
    n_comb = len(comb)

    no = Interval(expression[:])
    no_prob = 1

    yes = Interval([((0, False), (0, True))])

    total_cost = sum(10 for x in comb if x)
    x = Interval([])
    if n_interval is not 0:
        for i, positive in enumerate(comb):
            if not positive:
                continue
            lower_offset = max(0, i - 6)
            upper_offset = min(i + 1, n_comb)
            upper_value = min(i + 6, n_comb)
            lower_value = max(
                [i - 3] +
                [
                    lower_offset + j + 3
                    for j, x in enumerate(comb[lower_offset:i])
                    if x
                ]
            )
            endpoints = (
                [
                    upper_offset + j - 3
                    for j, x in enumerate(comb[upper_offset:upper_value])
                    if x and upper_offset + j - 3 >= lower_value
                ] +
                [i + 3]
            )
            #print(str(lower_value) + ".." + str(upper_values))
            yes[0] = ((lower_value, lower_value != i - 3), yes[0][1])
            for endpoint in endpoints:
                yes[0] = (yes[0][0], (endpoint, endpoint == i + 3))
                if not(yes[0][0][0] == yes[0][1][0] and yes[0][0][1] and not yes[0][1][1]) and yes in expression:
                    yes &= expression
                    no &= ~yes

                    for y in yes:
                        x.intervals = [y]
                        #print(x)
                        yes_prob = x.size() / n_interval
                        alert_cost = 0
                        for alert_interval, cost in alert_costs:
                            lower = (x[0] if alert_interval[0][1] <= x[0][1] else alert_interval[0])[0]
                            upper = (x[0] if x[0][0] <= alert_interval[0][0] else alert_interval[0])[1]

                            if lower[0] < upper[0] or (lower[0] == upper[0] and lower[1] < upper[1]):
                                alert_cost = cost
                        x += decay_unit
                        x &= limit
                        wait_cost = min(cost_table[str((minus_1, x))].values())
                        total_cost += yes_prob * (alert_cost + wait_cost)
                        no_prob -= yes_prob

                    yes[0] = ((yes[0][0][0], False), yes[0][1])
                    del yes[1:]
                yes[0] = ((endpoint, yes[0][0][1]), yes[0][1])
    alert_cost = 0
    wait_cost = 0
    #print(no)
    for y in no:
        x.intervals = [y]
        for alert_interval, cost in alert_costs:
            lower = (x[0] if alert_interval[0][1] <= x[0][1] else alert_interval[0])[0]
            upper = (x[0] if x[0][0] <= alert_interval[0][0] else alert_interval[0])[1]

            if alert_cost < cost and (
                lower[0] < upper[0] or (lower[0] == upper[0] and lower[1] < upper[1])
            ):
                alert_cost = cost
        x += decay_unit
        x &= limit
        wait_cost += min(cost_table[str((minus_1, x))].values())
    total_cost += no_prob * (alert_cost + wait_cost)

    return total_cost
def mate(chromosome_1: list, chromosome_2: list, n_genes):
    chromosome_1 = [x for x in chromosome_1]
    chromosome_2 = [x for x in chromosome_2]

    answers_1 = [index for index, x in enumerate(chromosome_1) if x]
    answers_2 = [index for index, x in enumerate(chromosome_2) if x]

    point_1 = choice(answers_1) if len(answers_1) > 0 else randrange(n_genes)
    point_2 = choice(answers_2) if len(answers_2) > 0 else randrange(n_genes)

    chromosome_1[point_1], chromosome_2[point_2] = chromosome_2[point_2], chromosome_1[point_1]

    return chromosome_1, chromosome_2
def mutate(chromosome: list, n_genes):
    chromosome = [x for x in chromosome]

    flip_signal = pb_neg < random()
    n_yes = sum(1 for x in chromosome if x)
    # Cannot flip bits to false if there are no true's
    if n_yes is 0 and not flip_signal:
        return chromosome

    if n_yes >= 4 and flip_signal:
        flip_signal = not flip_signal

    # Assulowerg m_flips is always greater than 0
    n_flips = randint(1, m_flips)
    # For each number of flips
    for _ in range(n_flips):
        # Repeat until gene is the opposite of its flip
        x = randrange(n_genes)
        while chromosome[x] == flip_signal:
            x = randrange(n_genes)
        # Flip value
        chromosome[x] = not chromosome[x]

    return chromosome
def search(time, expression, cost_table, m_tops, limit: Interval, alert_costs):
    global elites

    n_genes = len(limit) + 1
    n_pool = len(expression)
    # Genetic search is useless if the expression is degenerated
    if n_pool is 0:
        return [[False] * n_genes]

    key = str(expression)
    elite = elites[key] if key in elites else []
    n_expr = len(expression)
    pb_gen = 1 / n_expr
    n_gen = int(n_expr / 10) + 1

    #print("limit: " + str(n_genes) + " size: " + str(n_pool) + " pb: " + str(pb_gen) + " gen: " + str(n_gen))

    # Generate and evaluate
    pool = [generate(expression, limit, n_genes, pb_gen) for _ in range(n_pool - len(elite))] + elite
    fitness = [evaluate(time, expression, comb, cost_table, limit, alert_costs) for comb in pool]
    for _ in range(n_gen):
        # Mate, mutate and evaluate
        pool += [x for even, odd in zip(pool[::2], pool[1::2]) for x in mate(even, odd, n_genes)]
        pool += [mutate(x, n_genes) for x in pool]
        fitness += [evaluate(time, expression, comb, cost_table, limit, alert_costs) for comb in pool[n_pool:]]
        # Select
        pool = [x for _, x in sorted(zip(fitness, pool))][:n_pool]
        fitness = [x for x in sorted(fitness)][:n_pool]
    # Return top N
    elites[key] = pool[:n_gen]
    return pool[:m_tops]

def test():
    red_interval = Interval([((40, False), (45, True))])
    yellow_interval = Interval([((45, True), (70, True))])
    red_cost = 1000
    yellow_cost = 50
    alert_costs = [(red_interval, red_cost), (yellow_interval, yellow_cost)]
    limit = Interval([((0, False), (100, True))])
    cost_table = {
        str((0, x)): {"": 0}
        for x in limit.range()
    }
    expression = Interval([((0, False), (100, True))])


    comb = [False] * 32 + [True] + [True] + [True] + [False] * 66

    print(evaluate(
        time=1,
        expression=expression,
        comb=comb,
        cost_table=cost_table,
        limit=limit,
        alert_costs=alert_costs
    ))

    #while True:
    #    search(
    #        time=1,
    #        expression=expression,
    #        cost_table=cost_table,
    #        m_tops=5,
    #        limit=limit
    #    )
    #    print(
    #        '\n'.join([
    #            str(rank) + '-> ' + ' '.join([str(index) for index, x in enumerate(comb) if x]) + ': ' +
    # str(evaluate(1, expression, comb, cost_table, limit))
    #            for rank, comb in enumerate(elites[str(expression)])
    #        ])
    #    )
