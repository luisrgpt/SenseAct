# coding=utf-8

from graphs import Graph, Node, Hyperedge
from intervals import Interval
import genetic

from time import strftime
import csv

class UncertainByzantineProblem:
    def __init__(
        self,

        alert_costs: list,
        decay_unit: tuple
    ):
        self.alert_costs: list = alert_costs
        self.decay_unit: tuple = decay_unit
    def __iadd__(self, solution):
        # Decaying probes
        snapshot = Interval(solution.state[:])
        solution.state += solution.decay_unit
        solution.state &= solution.bounds
        solution.graph += [
            Hyperedge(
                sources=[x for x in snapshot if x in interval],
                targets=[interval],
                weight=0,
                label='Wait'
            ) for interval in solution.state
        ]
        # Useless batches (after too much decay)
        for timestamp, batch in enumerate(solution.batches):
            if not batch:
                continue

            decay = solution.timestamp - timestamp
            for index, probe in enumerate(batch):
                if not probe:
                    continue
                location, imprecision, _, does_detect, _ = probe
                upper_margin = solution.bounds[1][0] - imprecision - decay
                lower_margin = solution.bounds[0][0] + imprecision + decay
                useless_yes = does_detect and upper_margin < location < lower_margin
                useless_no = not does_detect and decay >= imprecision
                if useless_yes or useless_no:
                    batch[index] = None
                    continue
        solution.timestamp += 1
        # Incremented cost after decay
        alert_cost = 0
        x = Interval([])
        for y in solution.state:
            x.intervals = [y]
            for alert_interval, cost in solution.alert_costs:
                lower = (x[0] if alert_interval[0][1] <= x[0][1] else alert_interval[0])[0]
                upper = (x[0] if x[0][0] <= alert_interval[0][0] else alert_interval[0])[1]

                if alert_cost < cost and (
                        lower[0] < upper[0] or (lower[0] == upper[0] and lower[1] < upper[1])
                ):
                    alert_cost = cost

        solution.cost += alert_cost

        return self
class DynamicGeneticFormula:
    def __init__(
            self,
            approximation: Interval,
            bounds: tuple,

            alert_costs: list,
            decay_unit: tuple,

            computation_rate: int,
            pb_neg: float,
            m_flips: int,
            m_tops: int,
    ):
        self.approximation: Interval = approximation
        self.bounds: tuple = bounds

        self.alert_costs: list = alert_costs
        self.decay_unit: tuple = decay_unit

        self.computation_rate: int = computation_rate
        self.pb_neg: float = pb_neg
        self.m_flips: int = m_flips
        self.m_tops: int  = m_tops

        self.cost_table: dict = {
            str((0, x)): {'': 0}
            for x in Interval([bounds]).range()
        }
        self.time: int = 1
        self.result = None
    def __iadd__(self, problem: UncertainByzantineProblem):
        cnt = 0
        for time in range(self.time, self.time + self.computation_rate):
            lmt = 1 + (self.bounds[1][0] - self.bounds[0][0]) * 4 + 4
            for interval in Interval([self.bounds]).range():
                #(x for and_interval in problem.or_interval for x in and_interval):
                top5 = genetic.search(
                    time=time,
                    approximation=interval,
                    cost_table=self.cost_table,
                    m_tops=self.m_tops,
                    bounds=self.bounds,
                    alert_costs=self.alert_costs,
                    decay_unit=self.decay_unit,
                    pb_neg=self.pb_neg,
                    m_flips=self.m_flips
                )
                self.cost_table[str((time, interval))] = {
                    str(' '.join([str(index) for index, y in enumerate(x) if y])):
                        genetic.evaluate(
                            time=time,
                            approximation=interval,
                            cost_table=self.cost_table,
                            m_tops=self.m_tops,
                            bounds=self.bounds,
                            alert_costs=self.alert_costs,
                            decay_unit=self.decay_unit,
                            pb_neg=self.pb_neg,
                            m_flips=self.m_flips,
                            comb=x
                        )
                    for x in top5
                }
                #print(str((time, interval)) + " : " + str(self.cost_table[str((time, interval))]))
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

        self.time += self.computation_rate

        # Predict best probe combination
        comb = genetic.search(
            time=self.time,
            approximation=self.approximation,
            cost_table=self.cost_table,
            m_tops=self.m_tops,
            bounds=self.bounds,
            alert_costs=self.alert_costs,
            decay_unit=self.decay_unit,
            pb_neg=self.pb_neg,
            m_flips=self.m_flips
        )[0]
        self.result = [(10, 3, index) for index, x in enumerate(comb) if x]
        return self
