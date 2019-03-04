# coding=utf-8
############################################################










############################################################
from intervals import Interval, intersects
from random import random, randint
from math import inf, log
from copy import deepcopy
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from functools import partial
import time as timer
import csv
############################################################










############################################################
def generate(
        useful_probes_range: Interval,
        n_genes: int,
        generation_number_of_initial_probes: int,
        n_useful_probes: int
):
    pb_gen = generation_number_of_initial_probes / n_useful_probes
    return [
        x in useful_probes_range and random() < pb_gen
        for x in range(n_genes)
    ]
############################################################










############################################################
def evaluate(
        time: int,
        cost_table: dict,
        boundaries: tuple,
        alert_catalog: list,
        trajectory_speed: float,
        nucleus: list,
        sensor_catalog: dict,

        sensor_success_rate_area: dict,
        byzantine_fault_tolerance: int,

        boundaries_distributions: list,

        answer_intervals: list,

        convert: bool = True
):
    ((b_lower, b_open), (b_upper, b_closed)) = boundaries

    if convert:
        probes = [(x, i) for i, comb in nucleus for x in range(b_lower, b_upper) if comb[x]]
    else:
        probes = [(x, i) for i, comb in nucleus for x in comb]
    probes.sort(key=lambda x: x[0] - x[1])

    # From probes, define amount of endpoints per unit space and probe cost
    sensor_cost = 0
    lefties = [0] * (b_upper - b_lower + 1)
    righties = [0] * (b_upper - b_lower + 1)
    for x, i in probes:
        sensor_cost += sensor_catalog[i]
        lefties[max(x - i, b_lower)] += 1
        righties[min(x + i, b_upper)] += 1


    total_costs = [sensor_cost] * len(answer_intervals)

    # From endpoints per unit space, define claims
    endpoints = []
    claims = [0]
    for i, l, r in zip(range(b_lower, b_upper), lefties, righties):
        change = l - r
        if change is not 0:
            endpoints += i
            claims += [claims[-1] + change]
    endpoints += [None]
    claims = claims[1:] + [0]

    # From claims, define certainties
    lowers = []
    uppers = []
    previous_claim = 0
    current_claim = 0
    for e_upper, claim in zip(endpoints, claims):
        endpoint = (e_lower, current_claim < claim)
        if current_claim is not 0:
            lowers += [endpoint]
        if previous_claim is not 0:
            uppers += [endpoint]
        previous_claim = current_claim
        current_claim = claim
        e_lower = e_upper

    # From certainties, define uncertainties and confirmation cost
    minus_1 = time - 1
    noes = [Interval([s_answer_intervals]) for s_answer_intervals in answer_intervals]
    no_probs = [1] * len(answer_intervals)
    for yes_lower, yes_upper in enumerate(lowers, uppers):
        for index, (i_lower, i_upper) in enumerate(answer_intervals):
            # Filter non-intersections
            if not intersects((yes_lower, yes_upper), (i_lower, i_upper)):
                continue

            answer_intervals_yes = (max(yes_lower, i_lower), min(yes_upper, i_upper))
            ((x_lower, x_open), (x_upper, x_closed)) = answer_intervals_yes
            certainty_probability = sum(boundaries_distributions[index][int(x_lower):int(x_upper)])

            # Filter impossibilities
            if certainty_probability == 0:
                if 1 < claims[x]:
                    noes[index].remove(answer_intervals_yes)
                continue

            # Get alert cost
            alert_cost = next(cost for z, cost in alert_catalog if intersects(answer_intervals_yes, z))

            # Get wait cost
            next_unit_time = minus_1
            next_knowledge_space = (
                (x_lower - trajectory_speed, x_open  ),
                (x_upper + trajectory_speed, x_closed)
            )
            wait_cost = cost_table[(next_unit_time, next_knowledge_space)][0][1]

            #
            total_costs[index] += certainty_probability * (alert_cost + wait_cost)

            noes[index].remove(answer_intervals_yes)
            no_probs[index] -= certainty_probability

    # From uncertainties, define denial cost
    for (index, uncertainty_space), uncertainty_probability in zip(enumerate(noes), no_probs):
        # Filter impossibilities
        if uncertainty_probability == 0:
            continue

        # Get alert cost
        alert_cost = next(cost for x, cost in alert_catalog for y in uncertainty_space if intersects(x, y))

        # Get wait cost
        wait_cost = 0
        for ((uncertainty_lower, uncertainty_open), (uncertainty_upper, uncertainty_closed)) in uncertainty_space:
            # Filter impossibilities
            x_probability = sum(boundaries_distributions[index][int(uncertainty_lower):int(uncertainty_upper)]) / uncertainty_probability
            if x_probability == 0:
                continue

            # Get wait cost
            next_unit_time = minus_1
            next_knowledge_space = (
                (uncertainty_lower - trajectory_speed, uncertainty_open),
                (uncertainty_upper + trajectory_speed, uncertainty_closed)
            )
            wait_cost += x_probability * cost_table[(next_unit_time, next_knowledge_space)][0][1]

        total_costs[index] += uncertainty_probability * (alert_cost + wait_cost)

    return total_costs
