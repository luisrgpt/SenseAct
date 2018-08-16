# coding=utf-8
from intervals import Interval, random_interval
from random import random, randint, randrange, choice

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
        n_appr: int,
        cost_table: dict,
        n_pool: int,
        m_tops: int,
        n_sel: int,
        bounds: tuple,
        alert_costs: list,
        decay_unit: tuple,
        m_flips: int,
        m_stagnation: float,
        nucleus: list,
        n_precisions: list,
        n_costs: dict,
        n_genes: int,

        k_mat: float,
        k_mut: float
):
    (d_lower, d_open), (d_upper, d_closed) = decay_unit
    minus_1 = time - 1
    no = Interval([appr])
    no_prob = 1

    probes = [(x, i) for i, comb in nucleus for x in range(max(appr[0][0] - i, bounds[0][0]), min(appr[1][0] + i + 1, bounds[1][0])) if comb[x]]
    probes.sort(key=lambda x: x[0] - x[1])

    probe_cost = 0
    groups = []
    intersection_groups = []
    for x, i in probes:
        probe_cost += n_costs[i]

        in_groups = False
        x_l = x - i
        x_h = x + i
        for y in range(len(groups)):
            endpoints = groups[y]
            l = 1

            if x_l < endpoints[0]:
                #print(str(x_l) + ' ' + str(intersection_groups) + ' ' + str(groups), end='')
                groups[y][:0] += [x_l]
                intersection_groups[y][:0] += [0]
                in_groups = True
                #print(' <0< ' + str(intersection_groups) + ' ' + str(groups), end='')

            elif x_l == endpoints[0]:
                #print(str(x_l) + ' ' + str(intersection_groups) + ' ' + str(groups), end='')
                in_groups = True
                #print(' =0= ' + str(intersection_groups) + ' ' + str(groups), end='')

            elif endpoints[0] < x_l < endpoints[1]:
                #print(str(x_l) + ' ' + str(intersection_groups) + ' ' + str(groups), end='')
                groups[y][0:1] += [x_l]
                intersection_groups[y] += [intersection_groups[y][0]]
                in_groups = True
                #print(' >0> ' + str(intersection_groups) + ' ' + str(groups), end='')

            elif endpoints[-1] == x_l:
                #print(str(x_l) + ' ' + str(intersection_groups) + ' ' + str(groups), end='')
                groups[y] += [x_l]
                intersection_groups[y] += [intersection_groups[y][-1]]
                in_groups = True
                #print(' =-1= ' + str(intersection_groups) + ' ' + str(groups), end='')

            else:
                for z in range(1, len(endpoints) - 1):
                    l += 1

                    if endpoints[z] == x_l:
                        #print(str(x_l) + ' ' + str(intersection_groups) + ' ' + str(groups), end='')
                        groups[y][z - 1:z] += [x_l]
                        intersection_groups[y][z - 1:z] += [intersection_groups[y][z]]
                        in_groups = True
                        #print(' = ' + str(intersection_groups) + ' ' + str(groups), end='')
                        break

                    elif endpoints[z] < x_l < endpoints[z + 1]:
                        #print(str(x_l) + ' ' + str(intersection_groups) + ' ' + str(groups), end='')
                        groups[y][z:z + 1] += [x_l]
                        intersection_groups[y][z - 1:z] += [intersection_groups[y][z]]
                        in_groups = True
                        #print(' > ' + str(intersection_groups) + ' ' + str(groups), end='')
                        break

            #print(l)
            if in_groups:
                for z in range(l, len(endpoints)):
                    if x_h < endpoints[z]:
                        groups[y][z - 1:z] += [x_h]
                        intersection_groups[y][z - 2:z - 1] += [intersection_groups[y][z - 1]]
                        intersection_groups[y][z - 1] += 1
                        #print(' -<> ' + str(intersection_groups) + ' ' + str(groups), end='')
                        break

                    elif x_h == endpoints[z]:
                        groups[y][z - 1:z] += [x_h]
                        intersection_groups[y][z - 2:z - 1] += [intersection_groups[y][z - 1]]
                        intersection_groups[y][z - 1] += 1
                        intersection_groups[y][z] += 2
                        #print(' -==> ' + str(intersection_groups) + ' ' + str(groups), end='')
                        break

                    else:
                        if z == len(endpoints) - 1:
                            groups[y] += [x_h]
                            intersection_groups[y][z - 1] += 1
                            intersection_groups[y] += [0]
                            #print(' ->> ' + str(intersection_groups) + ' ' + str(groups), end='')
                break

        if not in_groups:
            groups += [[x_l, x_h]]
            intersection_groups += [[0]]
            #print(str(x_l) + ' new ' + str(intersection_groups) + ' ' + str(groups), end='')

        #print('')
    total_cost = probe_cost

    for endpoints, intersections in zip(groups, intersection_groups):
        for x in range(len(endpoints) - 1):
            yes = (
                (endpoints[x], x == 0 or intersections[x - 1] < intersections[x]),
                (endpoints[x + 1], x < len(endpoints) - 2 and intersections[x] < intersections[x + 1])
            )
            if (yes if yes[0] <= appr[0] else appr)[1] <= (yes if appr[1] <= yes[1] else appr)[0]:
                continue

            appr_yes = (max(yes[0], appr[0]), min(yes[1], appr[1]))
            yes_prob = (appr_yes[1][0] - appr_yes[0][0]) / n_appr
            if yes_prob == 0:
                continue

            no.remove(appr_yes)
            alert_cost = 0
            for x, cost in alert_costs:
                if alert_cost < cost and (appr_yes if x[1] <= appr_yes[1] else x)[0] < (appr_yes if appr_yes[0] <= x[0] else x)[1]:
                    alert_cost = cost

            delayed_yes = (
                (appr_yes[0][0] + d_lower, appr_yes[0][1] or d_open),
                (appr_yes[1][0] + d_upper, appr_yes[1][1] and d_closed)
            )
            bounded_yes = (max(delayed_yes[0], bounds[0]), min(delayed_yes[1], bounds[1]))
            if str((minus_1, bounded_yes)) not in cost_table:
                search(
                    time=minus_1,
                    appr=bounded_yes,
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
                    k_mut=k_mut
                )

            wait_cost = min(cost_table[str((minus_1, bounded_yes))].values())
            total_cost += yes_prob * (alert_cost + wait_cost)
            no_prob -= yes_prob

    alert_cost = 0
    wait_cost = 0
    for x in no:
        for y, cost in alert_costs:
            if alert_cost < cost and (x if y[1] <= x[1] else y)[0] < (x if x[0] <= y[0] else y)[1]:
                alert_cost = cost

        delayed_x = ((x[0][0] + d_lower, x[0][1] or d_open), (x[1][0] + d_upper, x[1][1] and d_closed))
        bounded_x = (max(delayed_x[0], bounds[0]), min(delayed_x[1], bounds[1]))
        if str((minus_1, bounded_x)) not in cost_table:
            search(
                time=minus_1,
                appr=bounded_x,
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
                k_mut=k_mut
            )
        wait_cost += min(cost_table[str((minus_1, bounded_x))].values())
    total_cost += no_prob * (alert_cost + wait_cost)

    # Debug
    # if total_cost > 0 and len(groups) is not 0:
    # # if len(groups) is not 0:
    #     print('')
    #     print('appr: ' + str(appr))
    #     print('pro: ' + str(probe_cost))
    #     print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')' for u, comb in nucleus]) + ' ' + ' '.join([str(endpoints[0]) + '..' + ','.join([str(x) for x in endpoints[1:]]) for endpoints in groups]))
    #     no = Interval([appr])
    #     # print(no, end='')
    #     for endpoints, intersections in zip(groups, intersection_groups):
    #         for x in range(len(endpoints) - 1):
    #             yes = (
    #                 (endpoints[x], x == 0 or intersections[x - 1] < intersections[x]),
    #                 (endpoints[x + 1], x < len(endpoints) - 2 and intersections[x] < intersections[x + 1])
    #             )
    #             if (yes if yes[0] <= appr[0] else appr)[1] <= (yes if appr[1] <= yes[1] else appr)[0]:
    #                 print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')' for u, comb in nucleus]) + ' yes: ' + str(
    #                     (time, Interval([yes]))) + ' -> ' + str(
    #                     (time, Interval([]))) + ' -> 0')
    #                 continue
    #             appr_yes = (max(yes[0], appr[0]), min(yes[1], appr[1]))
    #             no.remove(yes)
    #             yes_prob = (appr_yes[1][0] - appr_yes[0][0]) / n_appr
    #             if yes_prob == 0:
    #                 print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')' for u, comb in nucleus]) + ' yes: ' + str(
    #                     (time, Interval([yes]))) + ' -> ' + str(
    #                     (time, Interval([appr_yes]))) + ' -> 0', end='')
    #                 print(' ------------------- no : ' + str(no))
    #                 continue
    #             y_alert_cost = 0
    #             for x, cost in alert_costs:
    #                 if y_alert_cost < cost and (appr_yes if x[1] <= appr_yes[1] else x)[0] < \
    #                         (appr_yes if appr_yes[0] <= x[0] else x)[1]:
    #                     y_alert_cost = cost
    #             delayed_x = ((appr_yes[0][0] + d_lower, appr_yes[0][1] or d_open), (appr_yes[1][0] + d_upper, appr_yes[1][1] and d_closed))
    #             bounded_x = (max(delayed_x[0], bounds[0]), min(delayed_x[1], bounds[1]))
    #             wait_cost = min(cost_table[str((minus_1, bounded_x))].values())
    #             print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')' for u, comb in nucleus]) + ' yes: ' + str(
    #                 (time, Interval([yes]))) + ' -> cost-table(' + str(
    #                 (minus_1, Interval([bounded_x]))) + ') -> (' + str(y_alert_cost) + ' + ' + str(
    #                 wait_cost) + ') * (' + str(int(yes_prob * n_appr)) + ' / ' + str(n_appr) + ') = ' + str(
    #                 yes_prob * (y_alert_cost + wait_cost)), end='')
    #             print(' ------------------- no : ' + str(no))
    #             # print(' - [' + str(l) + '..' + str(h) + '] -> ' + str(no), end='')
    #     # print(' -> ' + str(no))
    #     print(','.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')' for u, comb in nucleus]) + ' no : ' + str((time, no)) + ' -> cost-table(' + str((minus_1, no + decay_unit)) + ') -> (' + str(alert_cost) + ' + ' + str(wait_cost) + ') * (' + str(int(no_prob * n_appr))  + ' / ' + str(n_appr) + ') = ' + str(no_prob * (alert_cost + wait_cost)))

    return total_cost
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
        nucleus: list,
        useful_probes_range: dict,
        n_appr: int,
        m_flips: int
):
    n_probes = sum(1 for _, chromosome in nucleus for x in chromosome if x)

    # Assuming m_flips is always greater than 0
    if n_probes/n_appr * 1.1 < random():
        probes = [(k, pos, u) for k, (u, chromosome) in enumerate(nucleus) for pos, cond in enumerate(chromosome) if not cond]

        # For each number of flips
        for _ in range(randint(1, m_flips)):
            # Repeat until gene is false and inside useful probe range
            x = choice(probes)
            while x[1] not in useful_probes_range[x[2]]:
                x = choice(probes)
            # Flip value
            nucleus[x[0]][1][x[1]] = True
    else:
        probes = [(k, pos) for k, (_, chromosome) in enumerate(nucleus) for pos, cond in enumerate(chromosome) if cond]

        # For each number of flips
        for _ in range(randint(1, m_flips)):
            if n_probes is 0:
                break
            n_probes -= 1
            x = choice(probes)
            probes.remove(x)
            # Flip value
            nucleus[x[0]][1][x[1]] = False