class BatchSolution:
    def __init__(
            self,
            approximation: Interval,
            bounds: tuple,

            input_source,

            location: int
    ):
        self.approximation: Interval = approximation
        self.bounds: tuple = bounds

        self.input_source = input_source

        self.location: int = location

        self.graph: Graph = Graph(
                node=Node(
                    label=str(approximation)
                )
            )
        self.batches: list = []
        self.true_value: int = next(self.input_source)
        self.timestamp: int = 0
        self.cost: int = 0
    def __repr__(self):
        # Create log
        # Computer
        csv_content = [strftime('%Y_%m_%d_%H_%M_%S')]
        csv_content += [self.location]
        csv_content += [self.timestamp]
        csv_content += [self.cost]
        csv_content += [self.approximation]

        # Environment
        csv_content += [self.true_value]
        csv_content += [self.timestamp]

        # Graph
        csv_content += [self.graph.save_into_disk_and_get_file_name(
            '../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX'
        )]

        # Decisions
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
                    Interval([
                        ((location - imprecision - decay, False), (location + imprecision + decay, True))
                    ])
                    if does_detect
                    else
                    Interval([
                        (self.bounds[0], (location - imprecision + decay, True)),
                        ((location + imprecision - decay, False), self.bounds[1])
                    ])
                ]

        csv_content = [str(x) for x in csv_content]

        stream = csv.StringIO()
        writer = csv.writer(stream)
        writer.writerow(csv_content)
        return stream.getvalue()
    def __iadd__(self, formula: DynamicGeneticFormula):
        # Get measurements
        self.true_value = next(self.input_source)
        batch = [
            (float(location), float(imprecision), cost, abs(location - self.true_value) <= imprecision, False)
            for cost, imprecision, location in formula.result
        ]
        # Generate result if batch is not empty
        if len(batch) > 0:
            snapshot = Interval(self.approximation[:])

            self.cost = sum(x for x, _, _ in formula.result)
            interval = Interval([])
            lower_bounds, upper_bounds = self.bounds[0]
            for location, imprecision, _, does_detect, _ in batch:
                if does_detect:
                    interval.intervals = [
                        ((location - imprecision, False), (location + imprecision, True))
                    ]
                else:
                    interval.intervals = [
                        (lower_bounds, (location - imprecision, False)),
                        ((location + imprecision, True), upper_bounds)
                    ]
                self.approximation &= interval

            # Update state
            self.graph += [
                Hyperedge(
                    sources=[interval],
                    targets=[x for x in self.approximation if x in interval],
                    weight=self.cost,
                    label=str(batch)
                ) for interval in snapshot
            ]
            self.batches += [batch]
        else:
            self.batches += [None]

        return self

def search(
        approximation: Interval,
        bounds: tuple,

        alert_costs: list,
        decay_unit: tuple,
        input_source,

        computation_rate: int,
        pb_neg: float,
        m_flips: int,
        m_tops: int,

        location: int
):
    solution = BatchSolution(
        approximation=approximation,
        bounds=bounds,

        input_source=input_source,

        location=location
    )
    problem = UncertainByzantineProblem(
        alert_costs=alert_costs,
        decay_unit=decay_unit
    )
    formula = DynamicGeneticFormula(
        approximation=approximation,
        bounds=bounds,

        alert_costs=alert_costs,
        decay_unit=decay_unit,

        computation_rate=computation_rate,
        pb_neg=pb_neg,
        m_flips=m_flips,
        m_tops=m_tops
    )

    while True:
        yield str(solution)

        problem += solution
        formula += problem
        solution += formula
