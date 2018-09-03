# coding=utf-8

from intervals import Interval
from random import random, randint
from math import inf
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from functools import partial

import time as timer
import csv

def generate(
        useful_probes_range: Interval,
        n_genes: int,
        n_initial_probes: int,
        n_useful_probes: int
):
    pb_gen = n_initial_probes / n_useful_probes
    return [
        x in useful_probes_range and random() < pb_gen
        for x in range(n_genes)
    ]
def evaluate(
        time: int,
        appr: tuple,
        cost_table: dict,
        bounds: tuple,
        alert_costs: list,
        decay_unit: tuple,
        nucleus: list,
        n_costs: dict,

        probability_distributions: dict,
        byzantine_fault_tolerance: int,

        bounds_distribution: list,

        intervals: list,

        convert: bool = True
):
    (d_lower, d_open), (d_upper, d_closed) = decay_unit
    minus_1 = time - 1
    noes = [Interval([s_appr]) for s_appr in intervals]
    no_probs = [1] * len(intervals)

    if convert:
        probes = [(x, i) for i, comb in nucleus for x in range(bounds[0][0], bounds[1][0]) if comb[x]]
    else:
        probes = [(x, i) for i, comb in nucleus for x in comb]
    probes.sort(key=lambda x: x[0] - x[1])

    probe_cost = 0
    groups = []
    claim_groups = []
    for x, i in probes:
        probe_cost += n_costs[i]

        in_groups = False
        x_l = x - i
        x_h = x + i
        for y in range(len(groups)):
            endpoints = groups[y]
            l = 1

            if x_l < endpoints[0]:
                #print(str(x_l) + ' ' + str(claim_groups) + ' ' + str(groups), end='')
                groups[y][:0] += [x_l]
                claim_groups[y][:0] += [1]
                in_groups = True
                #print(' <0< ' + str(claim_groups) + ' ' + str(groups), end='')

            elif x_l == endpoints[0]:
                #print(str(x_l) + ' ' + str(claim_groups) + ' ' + str(groups), end='')
                in_groups = True
                #print(' =0= ' + str(claim_groups) + ' ' + str(groups), end='')

            elif endpoints[0] < x_l < endpoints[1]:
                #print(str(x_l) + ' ' + str(claim_groups) + ' ' + str(groups), end='')
                groups[y][0:1] += [x_l]
                claim_groups[y] += [claim_groups[y][0]]
                in_groups = True
                #print(' >0> ' + str(claim_groups) + ' ' + str(groups), end='')

            elif endpoints[-1] == x_l:
                #print(str(x_l) + ' ' + str(claim_groups) + ' ' + str(groups), end='')
                groups[y] += [x_l]
                claim_groups[y] += [claim_groups[y][-1]]
                in_groups = True
                #print(' =-1= ' + str(claim_groups) + ' ' + str(groups), end='')

            else:
                for z in range(1, len(endpoints) - 1):
                    l += 1

                    if endpoints[z] == x_l:
                        #print(str(x_l) + ' ' + str(claim_groups) + ' ' + str(groups), end='')
                        groups[y][z - 1:z] += [x_l]
                        claim_groups[y][z - 1:z] += [claim_groups[y][z]]
                        in_groups = True
                        #print(' = ' + str(claim_groups) + ' ' + str(groups), end='')
                        break

                    elif endpoints[z] < x_l < endpoints[z + 1]:
                        #print(str(x_l) + ' ' + str(claim_groups) + ' ' + str(groups), end='')
                        groups[y][z:z + 1] += [x_l]
                        claim_groups[y][z - 1:z] += [claim_groups[y][z]]
                        in_groups = True
                        #print(' > ' + str(claim_groups) + ' ' + str(groups), end='')
                        break

            #print(l)
            if in_groups:
                for z in range(l, len(endpoints)):
                    if x_h < endpoints[z]:
                        groups[y][z - 1:z] += [x_h]
                        claim_groups[y][z - 2:z - 1] += [claim_groups[y][z - 1]]
                        claim_groups[y][z - 1] += 1
                        #print(' -<> ' + str(claim_groups) + ' ' + str(groups), end='')
                        break

                    elif x_h == endpoints[z]:
                        groups[y][z - 1:z] += [x_h]
                        claim_groups[y][z - 2:z - 1] += [claim_groups[y][z - 1]]
                        claim_groups[y][z - 1] += 1
                        claim_groups[y][z] += 2
                        #print(' -==> ' + str(claim_groups) + ' ' + str(groups), end='')
                        break

                    elif z == len(endpoints) - 1:
                        groups[y] += [x_h]
                        claim_groups[y] += [1]
                        #print(' ->>> ' + str(claim_groups) + ' ' + str(groups), end='')
                        break

                    else:
                        claim_groups[y][z] += 1
                        #print(' ->> ' + str(claim_groups) + ' ' + str(groups), end='')
                break

        if not in_groups:
            groups += [[x_l, x_h]]
            claim_groups += [[1]]
            #print(str(x_l) + ' new ' + str(claim_groups) + ' ' + str(groups), end='')

    total_costs = [probe_cost] * len(intervals)
    #print(str(claim_groups) + ' ' + str(groups))
    for endpoints, claims in zip(groups, claim_groups):
        for x in range(len(endpoints) - 1):
            #if claims[x] < byzantine_fault_tolerance + 1:
            #    continue

            yes = (
                (endpoints[x], x == 0 or claims[x - 1] < claims[x]),
                (endpoints[x + 1], x < len(endpoints) - 2 and claims[x] < claims[x + 1])
            )
            if (yes if yes[0] <= appr[0] else appr)[1] <= (yes if appr[1] <= yes[1] else appr)[0]:
                continue

            for y in range(len(intervals)):
                appr_yes = (max(yes[0], intervals[y][0]), min(yes[1], intervals[y][1]))
                yes_prob = sum(bounds_distribution[int(appr_yes[0][0]):int(appr_yes[1][0])])
                if yes_prob == 0:
                    if 1 < claims[x]:
                        noes[y].remove(appr_yes)
                    continue

                noes[y].remove(appr_yes)
                alert_cost = 0
                for z, cost in alert_costs:
                    lower = (appr_yes if z[1] <= appr_yes[1] else z)[0]
                    upper = (appr_yes if appr_yes[0] <= z[0] else z)[1]
                    if alert_cost < cost and lower < upper:
                        alert_cost = cost

                delayed_yes = (
                    (appr_yes[0][0] + d_lower, appr_yes[0][1] or d_open),
                    (appr_yes[1][0] + d_upper, appr_yes[1][1] and d_closed)
                )
                bounded_yes = (max(delayed_yes[0], bounds[0]), min(delayed_yes[1], bounds[1]))
                # if (minus_1, bounded_yes) not in cost_table:
                #     search(
                #         time=minus_1,
                #         t_appr=(bounded_yes, [bounded_yes]),
                #         cost_table=cost_table,
                #         n_pool=n_pool,
                #         m_tops=m_tops,
                #         n_sel=n_sel,
                #         bounds=bounds,
                #         alert_costs=alert_costs,
                #         decay_unit=decay_unit,
                #         m_stagnation=m_stagnation,
                #         m_flips=m_flips,
                #         n_precisions=n_precisions,
                #         n_costs=n_costs,
                #         k_mat=k_mat,
                #         k_mut=k_mut,
                #         elite=elite,
                #
                #         probability_distributions=probability_distributions,
                #         byzantine_fault_tolerance=byzantine_fault_tolerance
                #     )

                wait_cost = cost_table[(minus_1, bounded_yes)][0][1]
                total_costs[y] += yes_prob * (alert_cost + wait_cost)
                no_probs[y] -= yes_prob

    for z in range(len(intervals)):
        if no_probs[z] > 0:
            alert_cost = 0
            wait_cost = 0
            for x in noes[z]:
                for y, cost in alert_costs:
                    lower = (x if y[1] <= x[1] else y)[0]
                    upper = (x if x[0] <= y[0] else y)[1]
                    if alert_cost < cost and lower < upper:
                        alert_cost = cost

                x_prob = sum(bounds_distribution[int(x[0][0]):int(x[1][0])]) / no_probs[z]
                if x_prob == 0:
                    continue

                delayed_x = ((x[0][0] + d_lower, x[0][1] or d_open), (x[1][0] + d_upper, x[1][1] and d_closed))
                bounded_x = (max(delayed_x[0], bounds[0]), min(delayed_x[1], bounds[1]))
                # if (minus_1, bounded_x) not in cost_table:
                #     search(
                #         time=minus_1,
                #         t_appr=(bounded_x, [bounded_x]),
                #         cost_table=cost_table,
                #         n_pool=n_pool,
                #         m_tops=m_tops,
                #         n_sel=n_sel,
                #         bounds=bounds,
                #         alert_costs=alert_costs,
                #         decay_unit=decay_unit,
                #         m_stagnation=m_stagnation,
                #         m_flips=m_flips,
                #         n_precisions=n_precisions,
                #         n_costs=n_costs,
                #         k_mat=k_mat,
                #         k_mut=k_mut,
                #         elite=elite,
                #
                #         probability_distributions=probability_distributions,
                #         byzantine_fault_tolerance=byzantine_fault_tolerance
                #     )
                wait_cost += x_prob * cost_table[(minus_1, bounded_x)][0][1]
            total_costs[z] += no_probs[z] * (alert_cost + wait_cost)

    # Debug
    # print((time, appr))
    # print('probe cost: ' + str(probe_cost))
    # if probe_cost != 0:
    #     n_appr = appr[1][0] - appr[0][0]
    #     print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')'
    #         for u, comb in nucleus]) + ' ' + ' '.join([str(endpoints[0]) + '..' + ','.join([str(x)
    #         for x in endpoints[1:]]) for endpoints in groups]))
    #     no = Interval([appr])
    #     # print(no, end='')
    #     for endpoints, claims in zip(groups, claim_groups):
    #         for x in range(len(endpoints) - 1):
    #             yes = (
    #                 (endpoints[x], x == 0 or claims[x - 1] < claims[x]),
    #                 (endpoints[x + 1], x < len(endpoints) - 2 and claims[x] < claims[x + 1])
    #             )
    #             if (yes if yes[0] <= appr[0] else appr)[1] <= (yes if appr[1] <= yes[1] else appr)[0]:
    #                 print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')'
    #                     for u, comb in nucleus]) + ' yes: ' + str(
    #                     (time, Interval([yes]))) + ' -> ' + str(
    #                     (time, Interval([]))) + ' -> 0')
    #                 continue
    #             appr_yes = (max(yes[0], appr[0]), min(yes[1], appr[1]))
    #             no.remove(yes)
    #             yes_prob = (appr_yes[1][0] - appr_yes[0][0]) / n_appr
    #             if yes_prob == 0:
    #                 print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')'
    #                     for u, comb in nucleus]) + ' yes: ' + str(
    #                     (time, Interval([yes]))) + ' -> ' + str(
    #                     (time, Interval([appr_yes]))) + ' -> 0', end='')
    #                 print(' ------------------- no : ' + str(no))
    #                 continue
    #             y_alert_cost = 0
    #             for x, cost in alert_costs:
    #                 if y_alert_cost < cost and (appr_yes if x[1] <= appr_yes[1] else x)[0] < \
    #                         (appr_yes if appr_yes[0] <= x[0] else x)[1]:
    #                     y_alert_cost = cost
    #             delayed_x = (
    #                (appr_yes[0][0] + d_lower, appr_yes[0][1] or d_open),
    #                (appr_yes[1][0] + d_upper, appr_yes[1][1] and d_closed)
    #             )
    #             bounded_x = (max(delayed_x[0], bounds[0]), min(delayed_x[1], bounds[1]))
    #             wait_cost = min([x for _, x in cost_table[(minus_1, bounded_x)]])
    #             print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')'
    #                 for u, comb in nucleus]) + ' yes: ' + str(
    #                 (time, Interval([yes]))) + ' -> cost-table(' + str(
    #                 (minus_1, Interval([bounded_x]))) + ') -> (' + str(y_alert_cost) + ' + ' + str(
    #                 wait_cost) + ') * (' + str(int(yes_prob * n_appr)) + ' / ' + str(n_appr) + ') = ' + str(
    #                 yes_prob * (y_alert_cost + wait_cost)), end='')
    #             print(' ------------------- no : ' + str(no))
    #             # print(' - [' + str(l) + '..' + str(h) + '] -> ' + str(no), end='')
    #     # print(' -> ' + str(no))
    #     print(
    #         ','.join(
    #             [
    #                 str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')'
    #                 for u, comb in nucleus
    #             ]
    #         ) +
    #         ' no : ' + str((time, no)) + ' -> cost-table(' + str((minus_1, no + decay_unit)) + ') -> (' +
    #         str(alert_cost) + ' + ' + str(wait_cost) + ') * (' + str(int(no_probs[-1] * n_appr))  + ' / ' +
    #         str(n_appr) + ') = ' + str(no_probs[-1] * (alert_cost + wait_cost)))
    # print('')
    return total_costs
