# coding=utf-8
from intervals import Interval
from random import random, randint, randrange

def generate(
        approximation: Interval,
        bounds: tuple,
        n_genes: int,
        pb_gen:float
):
    return [
        bounds[0][0] + 3 <= x <= bounds[1][0] - 3 and x in approximation and random() < pb_gen
        for x in range(n_genes)
    ]
def evaluate(
        time: int,
        approximation: Interval,
        cost_table: dict,
        m_tops: int,
        bounds: tuple,
        alert_costs: list,
        decay_unit: tuple,
        m_flips: int,
        pb_neg: float,
        comb: list
):
    #length = len([x for x in comb if x])
    #if length > 2:
    #    print(length)
    (o_lower, o_open), (o_upper, o_closed) = decay_unit
    minus_1 = time - 1
    n_interval = approximation.size()
    n_comb = len(comb)

    no = Interval(approximation[:])
    no_prob = 1

    yes = Interval([((0, False), (0, True))])

    total_cost = sum(10 for x in comb if x)
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
                if not(yes[0][0][0] == yes[0][1][0] and yes[0][0][1] and not yes[0][1][1]) and yes in approximation:
                    yes &= approximation
                    no &= ~yes

                    for x in yes:
                        #print(x)
                        yes_prob = (x[1][0] - x[0][0]) / n_interval

                        alert_cost = 0
                        for y, cost in alert_costs:
                            if (x if y[1] <= x[1] else y)[0] < (x if x[0] <= y[0] else y)[1]:
                                alert_cost = cost

                        x = ((x[0][0] + o_lower, x[0][1] or o_open), (x[1][0] + o_upper, x[1][1] and o_closed))
                        x = (max(x[0], bounds[0]), min(x[1], bounds[1]))

                        if str((minus_1, Interval([x]))) not in cost_table:
                            top5 = search(
                                time=minus_1,
                                approximation=Interval([x]),
                                cost_table=cost_table,
                                m_tops=m_tops,
                                bounds=bounds,
                                alert_costs=alert_costs,
                                decay_unit=decay_unit,
                                pb_neg=pb_neg,
                                m_flips=m_flips
                            )
                            cost_table[str((minus_1, Interval([x])))] = {
                                str(' '.join([str(index) for index, y in enumerate(comb) if y])):
                                    evaluate(
                                        time=minus_1,
                                        approximation=Interval([x]),
                                        cost_table=cost_table,
                                        m_tops=m_tops,
                                        bounds=bounds,
                                        alert_costs=alert_costs,
                                        decay_unit=decay_unit,
                                        pb_neg=pb_neg,
                                        m_flips=m_flips,
                                        comb=comb
                                    )
                                for comb in top5
                            }

                        wait_cost = min(cost_table[str((minus_1, Interval([x])))].values())
                        if minus_1 is 1:
                            print("no : " + str((minus_1, Interval([x]))) + " -> " + str(alert_cost) + " + " + str(wait_cost))

                        total_cost += yes_prob * (alert_cost + wait_cost)
                        no_prob -= yes_prob

                    yes[0] = ((yes[0][0][0], False), yes[0][1])
                    del yes[1:]
                yes[0] = ((endpoint, yes[0][0][1]), yes[0][1])
    alert_cost = 0
    wait_cost = 0
    #print(no)
    for x in no:
        for y, cost in alert_costs:
            if alert_cost < cost and (x if y[1] <= x[1] else y)[0] < (x if x[0] <= y[0] else y)[1]:
                alert_cost = cost

        x = ((x[0][0] + o_lower, x[0][1] or o_open), (x[1][0] + o_upper, x[1][1] and o_closed))
        x = (max(x[0], bounds[0]), min(x[1], bounds[1]))

        if str((minus_1, Interval([x]))) not in cost_table:
            top5 = search(
                time=minus_1,
                approximation=Interval([x]),
                cost_table=cost_table,
                m_tops=m_tops,
                bounds=bounds,
                alert_costs=alert_costs,
                decay_unit=decay_unit,
                pb_neg=pb_neg,
                m_flips=m_flips
            )
            cost_table[str((minus_1, Interval([x])))] = {
                str(' '.join([str(index) for index, y in enumerate(comb) if y])):
                    evaluate(
                        time=minus_1,
                        approximation=Interval([x]),
                        cost_table=cost_table,
                        m_tops=m_tops,
                        bounds=bounds,
                        alert_costs=alert_costs,
                        decay_unit=decay_unit,
                        pb_neg=pb_neg,
                        m_flips=m_flips,
                        comb=comb
                    )
                for comb in top5
            }

        wait_cost += min(cost_table[str((minus_1, Interval([x])))].values())
        if minus_1 is 1:
            print("no : " + str((minus_1, Interval([x]))) + " -> " + str(alert_cost) + " + " + str(wait_cost))
    total_cost += no_prob * (alert_cost + wait_cost)

    return total_cost
