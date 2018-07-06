# coding=utf-8
import csv
from graphs import Graph, Node, Hyperedge
from intervals import AbsoluteUncertainty, Interval, IntervalExpression, LeftEndpoint, RightEndpoint
from random import randint, choice
from time import strftime
import genetic

decay_unit = AbsoluteUncertainty(0, 1)
def generate_submarine(location):
    while True:
        yield location
        if location is 0 or location is 100:
            raise StopIteration()

        velocity = choice([-location, location])
        norm = abs(velocity)

        normalized_vector = velocity / norm

        location = location + normalized_vector

class ByzantineProblem:
    def __init__(self, location, or_interval, limit: Interval, get_alarm_cost, computation_rate):
        self.location = location
        self.timestamp = 0
        self.total_cost = 0
        self.graph = Graph(
                node=Node(
                    label=str(or_interval)
                )
            )
        self.batches: list = []
        self.or_interval: IntervalExpression = or_interval
        self.limit: Interval = limit
        self.get_alarm_cost = get_alarm_cost
        self.submarine = generate_submarine(randint(0, 100))
        self.computation_rate = computation_rate
        self.submarine_location = None
    def __repr__(self):
        # Create log
        # Ship
        csv_content = [strftime('%Y_%m_%d_%H_%M_%S')]
        csv_content += [self.location]
        csv_content += [self.timestamp]
        csv_content += [self.total_cost]
        csv_content += [self.or_interval]

        # Submarine
        csv_content += [self.submarine_location]
        csv_content += [self.timestamp]

        # Graph
        csv_content += [self.graph.save_into_disk_and_get_file_name(
            '../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX'
        )]

        # Probes
        counter = 0
        for timestamp, batch in enumerate(self.batches, start=1):
            decay = self.timestamp - timestamp
            if not batch:
                continue
            counter += 1
            for label, probe in enumerate(batch):
                if not probe:
                    continue
                location, imprecision, cost, does_detect, does_lie = probe
                csv_content += [counter]
                csv_content += [label]
                csv_content += [timestamp]
                csv_content += [location]
                csv_content += [imprecision]
                csv_content += [decay]
                csv_content += [cost]
                csv_content += [does_detect]
                csv_content += [
                    Interval(
                        left=LeftEndpoint(location - imprecision - decay, False, True),
                        right=RightEndpoint(location + imprecision + decay, False, True)
                    )
                    if does_detect
                    else
                    IntervalExpression(
                        intervals=[
                            Interval(
                                left=self.limit.left,
                                right=RightEndpoint(location - imprecision + decay, True, False)
                            ),
                            Interval(
                                left=LeftEndpoint(location + imprecision - decay, True, False),
                                right=self.limit.right
                            )
                        ]
                    )
                ]

        csv_content = [str(x) for x in csv_content]

        stream = csv.StringIO()
        writer = csv.writer(stream)
        writer.writerow(csv_content)
        return stream.getvalue()

    def __iadd__(self, solution):
        global decay_unit

        # Wait
        snapshot = IntervalExpression(
            intervals=[
                Interval(
                    left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                    right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                ) for x in self.or_interval
            ]
        )
        self.or_interval += decay_unit
        self.or_interval[0] &= self.limit
        self.or_interval[-1] &= self.limit
        # Update state
        self.graph += [
            Hyperedge(
                sources=[x for x in snapshot if x in interval],
                targets=[interval],
                weight=0,
                label='Wait'
            ) for interval in self.or_interval
        ]
        # Eliminate useless batches
        for timestamp, batch in enumerate(self.batches):
            if not batch:
                continue

            decay = self.timestamp - timestamp
            for index, probe in enumerate(batch):
                if not probe:
                    continue
                location, imprecision, _, does_detect, _ = probe
                margin = imprecision + decay
                useless_yes = does_detect and self.limit.right.value - margin < location < self.limit.left.value + margin
                useless_no = decay >= imprecision
                if useless_yes or useless_no:
                    batch[index] = None
                    continue
        self.timestamp += 1

        # Get measurements
        self.submarine_location = next(self.submarine)
        batch = [
            (float(location), float(imprecision), cost, abs(location - self.submarine_location) <= imprecision, False)
            for cost, imprecision, location in solution.batch
        ]
        # Generate result if batch is not empty
        if len(batch) > 0:
            snapshot = IntervalExpression(
                intervals=[
                    Interval(
                        left=LeftEndpoint(x.left.value, x.left.is_open, x.left.is_closed),
                        right=RightEndpoint(x.right.value, x.right.is_open, x.right.is_closed)
                    ) for x in self.or_interval
                ]
            )

            batch_cost = sum(x for x, _, _ in solution.batch)
            interval = Interval(
                left=LeftEndpoint(0, False, True),
                right=RightEndpoint(0, False, True)
            )
            expression = IntervalExpression(
                intervals=[
                    Interval(
                        left=self.limit.left,
                        right=RightEndpoint(0, False, True)
                    ),
                    Interval(
                        left=LeftEndpoint(0, False, True),
                        right=self.limit.right
                    )
                ]
            )
            interval_left = interval.left
            interval_right = interval.right
            not_lower_right = expression[0].right
            not_upper_left = expression[1].left
            for location, imprecision, _, does_detect, _ in batch:
                if does_detect:
                    interval_left.value = location - imprecision
                    interval_left.is_open = False
                    interval_left.is_closed = True
                    interval_right.value = location + imprecision
                    interval_right.is_open = False
                    interval_right.is_closed = True
                    for index in range(len(self.or_interval)):
                        self.or_interval[index] &= interval
                else:
                    not_lower_right.value = location - imprecision
                    not_lower_right.is_open = True
                    not_lower_right.is_closed = False
                    not_upper_left.value = location + imprecision
                    not_upper_left.is_open = True
                    not_upper_left.is_closed = False
                    self.or_interval &= expression

            # Update state
            self.graph += [
                Hyperedge(
                    sources=[interval],
                    targets=[x for x in self.or_interval if x in interval],
                    weight=batch_cost,
                    label=str(batch)
                ) for interval in snapshot
            ]
            self.total_cost += batch_cost
            self.batches += [batch]
        else:
            self.batches += [None]

        self.total_cost += self.get_alarm_cost(self.or_interval)

        return self
