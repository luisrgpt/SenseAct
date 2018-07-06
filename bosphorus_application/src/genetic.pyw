# coding=utf-8
from intervals import AbsoluteUncertainty, Interval, IntervalExpression, LeftEndpoint, RightEndpoint
from random import random, randint, randrange

n_genes = 101
m_pool = 50
m_elite = 5
n_gen = 10
m_flips = 1
pb_gen = 0.01
pb_mate = 1
not_pb_mutate = 1

elites = {}

def generate(expression):
    return [
        index in expression and random() < pb_gen
        for index ,_ in enumerate(range(n_genes))
    ]

def evaluate(time, expression, comb, cost_table, limit: Interval, get_alarm_cost):
    or_interval = IntervalExpression(
        intervals=[
            Interval(
                left=LeftEndpoint(
                    value=expression.left.value,
                    is_open=expression.left.is_open,
                    is_closed=expression.left.is_closed
                ),
                right=RightEndpoint(
                    value=expression.right.value,
                    is_open=expression.right.is_open,
                    is_closed=expression.right.is_closed
                )
            )
        ]
        if isinstance(expression, Interval)
        else
        [
            Interval(
                left=LeftEndpoint(
                    value=x.left.value,
                    is_open=x.left.is_open,
                    is_closed=x.left.is_closed
                ),
                right=RightEndpoint(
                    value=x.right.value,
                    is_open=x.right.is_open,
                    is_closed=x.right.is_closed
                )
            )
            for x in expression
        ]
    )
    minus_1 = time - 1
    decay_unit = AbsoluteUncertainty(0, 1)
    n_interval = sum(len(x) for x in or_interval)

    no = IntervalExpression(
        intervals=[
            Interval(
                left=LeftEndpoint(
                    value=x.left.value,
                    is_open=x.left.is_open,
                    is_closed=x.left.is_closed
                ),
                right=RightEndpoint(
                    value=x.right.value,
                    is_open=x.right.is_open,
                    is_closed=x.right.is_closed
                )
            )
            for x in or_interval
        ]
    )
    no_prob = 1

    yes = IntervalExpression(
        intervals = [
            Interval(
                left=LeftEndpoint(
                    value=0,
                    is_open=False,
                    is_closed=True
                ),
                right=RightEndpoint(
                    value=0,
                    is_open=False,
                    is_closed=True
                )
            )
        ]
    )

    cost = sum(10 for x in comb if x)
    if n_interval is not 0:
        for i, positive in enumerate(comb):
            if not positive:
                continue
            left_value = max(
                [i - 3] +
                [max(0, i - 6) + j + 3 for j, x in enumerate(comb[max(0, i - 6):i]) if x]
            )
            right_values = (
                [min(i + 1, len(comb)) + j - 3 for j, x in enumerate(comb[min(i + 1, len(comb)):min(i + 6, len(comb))]) if x] +
                [i + 3]
            )
            if left_value != i - 3:
                yes[0].left.is_open = True
                yes[0].left.is_closed = False
            for right_value in right_values:
                yes[0].left.value = left_value
                yes[0].right.value = right_value
                if right_value == i + 3:
                    yes[0].right.is_open = False
                    yes[0].right.is_closed = True
                else:
                    yes[0].right.is_open = True
                    yes[0].right.is_closed = False
                yes &= or_interval
                for x in yes:
                    #print(x)
                    yes_prob = len(x) / n_interval
                    alarm_cost = get_alarm_cost(x)
                    wait_cost = min(cost_table[str((minus_1, (x + decay_unit) & limit))].values())
                    cost += yes_prob * (alarm_cost + wait_cost)
                    no_prob -= yes_prob
                no &= ~yes
                left_value = right_value
                yes[0].left.is_open = False
                yes[0].left.is_closed = True
    print(no)
    alarm_cost = max(get_alarm_cost(x) for x in no)
    wait_cost = sum(min(cost_table[str((minus_1, (x + decay_unit) & limit))].values()) for x in no)
    cost += no_prob * (alarm_cost + wait_cost)

    return cost
def mate(chromosome_1: list, chromosome_2: list):
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
def mutate(chromosome: list, m_flips: int):
    chromosome = [x for x in chromosome]

    n_flips = randint(-m_flips, m_flips)

    flip_signal = n_flips > 0

    # for each number of flips
    for x in range(abs(n_flips)):
        # break loop if all genes are flipped
        if all(y == flip_signal for y in chromosome):
            break

        # repeat until gene is the opposite of its flip
        y = randrange(len(chromosome))
        while chromosome[y] == flip_signal:
            y = randrange(len(chromosome))
        # flip value
        chromosome[y] = type(chromosome[y])(not chromosome[y])

    return chromosome
def search(time, expression, cost_table, m_tops, limit: Interval, get_alarm_cost):
    global elites

    key = str(expression)
    elite = elites[key] if key in elites else []
    n_pool = min(m_pool, len(expression))
    n_tops = min(m_tops, n_pool)
    n_elite = min(m_elite, n_pool)

    # Generate and evaluate
    pool = [generate(expression) for _ in range(n_pool - len(elite))] + elite
    fitness = [evaluate(time, expression, comb, cost_table, limit, get_alarm_cost) for comb in pool]
    for _ in range(n_gen):
        # Mate, mutate and evaluate
        prob = [random() for _ in pool]
        pool += [x for even, odd, pb in zip(pool[::2], pool[1::2], prob) if pb < pb_mate for x in mate(even, odd)]
        pool += [mutate(x, m_flips) for x, pb in zip(pool, prob) if not_pb_mutate <= pb]
        fitness += [evaluate(time, expression, comb, cost_table, limit, get_alarm_cost) for comb in pool[n_pool:]]
        # Select
        pool = [x for _, x in sorted(zip(fitness, pool))][:n_pool]
        fitness = [x for x in sorted(fitness)][:n_pool]
    # Return top N
    elites[key] = pool[:n_elite]
    return pool[:n_tops]

def test():
    red_alert_interval = Interval(
        left=LeftEndpoint(40, False, True),
        right=RightEndpoint(45, False, True)
    )
    yellow_alert_interval = Interval(
        left=LeftEndpoint(45, True, False),
        right=RightEndpoint(70, False, True)
    )
    red_alert_cost = 1000
    yellow_alert_cost = 50
    def get_alarm_cost(location):
        return (
            red_alert_cost
            if location & red_alert_interval in red_alert_interval
            else
            yellow_alert_cost
            if location & yellow_alert_interval in yellow_alert_interval
            else
            0
        )
    limit = Interval(
        left=LeftEndpoint(0, False, True),
        right=RightEndpoint(100, False, True)
    )
    cost_table = {
        str((0, x)): {"": 0}
        for x in limit
    }
    expression = Interval(
        left=LeftEndpoint(0, False, True),
        right=RightEndpoint(100, False, True)
    )


    comb = [False] * 32 + [True] + [False] + [True] + [False] * 66

    print(evaluate(
        time=1,
        expression=expression,
        comb=comb,
        cost_table=cost_table,
        limit=limit,
        get_alarm_cost=get_alarm_cost
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