############################################################










############################################################
def mate(
        chromosome_1: list,
        chromosome_2: list
):
    # Check if both chromosomes are identical
    if chromosome_1 == chromosome_2:
        return

    # Identify first difference
    min_point = None
    for min_point, _ in enumerate(chromosome_1):
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
############################################################










############################################################
def mutate(
        chromosome: list,
        useful_probes_range: Interval,
        n_answer_intervals: int,
        mutation_probability_of_flipping_bit: float
):
    n_probes = sum(chromosome)

    for ((x_lower, x_open), (x_upper, x_closed)) in useful_probes_range:
        for n in range(x_lower, x_upper + 1):
            r = random()

            if not chromosome[n] and mutation_probability_of_flipping_bit * (n_probes + 1) / n_answer_intervals < r:
                chromosome[n] = True
            elif chromosome[n] and mutation_probability_of_flipping_bit * (1 - n_probes / n_answer_intervals) < r:
                chromosome[n] = False
############################################################










############################################################
def search(
        t_answer_intervals: tuple,
        time: int,
        cost_table: dict,
        max_size_of_population: int,
        elite_chromosomes: int,
        selection_max_number_of_fit_chromosomes: int,
        boundaries: tuple,
        alert_catalog: list,
        trajectory_speed: float,
        mutation_probability_of_flipping_bit: float,
        stopping_condition: float,
        generation_number_of_initial_probes: list,
        sensor_catalog: dict,

        selection_base_logarithm: float,
        crossover_probability_of_crossover: float,
        mutation_probability_of_mutation: float,

        elite: list,

        sensor_success_rate_area: dict,
        byzantine_fault_tolerance: int
):
    answer_intervals, g_answer_intervals = t_answer_intervals

    n_boundaries = boundaries[1][0] - boundaries[0][0]
    n_genes = n_boundaries + 1
    n_answer_intervals = answer_intervals[1][0] - answer_intervals[0][0]

    boundaries_distributions = [[0] * n_boundaries for _ in enumerate(g_answer_intervals)]
    for x, ((g_lower, _), (g_upper, _)) in enumerate(g_answer_intervals):
        pb_dist = 1 / (g_upper - g_lower)
        for y in range(g_lower, g_upper):
            boundaries_distributions[x][y] = pb_dist

    (answer_intervals_lower, _), (answer_intervals_upper, _) = answer_intervals
    i_boundaries = Interval([boundaries])
    useful_probes_range = Interval([x for x, _ in alert_catalog])
    useful_probes_range &= Interval([((answer_intervals_lower - (time - 1), False), (answer_intervals_upper + (time - 1), True))])
    useful_probes_range = {
        u: (useful_probes_range + (0, u - 1)) & i_boundaries
        for u, _ in generation_number_of_initial_probes
    }
    n_useful_probes = {u: useful_probes_range[u].size() + len(useful_probes_range[u])  for u, _ in generation_number_of_initial_probes}

    dynamic_fitness = {}

    zero_probes = [[(u, [False] * n_genes) for u, _ in generation_number_of_initial_probes]]

    # Generate and evaluate
    pool = [
        [(u, generate(useful_probes_range[u], n_genes, n, n_useful_probes[u])) for u, n in generation_number_of_initial_probes]
        for _ in range(max_size_of_population - len(elite) - 1)
    ] + elite + deepcopy(zero_probes)
    fitness = []
    for nucleus in pool:
        fitness_key = tuple((u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in nucleus)
        if fitness_key not in dynamic_fitness:
            dynamic_fitness[fitness_key] = evaluate(
                time=time,
                cost_table=cost_table,
                boundaries=boundaries,
                alert_catalog=alert_catalog,
                trajectory_speed=trajectory_speed,
                nucleus=nucleus,
                sensor_catalog=sensor_catalog,

                sensor_success_rate_area=sensor_success_rate_area,
                byzantine_fault_tolerance=byzantine_fault_tolerance,

                boundaries_distributions=[boundaries_distributions[-1]],

                answer_intervals=[answer_intervals]
            )[0]
        fitness += [dynamic_fitness[fitness_key]]

    # Select
    pool = [pool[x] for x, _ in sorted(enumerate(fitness), key=lambda x: x[1])]
    fitness.sort()

    # Update test
    prev_best = fitness[selection_max_number_of_fit_chromosomes - 1]
    stagnation_counter = 0

    # Test
    while stagnation_counter < stopping_condition and fitness[0] != 0:
        #old_pool = zero_probes
        old_pool = pool

        pool = pool[:selection_max_number_of_fit_chromosomes]
        for _ in range(selection_max_number_of_fit_chromosomes, max_size_of_population, 2):
            # Select
            nucleus1 = deepcopy(old_pool[min(-int(log(random(), selection_base_logarithm)), len(old_pool))])
            nucleus2 = deepcopy(old_pool[min(-int(log(random(), selection_base_logarithm)), len(old_pool))])

            for (y, _), useful_probes in zip(enumerate(nucleus1), useful_probes_range.values()):
                # Crossover
                if random() < crossover_probability_of_crossover:
                    mate(nucleus1[y][1], nucleus2[y][1])

                # Mutation
                if random() < mutation_probability_of_mutation:
                    mutate(nucleus1[y][1], useful_probes, n_answer_intervals, mutation_probability_of_flipping_bit)
                    mutate(nucleus2[y][1], useful_probes, n_answer_intervals, mutation_probability_of_flipping_bit)

            # Accept
            #print(len([x for x, cond in enumerate(pool[2 - 1][1][1]) if cond]), end=' -> ')
            pool += [nucleus1, nucleus2]
        #print(len([x for x, cond in enumerate(pool[2 - 1][1][1]) if cond]))

        # Mate and accepting new offspring
        #for x in range(selection_max_number_of_fit_chromosomes, max_size_of_population - 1, 2):
        #    for y, _ in enumerate(pool[x]):
        #        if random() < x / max_size_of_population:
        #            mate(pool[x][y][1], pool[x + 1][y][1])

        # Mutate and accepting new offspring
        #for x in range(selection_max_number_of_fit_chromosomes, max_size_of_population):
        #    for (y, _), useful_probes in zip(enumerate(pool[x]), useful_probes_range.values()):
        #        if random() < x / max_size_of_population:
        #            mutate(pool[x][y][1], useful_probes, n_answer_intervals, mutation_probability_of_mutation)

        # Evaluate
        fitness = []
        for nucleus in pool:
            fitness_key = tuple((u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in nucleus)
            if fitness_key not in dynamic_fitness:
                dynamic_fitness[fitness_key] = evaluate(
                    time=time,
                    cost_table=cost_table,
                    boundaries=boundaries,
                    alert_catalog=alert_catalog,
                    trajectory_speed=trajectory_speed,
                    nucleus=nucleus,
                    sensor_catalog=sensor_catalog,

                    sensor_success_rate_area=sensor_success_rate_area,
                    byzantine_fault_tolerance=byzantine_fault_tolerance,

                    boundaries_distributions=[boundaries_distributions[-1]],

                    answer_intervals=[answer_intervals]
                )[0]
            fitness += [dynamic_fitness[fitness_key]]

        # Select
        pool = [pool[x] for x, _ in sorted(enumerate(fitness), key=lambda x: x[1])]
        fitness.sort()

        # Update test
        next_best = fitness[selection_max_number_of_fit_chromosomes - 1]
        if prev_best == next_best:
            stagnation_counter += 1
            fitness_key = tuple((u, tuple(pos for pos, cond in enumerate(comb) if cond)) for u, comb in pool[selection_max_number_of_fit_chromosomes - 1])
            #print(dynamic_fitness[fitness_key])
            #print(str(stagnation_counter) + ' -> ' + str([x for x, cond in enumerate(pool[selection_max_number_of_fit_chromosomes - 1][1][1]) if cond]) + ' -> ' + str(dynamic_fitness[fitness_key]))
        else:
            stagnation_counter = 0
        prev_best = next_best
        #print('')

    elite[:] = pool[:elite_chromosomes]

    for x in g_answer_intervals:
        cost_table[(time, x)] = []

    for nucleus in elite:
        results = evaluate(
            time=time,
            cost_table=cost_table,
            boundaries=boundaries,
            alert_catalog=alert_catalog,
            trajectory_speed=trajectory_speed,
            nucleus=nucleus,
            sensor_catalog=sensor_catalog,

            sensor_success_rate_area=sensor_success_rate_area,
            byzantine_fault_tolerance=byzantine_fault_tolerance,

            boundaries_distributions=boundaries_distributions,

            answer_intervals=g_answer_intervals
        )
        comb = [(u, [pos for pos, cond in enumerate(comb) if cond]) for u, comb in nucleus]
        for x, y in zip(g_answer_intervals, results):
            cost_table[(time, x)] += [(comb, y)]
############################################################










############################################################
def extrapolate(
        answer_intervals: tuple,
        excluded: list,
        partitions: list
):
    (a_left, a_right) = answer_intervals
    ((a_lower, _), (a_upper, _)) = answer_intervals
    i_answer_intervals = Interval([answer_intervals])

    alert_cost = inf
    useless_range = []
    for ((x_lower, _), (x_upper, _)), cost in partitions:
        x = ((x_lower, True), (x_upper, False))
        if cost < alert_cost and intersects(answer_intervals, x):
            alert_cost = cost
            useless_range = [x]
        elif cost == alert_cost:
            useless_range += [x]
    useless_range = Interval(useless_range)
    # print(str((a_lower, a_upper)) + ' -> ' + str(useless_range))

    answer_intervals = []
    if len(useless_range) is 0:
        answer_intervals += [answer_intervals]

    else:
        i_answer_intervals &= ~useless_range
        i_answer_intervals = i_answer_intervals[0]
        ((i_a_lower, i_a_open), (i_a_upper, i_a_closed)) = i_answer_intervals

        if i_a_upper == a_upper:
            s_left = (i_a_lower - 1, True)
            while a_left <= s_left:
                s_answer_intervals = (s_left, a_right)
                if s_answer_intervals not in excluded:
                    answer_intervals += [s_answer_intervals]
                (s_lower, s_open) = s_left
                s_left = (s_lower - (not s_open), not s_open)

        elif a_lower == i_a_lower:
            s_right = (i_a_upper + 1, False)
            while s_right <= a_right:
                s_answer_intervals = (a_left, s_right)
                if s_answer_intervals not in excluded:
                    answer_intervals += [s_answer_intervals]
                (s_upper, s_closed) = s_right
                s_right = (s_upper + s_closed, not s_closed)

        else:
            s_right = (i_a_upper + 1, False)
            while s_right <= a_right:
                s_left = (i_a_lower - 1, True)
                while a_left <= s_left:
                    s_answer_intervals = (s_left, s_right)
                    if s_answer_intervals not in excluded:
                        answer_intervals += [s_answer_intervals]
                    (s_lower, s_open) = s_left
                    s_left = (s_lower - (not s_open), not s_open)
                (s_upper, s_closed) = s_right
                s_right = (s_upper + s_closed, not s_closed)

    return answer_intervals
############################################################










############################################################
def multi_search(
        k_answer_intervals: list,
        l_answer_intervals: dict,
        time: int,
        cost_table: dict,
        max_size_of_population: int,
        elite_chromosomes: int,
        selection_max_number_of_fit_chromosomes: int,
        boundaries: tuple,
        alert_catalog: list,
        trajectory_speed: float,
        mutation_probability_of_flipping_bit: float,
        stopping_condition: float,
        generation_number_of_initial_probes: list,
        sensor_catalog: dict,

        selection_base_logarithm: float,
        crossover_probability_of_crossover: float,
        mutation_probability_of_mutation: float,

        sensor_success_rate_area: dict,
        byzantine_fault_tolerance: int
):
    elite = []

    for x in k_answer_intervals:
        #print(str(x) + ' -> ' + str(l_answer_intervals[x][0]))
        t_answer_intervals = (x, l_answer_intervals[x])
        search(
            time=time,
            t_answer_intervals=t_answer_intervals,
            cost_table=cost_table,
            max_size_of_population=max_size_of_population,
            elite_chromosomes=elite_chromosomes,
            selection_max_number_of_fit_chromosomes=selection_max_number_of_fit_chromosomes,
            boundaries=boundaries,
            alert_catalog=alert_catalog,
            trajectory_speed=trajectory_speed,
            stopping_condition=stopping_condition,
            mutation_probability_of_flipping_bit=mutation_probability_of_flipping_bit,
            generation_number_of_initial_probes=generation_number_of_initial_probes,
            sensor_catalog=sensor_catalog,

            selection_base_logarithm=selection_base_logarithm,
            crossover_probability_of_crossover=crossover_probability_of_crossover,
            mutation_probability_of_mutation=mutation_probability_of_mutation,
            elite=elite,

            sensor_success_rate_area=sensor_success_rate_area,
            byzantine_fault_tolerance=byzantine_fault_tolerance
        )
############################################################










############################################################
def build(
        name: str,

        boundaries: tuple,

        alert_catalog: list,
        trajectory_speed: float,

        cost_table_quality: int,
        stopping_condition: float,
        mutation_probability_of_flipping_bit: float,
        max_size_of_population: int,
        elite_chromosomes: int,
        selection_max_number_of_fit_chromosomes: int,
        generation_number_of_initial_probes: list,
        sensor_catalog: dict,

        selection_base_logarithm: float,
        crossover_probability_of_crossover: float,
        mutation_probability_of_mutation: float,

        sensor_success_rate_area: dict,
        byzantine_fault_tolerance: int
):
    start = timer.time()

    cost_table = {
        (0, x): [('', 0)]
        for x in Interval([boundaries]).range()
    }

    i_boundaries = Interval([boundaries])
    (b_left, b_right) = boundaries
    not_alert = [(x, 0) for x in ~Interval([x for x, _ in alert_catalog])]
    alert_partitions = alert_catalog + not_alert
    useless_partitions = alert_partitions[:]
    useful_partitions = alert_catalog[:]
    for time in range(1, cost_table_quality + 1):
        time_minus_1 = time - 1
        excluded = []

        # Get well known costs
        for x in i_boundaries.range():
            ((x_lower, x_open), (x_upper, x_closed)) = x
            if x_upper - x_lower <= 1:
                for  y, c in alert_partitions:
                    if not intersects(x, y):
                        continue
                    _, wait_cost = cost_table[(
                        time_minus_1,
                        (
                            max((x_lower - trajectory_speed, x_open), b_left),
                            min((x_upper + trajectory_speed, x_closed), b_right)
                        )
                    )][0]
                    cost_table[(time, x)] = [([], wait_cost + c)]
                    excluded += [x]
                    # print(str((x_lower, x_upper)) + ' & ' + str((i_lower, i_upper)) + ' -> ' + str(
                    #     cost_table[(time, x_lower, x_upper)]))
                    break
            else:
                for (y_left, y_right), c in useless_partitions:
                    if not (y_left <= (x_lower, x_open) and (x_upper, x_closed) <= y_right):
                        continue
                    _, wait_cost = cost_table[(
                        time_minus_1,
                        (
                            max((x_lower - trajectory_speed, x_open), b_left),
                            min((x_upper + trajectory_speed, x_closed), b_right)
                        )
                    )][0]
                    cost_table[(time, x)] = [([], wait_cost + c)]
                    excluded += [x]
                    # print(str((x_lower, x_upper)) + ' & ' + str((i_lower, i_upper)) + ' -> ' + str(
                    #     cost_table[(time, x_lower, x_upper)]))
                    break

        # Group intervals by extrapolation
        l_answer_intervals = {}
        for x in reversed(sorted(
            Interval([boundaries]).range(),
            key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(x[1][1])
        )):
            if x not in excluded:
                answer_intervals = extrapolate(
                    answer_intervals=x,
                    excluded=excluded,
                    partitions=useless_partitions
                )
                l_answer_intervals[x] = answer_intervals
                excluded += answer_intervals

        # Group intervals by proximity
        d_answer_intervals = {}
        for x in l_answer_intervals:
            (x_left, x_right) = x
            lower_key = (x_left, False)
            if lower_key not in d_answer_intervals:
                d_answer_intervals[lower_key] = [x]
            else:
                d_answer_intervals[lower_key] += [x]

            upper_key = (x_right, True)
            if upper_key not in d_answer_intervals:
                d_answer_intervals[upper_key] = [x]
            else:
                d_answer_intervals[upper_key] += [x]
        k_answer_intervals = sorted(d_answer_intervals.values(), key=lambda x: len(x), reverse=True)

        # Remove repeated intervals
        excluded = []
        x_deleted = 0
        for x in range(len(k_answer_intervals)):
            x -= x_deleted
            x_answer_intervals = k_answer_intervals[x]
            y_deleted = 0
            for y in range(len(x_answer_intervals)):
                y -= y_deleted
                y_answer_intervals = x_answer_intervals[y]
                if y_answer_intervals in excluded:
                    del x_answer_intervals[y]
                    y_deleted += 1
                    if len(x_answer_intervals) is 0:
                        del k_answer_intervals[x]
                        x_deleted += 1
                else:
                    excluded += [y_answer_intervals]

        for x, _ in enumerate(k_answer_intervals):
            k_answer_intervals[x].sort(key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(x[1][1]))

        end = timer.time()
        print('Dynamic Performance: ' + str(end - start))


        with open('../share/' + name + '_bla' + str(time) + '.csv', 'w') as file:
            writer = csv.writer(
                file,
                escapechar='\\',
                lineterminator='\n',
                quoting=csv.QUOTE_NONE
            )
            for ((x_lower, x_open), (x_upper, x_closed)), x in sorted(l_answer_intervals.items(), key=lambda x: x[0]):
                a = (
                        ('{' + str(x_lower) + '}')
                        if not x_open and x_closed and x_lower == x_upper
                        else
                        ('(' if x_open else '[') +
                        str(float(x_lower)) + '..' + str(float(x_upper)) +
                        (']' if x_closed else ')')
                    )
                # print(a + ' -> ' + str(x))
                x = [
                    (
                        ('{' + str(x_lower) + '}')
                        if not x_open and x_closed and x_lower == x_upper
                        else
                        ('(' if x_open else '[') +
                        str(float(x_lower)) + '..' + str(float(x_upper)) +
                        (']' if x_closed else ')')
                    )
                    for ((x_lower, x_open), (x_upper, x_closed)) in x
                ]
                writer.writerow([a] + x)

        with open('../share/' + name + '_ble' + str(time) + '.csv', 'w') as file:
            writer = csv.writer(
                file,
                escapechar='\\',
                lineterminator='\n',
                quoting=csv.QUOTE_NONE
            )
            for x in k_answer_intervals:
                x = [
                    (
                        ('{' + str(x_lower) + '}')
                        if not x_open and x_closed and x_lower == x_upper
                        else
                        ('(' if x_open else '[') +
                        str(float(x_lower)) + '..' + str(float(x_upper)) +
                        (']' if x_closed else ')')
                    )
                    for ((x_lower, x_open), (x_upper, x_closed)) in x
                ]
                writer.writerow(x)

        start = timer.time()

        # context = partial(
        #     multi_search,
        #
        #     l_answer_intervals=l_answer_intervals,
        #
        #     time=time,
        #     cost_table=cost_table,
        #     max_size_of_population=max_size_of_population,
        #     elite_chromosomes=elite_chromosomes,
        #     selection_max_number_of_fit_chromosomes=selection_max_number_of_fit_chromosomes,
        #     boundaries=boundaries,
        #     alert_catalog=alert_catalog,
        #     trajectory_speed=trajectory_speed,
        #     stopping_condition=stopping_condition,
        #     m_flips=m_flips,
        #     generation_number_of_initial_probes=generation_number_of_initial_probes,
        #     sensor_catalog=sensor_catalog,
        #
        #     crossover_probability_of_crossover=crossover_probability_of_crossover,
        #     mutation_probability_of_mutation=mutation_probability_of_mutation,
        #
        #     sensor_success_rate_area=sensor_success_rate_area,
        #     byzantine_fault_tolerance=byzantine_fault_tolerance
        # )
        # with Pool(processes=cpu_count()) as pool:
        #     pool.map(context, k_answer_intervals)
        for x in k_answer_intervals:
            multi_search(
                k_answer_intervals=x,
                l_answer_intervals=l_answer_intervals,

                time=time,
                cost_table=cost_table,
                max_size_of_population=max_size_of_population,
                elite_chromosomes=elite_chromosomes,
                selection_max_number_of_fit_chromosomes=selection_max_number_of_fit_chromosomes,
                boundaries=boundaries,
                alert_catalog=alert_catalog,
                trajectory_speed=trajectory_speed,
                stopping_condition=stopping_condition,
                mutation_probability_of_flipping_bit=mutation_probability_of_flipping_bit,
                generation_number_of_initial_probes=generation_number_of_initial_probes,
                sensor_catalog=sensor_catalog,

                selection_base_logarithm=selection_base_logarithm,
                crossover_probability_of_crossover=crossover_probability_of_crossover,
                mutation_probability_of_mutation=mutation_probability_of_mutation,

                sensor_success_rate_area=sensor_success_rate_area,
                byzantine_fault_tolerance=byzantine_fault_tolerance
            )

        end = timer.time()
        print('Genetic Performance: ' + str(end - start))
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
            for x, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
                t, ((x_lower, x_open), (x_upper, x_closed)) = x
                i = (
                    ('{' + str(x_lower) + '}')
                    if not x_open and x_closed and x_lower == x_upper
                    else
                    (
                            ('(' if x_open else '[') +
                            str(float(x_lower)) + '..' + str(float(x_upper)) +
                            (']' if x_closed else ')')
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

        for x, _ in enumerate(useful_partitions):
            ((x_lower, x_open), (x_upper, x_closed)), x_cost = useful_partitions[x]
            x_range = (max((x_lower - trajectory_speed, x_open), b_left), min((x_upper + trajectory_speed, x_closed), b_right))
            useful_partitions[x] = (x_range, x_cost)

            (x_left, x_right) = x_range
            deleted = 0
            for y in range(len(useless_partitions)):
                y -= deleted
                y_range, y_cost = useless_partitions[y]
                if y_cost < x_cost:
                    (y_left, y_right) = y_range
                    if x_right <= y_right and intersects(x_range, y_range):
                        y_left = x_right
                        useless_partitions[y] = ((y_left, y_right), y_cost)
                    if y_left <= x_left and intersects(x_range, y_range):
                        y_right = x_left
                        useless_partitions[y] = ((y_left, y_right), y_cost)
                    if x_left <= y_left and y_right <= x_right:
                        del useless_partitions[y]
                        deleted += 1

    with open('../share/cost_table_' + name + '.csv', 'w') as file:
        writer = csv.writer(
            file,
            escapechar='\\',
            lineterminator='\n',
            delimiter=';',
            quoting=csv.QUOTE_NONE
        )
        for c, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
            writer.writerow([c, row_value])

    # time += cost_table_quality

    return cost_table
############################################################










############################################################
def test():
    import time as timer
    from submarine import Parameters

    time = 1
    answer_intervals = ((0, False), (53, False)) # [0..53)
    ((a_lower, a_open), (a_upper, a_closed)) = answer_intervals
    n_answer_intervals = a_upper - a_lower

    cost_table = {
        (0, x): [('', 0)]
        for x in Interval([Parameters.boundaries]).range()
    }
    nucleus = [
        (3, [False] * (Interval([Parameters.boundaries]).size() + 1)),
        (5, [False] * (Interval([Parameters.boundaries]).size() + 1))
    ]
    for pos in []:
        nucleus[0][1][pos] = True
    for pos in [40, 45]:
        nucleus[1][1][pos] = True

    n_genes = (Parameters.boundaries[1][0] - Parameters.boundaries[0][0]) + 1

    print('Initial settings: ' + Parameters.__repr__())
    print('answer_intervals: ' + str(answer_intervals))
    print('k time minus: ' + str(time))
    print('Set of probes: ' + ' , '.join([str(Interval([((x - 5 ,True), (x + 5,False))])) for x in [40, 45]]))

    n_boundaries = Parameters.boundaries[1][0] - Parameters.boundaries[0][0]
    boundaries_distributions = [[0] * n_boundaries]
    pb_dist = 1 / n_answer_intervals
    for x in range(a_lower, a_upper):
        boundaries_distributions[0][x] = pb_dist

    # start = timer.time()
    # print(evaluate(
    #     time=time,
    #     cost_table=cost_table,
    #     boundaries=Parameters.boundaries,
    #     alert_catalog=Parameters.alert_catalog,
    #     trajectory_speed=Parameters.trajectory_speed,
    #     nucleus=nucleus,
    #     sensor_catalog=Parameters.sensor_catalog,
    #
    #     sensor_success_rate_area = {},
    #     byzantine_fault_tolerance = 0,
    #
    #     boundaries_distributions=boundaries_distributions,
    #
    #     answer_intervals=[answer_intervals]
    # ))
    # end = timer.time()
    # print(end - start)

    start = timer.time()
    search(
        time=time,
        t_answer_intervals=(answer_intervals, [answer_intervals]),
        cost_table=cost_table,
        max_size_of_population=Parameters.max_size_of_population,
        elite_chromosomes=Parameters.elite_chromosomes,
        selection_max_number_of_fit_chromosomes=Parameters.selection_max_number_of_fit_chromosomes,
        boundaries=Parameters.boundaries,
        alert_catalog=Parameters.alert_catalog,
        trajectory_speed=Parameters.trajectory_speed,
        stopping_condition=Parameters.stopping_condition,
        mutation_probability_of_flipping_bit=Parameters.mutation_probability_of_flipping_bit,
        generation_number_of_initial_probes=Parameters.generation_number_of_initial_probes,
        sensor_catalog=Parameters.sensor_catalog,
        selection_base_logarithm=Parameters.selection_base_logarithm,
        crossover_probability_of_crossover=Parameters.crossover_probability_of_crossover,
        mutation_probability_of_mutation=Parameters.mutation_probability_of_mutation,
        elite=[],

        sensor_success_rate_area={},
        byzantine_fault_tolerance=0
    )
    print(cost_table[(time, answer_intervals)])
    end = timer.time()
    print(end - start)

    quit(0)