def search(
        time: int,
        appr: tuple,
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
        k_mut: float
):
    #elite = [
    #    y
    #    for x in appr
    #    for y in cost_table[str((time - 1, x))].values()
    #]
    # Genetic search is useless if the appr is degenerated
    n_genes = (bounds[1][0] - bounds[0][0]) + 1

    useful_probes_range = Interval([x for x, _ in alert_costs])
    useful_probes_range &= Interval([appr])

    n_appr = appr[1][0] - appr[0][0]
    if useful_probes_range.size() is 0:
        cost_table[str((time, appr))] = {'': 0}
        return

    i_bounds = Interval([bounds])

    useful_probes_range = {u: (useful_probes_range + ((-u, False), (u, True))) & i_bounds for u, _ in n_precisions}
    n_useful_probes = {u: useful_probes_range[u].size() + len(useful_probes_range[u])  for u, _ in n_precisions}

    # Generate and evaluate
    pool = [[(u, generate(useful_probes_range[u], n_genes, n, n_useful_probes[u])) for u, n in n_precisions] for _ in range(n_pool)] + [[(u, [False] * n_genes) for u, _ in n_precisions]]
    fitness = [
        evaluate(
            time=time,
            appr=appr,
            n_appr=n_appr,
            cost_table=cost_table,
            n_pool=n_pool,
            m_tops=m_tops,
            n_sel=n_sel,
            bounds=bounds,
            alert_costs=alert_costs,
            decay_unit=decay_unit,
            m_stagnation=m_stagnation,
            m_flips=m_flips,
            nucleus=nucleus,
            n_precisions=n_precisions,
            n_costs=n_costs,
            n_genes=n_genes,
            k_mat=k_mat,
            k_mut=k_mut
        )
        for nucleus in pool
    ]

    # Select
    pool = [pool[x[0]] for x in sorted(enumerate(fitness), key=lambda x: x[1])]
    fitness.sort()

    # Update test
    prev_best = fitness[0]
    stagnation_counter = 0
    n_nucleus = len(n_precisions)

    # Test
    while stagnation_counter < m_stagnation:
        # Mate and accepting new offspring
        for x in range(n_sel + 1, n_pool - 1, 2):
            for y in range(n_nucleus):
                if random() < k_mat * x / n_pool:
                    mate(pool[x][y][1], pool[x + 1][y][1])

        # Mutate and accepting new offspring
        for x in range(n_sel + 1, n_pool):
            if random() < k_mut * x / n_pool:
                mutate(pool[x], useful_probes_range, n_appr, m_flips)

        # Evaluate
        fitness = [
            evaluate(
                time=time,
                appr=appr,
                n_appr=n_appr,
                cost_table=cost_table,
                n_pool=n_pool,
                m_tops=m_tops,
                n_sel=n_sel,
                bounds=bounds,
                alert_costs=alert_costs,
                decay_unit=decay_unit,
                m_stagnation=m_stagnation,
                m_flips=m_flips,
                nucleus=nucleus,
                n_precisions=n_precisions,
                n_costs=n_costs,
                n_genes=n_genes,
                k_mat=k_mat,
                k_mut=k_mut
            )
            for nucleus in pool
        ]

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

    cost_table[str((time, appr))] = {
        ' '.join([str(u) + '(' + ' '.join([str(pos) for pos, cond in enumerate(comb) if cond]) + ')' for u, comb in nucleus]): fit
        for nucleus, fit in zip(pool[:m_tops], fitness[:m_tops])
    }