def mate(
        chromosome_1: list,
        chromosome_2: list
):
    chromosome_1 = [x for x in chromosome_1]
    chromosome_2 = [x for x in chromosome_2]

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

    cx_point = randint(min_point, max_point)
    chromosome_1[cx_point:], chromosome_2[cx_point:] = chromosome_2[cx_point:], chromosome_1[cx_point:]

    return chromosome_1, chromosome_2
def mutate(
        chromosome: list,
        n_genes: int,
        approximation: Interval,
        pb_neg: float,
        m_flips: int
):
    chromosome = [x for x in chromosome]

    flip_signal = pb_neg < random()
    # Cannot flip bits to false if there are no true's
    if sum(1 for x in chromosome if x) is 0 and not flip_signal:
        return chromosome

    # Assuming m_flips is always greater than 0
    n_flips = randint(1, m_flips)
    if flip_signal:
        # For each number of flips
        for _ in range(n_flips):
            # Repeat until gene is the opposite of its flip
            x = randrange(n_genes)
            while chromosome[x] == flip_signal and x in approximation:
                x = randrange(n_genes)
            # Flip value
            chromosome[x] = not chromosome[x]
    else:
        # For each number of flips
        for _ in range(n_flips):
            # Repeat until gene is the opposite of its flip
            x = randrange(n_genes)
            while chromosome[x] == flip_signal:
                if sum(1 for x in chromosome if x) is 0:
                    return chromosome
                x = randrange(n_genes)
            # Flip value
            chromosome[x] = not chromosome[x]

    return chromosome
def search(
        time: int,
        approximation: Interval,
        cost_table: dict,
        m_tops: int,
        bounds: tuple,
        alert_costs: list,
        decay_unit: tuple,
        m_flips: int,
        pb_neg: float
):
    elite = [
        y
        for x in approximation
        if str((time - 1, x)) in cost_table
        for y in cost_table[str((time - 1, x))].values()
    ]

    n_genes = (bounds[1][0] - bounds[0][0]) + 1
    n_pool = approximation.size()
    # Genetic search is useless if the approximation is degenerated
    if n_pool is 0:
        return [[False] * n_genes]

    pb_gen = 1 / n_pool
    n_gen = int(n_pool / 10) + 1

    #print("bounds: " + str(n_genes) + " size: " + str(n_pool) + " pb: " + str(pb_gen) + " gen: " + str(n_gen))

    # Generate and evaluate
    pool = [generate(approximation, bounds, n_genes, pb_gen) for _ in range(n_pool - len(elite))] + elite
    fitness = [
        evaluate(
            time=time,
            approximation=approximation,
            cost_table=cost_table,
            m_tops=m_tops,
            bounds=bounds,
            alert_costs=alert_costs,
            decay_unit=decay_unit,
            pb_neg=pb_neg,
            m_flips=m_flips,
            comb=x
        )
        for x in pool
    ]
    for _ in range(n_gen):
        # Mate, mutate and evaluate
        pool += [x for even, odd in zip(pool[::2], pool[1::2]) for x in mate(even, odd)]
        pool += [mutate(x, n_genes, approximation, pb_neg, m_flips) for x in pool]
        fitness += [
            evaluate(
                time=time,
                approximation=approximation,
                cost_table=cost_table,
                m_tops=m_tops,
                bounds=bounds,
                alert_costs=alert_costs,
                decay_unit=decay_unit,
                pb_neg=pb_neg,
                m_flips=m_flips,
                comb=x
            )
            for x in pool
        ]
        # Select
        pool = [x for _, x in sorted(zip(fitness, pool))][:n_pool]
        fitness = [x for x in sorted(fitness)][:n_pool]
    # Return top N
    return pool[:m_tops]

def test():
    from submarine import Parameters

    time = 1
    set_of_probes = [37]
    approximation = Interval([((16, True), (40, True))])

    cost_table = {
        str((0, x)): {"": 0}
        for x in Interval([Parameters.bounds]).range()
    }
    comb = [False] * (Interval([Parameters.bounds]).size() + 1)
    for pos in set_of_probes:
        comb[pos] = True

    print(evaluate(
        time=time,
        approximation=approximation,
        cost_table=cost_table,
        m_tops=Parameters.m_tops,
        bounds=Parameters.bounds,
        alert_costs=Parameters.alert_costs,
        decay_unit=Parameters.decay_unit,
        pb_neg=Parameters.pb_neg,
        m_flips=Parameters.m_flips,
        comb=comb
    ))

    #while True:
    #    search(
    #        time=1,
    #        approximation=approximation,
    #        cost_table=cost_table,
    #        m_tops=5,
    #        bounds=bounds
    #    )
    #    print(
    #        '\n'.join([
    #            str(rank) + '-> ' + ' '.join([str(index) for index, x in enumerate(comb) if x]) + ': ' +
    # str(evaluate(1, approximation, comb, cost_table, bounds))
    #            for rank, comb in enumerate(elites[str(approximation)])
    #        ])
    #    )