def mate(
        chromosome_1: list,
        chromosome_2: list
):
    # Check if both chromosomes are identical
    if chromosome_1 == chromosome_2:
        return

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
        return

    cx_point = randint(min_point, max_point)
    chromosome_1[cx_point:], chromosome_2[cx_point:] = chromosome_2[cx_point:], chromosome_1[cx_point:]
def mutate(
        chromosome: list,
        useful_probes_range: dict,
        n_appr: int,
        k_mut: float
):
    n_probes = sum(chromosome)

    for n in range(len(chromosome)):
        if n not in useful_probes_range[5]:
            continue

        r = random()

        if not chromosome[n] and k_mut * (n_probes + 1) / n_appr < r:
            chromosome[n] = True
        elif chromosome[n] and k_mut * (1 - n_probes / n_appr) < r:
            chromosome[n] = False
def search(
        t_appr: tuple,
        time: int,
        cost_table: dict,
        n_pool: int,
        m_tops: int,
        n_sel: int,
        bounds: tuple,
        alert_costs: list,
        decay_unit: tuple,
        m_flips: int,
        m_stagnation: float,
        n_precisions: list,
        n_costs: dict,

        k_mat: float,
        k_mut: float,

        elite: list,

        probability_distributions: dict,
        byzantine_fault_tolerance: int
):
    appr, g_appr = t_appr

    n_bounds = bounds[1][0] - bounds[0][0]
    n_genes = n_bounds + 1
    n_appr = appr[1][0] - appr[0][0]

    bounds_distribution = [0] * n_bounds
    pb_dist = 1 / n_bounds
    for x in range(appr[0][0], appr[1][0]):
        bounds_distribution[x] = pb_dist

    (appr_lower, _), (appr_upper, _) = appr
    i_bounds = Interval([bounds])
    useful_probes_range = Interval([x for x, _ in alert_costs])
    useful_probes_range &= Interval([((appr_lower - (time - 1), False), (appr_upper + (time - 1), True))])
    useful_probes_range = {
        u: (useful_probes_range + ((-(u - 1), False), ((u - 1), True))) & i_bounds
        for u, _ in n_precisions
    }
    n_useful_probes = {u: useful_probes_range[u].size() + len(useful_probes_range[u])  for u, _ in n_precisions}

    dynamic_fitness = {}

    zero_probes = [(u, [False] * n_genes) for u, _ in n_precisions]

    # Generate and evaluate
    pool = [
        [(u, generate(useful_probes_range[u], n_genes, n, n_useful_probes[u])) for u, n in n_precisions]
        for _ in range(n_pool - len(elite) - 1)
    ] + elite + [zero_probes]
    fitness = []
    for nucleus in pool:
        fitness_key = tuple((u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in nucleus)
        if fitness_key not in dynamic_fitness:
            dynamic_fitness[fitness_key] = evaluate(
                time=time,
                appr=appr,
                cost_table=cost_table,
                bounds=bounds,
                alert_costs=alert_costs,
                decay_unit=decay_unit,
                nucleus=nucleus,
                n_costs=n_costs,

                probability_distributions=probability_distributions,
                byzantine_fault_tolerance=byzantine_fault_tolerance,

                bounds_distribution=bounds_distribution,

                intervals=[appr]
            )[0]
        fitness += [dynamic_fitness[fitness_key]]

    # Select
    pool = [pool[x[0]] for x in sorted(enumerate(fitness), key=lambda x: x[1])]
    fitness.sort()

    # Update test
    prev_best = fitness[0]
    stagnation_counter = 0
    n_nucleus = len(n_precisions)

    # Test
    while stagnation_counter < m_stagnation and fitness[0] != 0:
        # Mate and accepting new offspring
        for x in range(n_sel, n_pool - 1, 2):
            for y in range(n_nucleus):
                if random() < x / n_pool:
                    mate(pool[x][y][1], pool[x + 1][y][1])

        # Mutate and accepting new offspring
        for x in range(n_sel, n_pool):
            for y in range(n_nucleus):
                if random() < x / n_pool:
                    mutate(pool[x][y][1], useful_probes_range, n_appr, k_mut)

        # The worst nucleus gets replaced by 'zero probes'
        pool[-1] = zero_probes

        # Evaluate
        fitness = []
        for nucleus in pool:
            fitness_key = tuple((u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in nucleus)
            if fitness_key not in dynamic_fitness:
                dynamic_fitness[fitness_key] = evaluate(
                    time=time,
                    appr=appr,
                    cost_table=cost_table,
                    bounds=bounds,
                    alert_costs=alert_costs,
                    decay_unit=decay_unit,
                    nucleus=nucleus,
                    n_costs=n_costs,

                    probability_distributions=probability_distributions,
                    byzantine_fault_tolerance=byzantine_fault_tolerance,

                    bounds_distribution=bounds_distribution,

                    intervals=[appr]
                )[0]
            fitness += [dynamic_fitness[fitness_key]]

        # Select
        pool = [pool[x[0]] for x in sorted(enumerate(fitness), key=lambda x: x[1])]
        fitness.sort()

        # Update test
        next_best = fitness[0]
        if prev_best == next_best:
            stagnation_counter += 1
        else:
            stagnation_counter = 0
        prev_best = next_best
        #print('')

        if len(dynamic_fitness) is 1000000:
            dynamic_fitness[:] = dynamic_fitness[100000:]

    elite[:] = pool[:m_tops]

    for x in g_appr:
        cost_table[(time, x)] = []

    for nucleus in elite:
        comb = [(u, [pos for pos, cond in enumerate(comb) if cond]) for u, comb in nucleus]
        results = evaluate(
            time=time,
            appr=appr,
            cost_table=cost_table,
            bounds=bounds,
            alert_costs=alert_costs,
            decay_unit=decay_unit,
            nucleus=nucleus,
            n_costs=n_costs,

            probability_distributions=probability_distributions,
            byzantine_fault_tolerance=byzantine_fault_tolerance,

            bounds_distribution=bounds_distribution,

            intervals=g_appr
        )
        for x, y in zip(g_appr, results):
            cost_table[(time, x)] += [(comb, y)]

def extrapolate(
        appr: tuple,
        time: int,
        cost_table: dict,
        decay_unit: tuple,
        t_minus_1: int,
        i_bounds: Interval
):
    i_appr = Interval([appr])

    min_cost = inf
    for x in i_appr.range():
        if (time, x) in cost_table:
            nucleus, cost = cost_table[(time, x)][0]
            nucleus_minus, _ = cost_table[(t_minus_1, ((Interval([x]) + decay_unit) & i_bounds)[0])][0]
            if len(nucleus_minus) is 0 and len(nucleus) is 0 and cost < min_cost:
                min_cost = cost

    useless_range = Interval([])
    for x in i_appr.range():
        if (time, x) in cost_table and cost_table[(time, x)][0][1] == min_cost:
            useless_range |= Interval([x])

    if len(useless_range) is 0:
        return appr, [appr]

    else:
        i_appr &= ~useless_range
        intervals = []
        s_appr = i_appr[0]

        while s_appr[1] <= appr[1]:
            s_appr = (i_appr[0][0], s_appr[1])
            while appr[0] <= s_appr[0]:
                if (time, s_appr) not in cost_table:
                    intervals += [s_appr]
                s_appr = ((s_appr[0][0] - (not s_appr[0][1]), not s_appr[0][1]), s_appr[1])
            s_appr = (s_appr[0], (s_appr[1][0] + s_appr[1][1], not s_appr[1][1]))

        return appr, intervals
def multi_search(
        k_appr: list,
        l_appr: dict,
        time: int,
        cost_table: dict,
        n_pool: int,
        m_tops: int,
        n_sel: int,
        bounds: tuple,
        alert_costs: list,
        decay_unit: tuple,
        m_flips: int,
        m_stagnation: float,
        n_precisions: list,
        n_costs: dict,

        k_mat: float,
        k_mut: float,

        probability_distributions: dict,
        byzantine_fault_tolerance: int
):
    elite = []

    for x in k_appr:
        t_appr = (x, l_appr[x])
        search(
            time=time,
            t_appr=t_appr,
            cost_table=cost_table,
            n_pool=n_pool,
            m_tops=m_tops,
            n_sel=n_sel,
            bounds=bounds,
            alert_costs=alert_costs,
            decay_unit=decay_unit,
            m_stagnation=m_stagnation,
            m_flips=m_flips,
            n_precisions=n_precisions,
            n_costs=n_costs,

            k_mat=k_mat,
            k_mut=k_mut,
            elite=elite,

            probability_distributions=probability_distributions,
            byzantine_fault_tolerance=byzantine_fault_tolerance
        )
def build(
    name: str,

    bounds: tuple,

    alert_costs: list,
    decay_unit: tuple,

    computation_rate: int,
    m_stagnation: float,
    m_flips: int,
    n_pool: int,
    m_tops: int,
    n_sel: int,
    n_precisions: list,
    n_costs: dict,

    k_mat: float,
    k_mut: float,

    probability_distributions: dict,
    byzantine_fault_tolerance: int
):
    start = timer.time()

    cost_table = {
        (0, x): [('', 0)]
        for x in Interval([bounds]).range()
    }

    partitions = [(Interval([x]), c) for x, c in alert_costs]
    partitions += [(~Interval([x for x, _ in alert_costs]), 0)]
    i_bounds = Interval([bounds])
    for time in range(1, computation_rate + 1):
        time_minus_1 = time - 1
        l_appr = {}
        excluded = []

        # Get well known costs
        for x in i_bounds.range():
            xi = Interval([x])
            if 0 < len(cost_table[(time_minus_1, ((xi + decay_unit) & i_bounds)[0])][0][0]) and 0 < x[1][0] - x[0][0]:
                continue
            for i, c in partitions:
                if xi not in i:
                    continue
                x_minus_1 = ((xi + decay_unit) & i_bounds)[0]
                cost_table[(time, x)] = [([], cost_table[(time_minus_1, x_minus_1)][0][1] + c)]
                excluded += [x]

        for appr in reversed(sorted(
            Interval([bounds]).range(),
            key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(x[1][1])
        )):
            if appr not in excluded:
                appr, intervals = extrapolate(
                    appr=appr,
                    time=time,
                    cost_table=cost_table,
                    decay_unit=decay_unit,
                    t_minus_1=time_minus_1,
                    i_bounds=i_bounds
                )
                l_appr[appr] = intervals
                excluded += intervals

        d_appr = {}
        for x in l_appr:
            lower_key = (x[0], False)
            if lower_key not in d_appr:
                d_appr[lower_key] = []
            d_appr[lower_key] += [x]

            upper_key = (x[1], True)
            if upper_key not in d_appr:
                d_appr[upper_key] = []
            d_appr[upper_key] += [x]

        k_appr = sorted(d_appr.values(), key=lambda x: len(x), reverse=True)

        excluded = []
        x_deleted = 0
        for x in range(len(k_appr)):
            x -= x_deleted
            y_deleted = 0
            for y in range(len(k_appr[x])):
                y -= y_deleted
                if k_appr[x][y] in excluded:
                    del k_appr[x][y]
                    y_deleted += 1
                    if len(k_appr[x]) is 0:
                        del k_appr[x]
                        x_deleted += 1
                        break
                else:
                    excluded += [k_appr[x][y]]

        for x in range(len(k_appr)):
            k_appr[x].sort(key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(x[1][1]))

        end = timer.time()
        print('extra: ' + str(end - start))
        start = timer.time()


        with open('../share/' + name + '_bla' + str(time) + '.csv', 'w') as file:
            writer = csv.writer(
                file,
                escapechar='\\',
                lineterminator='\n',
                delimiter=';',
                quoting=csv.QUOTE_NONE
            )
            for x in l_appr.values():
                writer.writerow(x)

        # context = partial(
        #     multi_search,
        #
        #     l_appr=l_appr,
        #
        #     time=time,
        #     cost_table=cost_table,
        #     n_pool=n_pool,
        #     m_tops=m_tops,
        #     n_sel=n_sel,
        #     bounds=bounds,
        #     alert_costs=alert_costs,
        #     decay_unit=decay_unit,
        #     m_stagnation=m_stagnation,
        #     m_flips=m_flips,
        #     n_precisions=n_precisions,
        #     n_costs=n_costs,
        #
        #     k_mat=k_mat,
        #     k_mut=k_mut,
        #
        #     probability_distributions=probability_distributions,
        #     byzantine_fault_tolerance=byzantine_fault_tolerance
        # )
        # with Pool(processes=cpu_count()) as pool:
        #     pool.map(context, k_appr)
        for x in k_appr:
            multi_search(
                k_appr=x,
                l_appr=l_appr,

                time=time,
                cost_table=cost_table,
                n_pool=n_pool,
                m_tops=m_tops,
                n_sel=n_sel,
                bounds=bounds,
                alert_costs=alert_costs,
                decay_unit=decay_unit,
                m_stagnation=m_stagnation,
                m_flips=m_flips,
                n_precisions=n_precisions,
                n_costs=n_costs,

                k_mat=k_mat,
                k_mut=k_mut,

                probability_distributions=probability_distributions,
                byzantine_fault_tolerance=byzantine_fault_tolerance
            )

        end = timer.time()
        print(end - start)
        start = timer.time()

        with open('../share/' + name + '_readable_cost_table_t_minus_' + str(time) + '_minutes.csv', 'w') as file:
            writer = csv.writer(
                file,
                escapechar='\\',
                lineterminator='\n',
                quoting=csv.QUOTE_NONE
            )
            writer.writerow(
                ['time till done', 'interval', 'probes', 'cost', 'probes', 'cost', 'probes', 'cost',
                 'probes',
                 'cost', 'probes', 'cost'])
            for c, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
                t, ((k_lower, k_open), (k_upper, k_closed)) = c
                i = (
                    ('{' + str(k_lower) + '}')
                    if not k_open and k_closed and k_lower == k_upper
                    else
                    (
                            ('(' if k_open else '[') +
                            str(float(k_lower)) +
                            '..' +
                            str(float(k_upper)) +
                            (']' if k_closed else ')')
                    )
                )
                writer.writerow([t] + [i] + [
                    x
                    for probes, cost in row_value
                    for x in [' '.join([
                        str(u) + '(' + ' '.join([str(pos) for pos in comb]) + ')'
                        for u, comb in probes
                    ]), cost]
                ])

    with open('../share/' + name + '_cost_table_t_minus_' + str(computation_rate) + '_minutes.csv', 'w') as file:
        writer = csv.writer(
            file,
            escapechar='\\',
            lineterminator='\n',
            delimiter=';',
            quoting=csv.QUOTE_NONE
        )
        for c, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
            writer.writerow([c, row_value])

    # time += computation_rate

    return cost_table
def test():
    import time as timer
    from submarine import Parameters

    time = 2
    appr = ((0, False), (50, False)) # [0..50)
    n_appr = appr[1][0] - appr[0][0]

    cost_table = {
        (0, x): [('', 0)]
        for x in Interval([Parameters.bounds]).range()
    }
    nucleus = [
        (3, [False] * (Interval([Parameters.bounds]).size() + 1)),
        (5, [False] * (Interval([Parameters.bounds]).size() + 1))
    ]
    for pos in []:
        nucleus[0][1][pos] = True
    for pos in [44, 45, 50]:
        nucleus[1][1][pos] = True

    n_genes = (Parameters.bounds[1][0] - Parameters.bounds[0][0]) + 1

    print('Initial settings: ' + Parameters.__repr__())
    print('appr: ' + str(appr))
    print('k time minus: ' + str(time))
    print('Set of probes: ' + ' , '.join([str(Interval([((x - 5 ,True), (x + 5,False))])) for x in [44, 45, 50]]))

    n_bounds = Parameters.bounds[1][0] - Parameters.bounds[0][0]
    bounds_distribution = [0] * n_bounds
    pb_dist = 1 / n_bounds
    for x in range(appr[0][0], appr[1][0]):
        bounds_distribution[x] = pb_dist

    start = timer.time()
    print(evaluate(
        time=time,
        appr=appr,
        cost_table=cost_table,
        bounds=Parameters.bounds,
        alert_costs=Parameters.alert_costs,
        decay_unit=Parameters.decay_unit,
        nucleus=nucleus,
        n_costs=Parameters.n_costs,

        probability_distributions = {},
        byzantine_fault_tolerance = 0,

        bounds_distribution=bounds_distribution,

        intervals=[appr]
    ))
    end = timer.time()
    print(end - start)

    # start = timer.time()
    # search(
    #     time=time,
    #     t_appr=(appr, [appr]),
    #     cost_table=cost_table,
    #     n_pool=Parameters.n_pool,
    #     m_tops=Parameters.m_tops,
    #     n_sel=Parameters.n_sel,
    #     bounds=Parameters.bounds,
    #     alert_costs=Parameters.alert_costs,
    #     decay_unit=Parameters.decay_unit,
    #     m_stagnation=Parameters.m_stagnation,
    #     m_flips=Parameters.m_flips,
    #     n_precisions=Parameters.n_precisions,
    #     n_costs=Parameters.n_costs,
    #     k_mat=Parameters.k_mat,
    #     k_mut=Parameters.k_mut,
    #     elite=[],
    #
    #     probability_distributions={},
    #     byzantine_fault_tolerance=0
    # )
    # print(cost_table[(time, appr)])
    # end = timer.time()
    # print(end - start)

    quit(0)