def test():
    import time as timer
    from submarine import Parameters

    time = 1
    appr = ((0, False), (46, False)) # [0..46)
    n_appr = appr[1][0] - appr[0][0]

    cost_table = {
        str((0, x)): {'': 0}
        for x in Interval([Parameters.bounds]).range()
    }
    nucleus = [(3, [False] * (Interval([Parameters.bounds]).size() + 1)), (5, [False] * (Interval([Parameters.bounds]).size() + 1))]
    for pos in []:
        nucleus[0][1][pos] = True
    for pos in [35, 43, 50]:
        nucleus[1][1][pos] = True

    n_genes = (Parameters.bounds[1][0] - Parameters.bounds[0][0]) + 1

    print('Initial settings: ' + Parameters.__repr__())
    print('appr: ' + str(appr))
    print('k time minus: ' + str(time))
    print('Set of probes: ' + ' , '.join([str(Interval([((x - 5 ,True), (x + 5,False))])) for x in [35, 43, 50]]))

    start = timer.time()
    print(evaluate(
        time=time,
        appr=appr,
        n_appr=n_appr,
        cost_table=cost_table,
        n_pool=Parameters.n_pool,
        m_tops=Parameters.m_tops,
        n_sel=Parameters.n_sel,
        bounds=Parameters.bounds,
        alert_costs=Parameters.alert_costs,
        decay_unit=Parameters.decay_unit,
        m_stagnation=Parameters.m_stagnation,
        m_flips=Parameters.m_flips,
        nucleus=nucleus,
        n_precisions=Parameters.n_precisions,
        n_costs=Parameters.n_costs,
        n_genes=n_genes,
        k_mat=Parameters.k_mat,
        k_mut=Parameters.k_mut
    ))
    end = timer.time()
    print(end - start)