class DynamicFormula:
    def __init__(self, limit: Interval, get_alarm_cost):
        self.or_interval = None
        self.cost_table = {
            str((0, x)): {'': 0}
            for x in Interval(
                left=LeftEndpoint(0, False, True),
                right=RightEndpoint(100, False, True)
            )
        }
        self.time = 1
        self.limit: Interval = limit
        self.get_alarm_cost = get_alarm_cost
        cnt = 0
        lmt = 1 + len(self.limit) * 4 + 4
        for interval in self.limit:
            genetic.search(self.time, interval, self.cost_table, 0, self.limit, get_alarm_cost)
            if cnt is 0:
                print(str(self.time) + ": " + str(interval))
                lmt -= 4
            cnt += 1
            cnt %= lmt
    def __iadd__(self, problem: ByzantineProblem):
        cnt = 0
        for time in range(self.time, self.time + problem.computation_rate):
            lmt = 1 + len(self.limit) * 4 + 4
            for interval in self.limit:#(x for and_interval in problem.or_interval for x in and_interval):
                top5 = genetic.search(time, interval, self.cost_table, 5, self.limit, self.get_alarm_cost)
                self.cost_table[str((time, interval))] = {
                    str(' '.join([str(index) for index, y in enumerate(comb) if y])):
                        genetic.evaluate(time, interval, comb, self.cost_table, self.limit, self.get_alarm_cost)
                    for comb in top5
                }
                if cnt is 0:
                    print(str(time) + ": " + str(interval))
                    lmt -= 4
                cnt += 1
                cnt %= lmt

        with open('log/test.csv', 'w') as file:
            writer = csv.writer(
                file,
                escapechar='\\',
                lineterminator='\n',
                quoting=csv.QUOTE_NONE
            )
            writer.writerow(
                ['time till done', 'interval', 'probes', 'cost', 'probes', 'cost', 'probes', 'cost', 'probes',
                 'cost', 'probes', 'cost'])
            for row_key, row_value in self.cost_table.items():
                writer.writerow(row_key[1:-1].split(', ') + [x for cell in row_value.items() for x in cell])

        self.time += problem.computation_rate
        self.or_interval = problem.or_interval
        return self
class NoFormula:
    def __iadd__(self, problem):
        return self
class GeneticSolution:
    def __init__(self, limit, get_alarm_cost):
        self.batch: list = []
        self.limit: Interval = limit
        self.get_alarm_cost = get_alarm_cost
    def __iadd__(self, formula: DynamicFormula):
        comb = genetic.search(
            time=formula.time,
            expression=formula.or_interval,
            cost_table=formula.cost_table,
            m_tops=1,
            limit=self.limit,
            get_alarm_cost=self.get_alarm_cost
        )[0]
        self.batch = [(10, 3, index) for index, x in enumerate(comb) if x]

        return self
class RandomSolution:
    def __init__(self):
        self.batch: list = []

    def __iadd__(self, formula):
        self.batch = [(10, 3, randint(10, 90)) for _ in range(randint(2, 2))]

        return self

def ship(ship_location, submarine_location, limit, get_alarm_cost, computation_rate):
    problem = ByzantineProblem(
        location=ship_location,
        or_interval=submarine_location,
        limit=limit,
        get_alarm_cost=get_alarm_cost,
        computation_rate=computation_rate
    )
    formula = DynamicFormula(
        limit=limit,
        get_alarm_cost=get_alarm_cost
    )
    solution = GeneticSolution(
        limit,
        get_alarm_cost=get_alarm_cost
    )
    #formula = NoFormula()
    #solution = RandomSolution()

    while True:
        yield str(problem)

        formula += problem
        solution += formula
        problem += solution
