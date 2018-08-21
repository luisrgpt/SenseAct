# coding=utf-8

from graphs import Graph, Node, Hyperedge
from intervals import Interval
import genetic

from time import strftime
from ast import literal_eval
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
        snapshot = Interval(solution.appr[:])
        solution.appr += self.decay_unit
        solution.appr &= Interval([solution.bounds])
        solution.graph += [
            Hyperedge(
                sources=[x for x in snapshot if x in interval],
                targets=[interval],
                weight=0,
                label='Wait'
            ) for interval in solution.appr
        ]
        # Useless batches (after too much decay)
        for timestamp, batch in enumerate(solution.batches):
            if not batch:
                continue

            decay = (solution.timestamp - timestamp) * self.decay_unit
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
        for y in solution.appr:
            x.intervals = [y]
            for alert_interval, cost in self.alert_costs:
                lower = (x[0] if Interval([alert_interval])[0][1] <= x[0][1] else alert_interval[0])[0]
                upper = (x[0] if x[0][0] <= Interval([alert_interval])[0][0] else alert_interval[0])[1]

                if alert_cost < cost and (
                    lower[0] < upper[0] or (lower[0] == upper[0] and lower[1] < upper[1])
                ):
                    alert_cost = cost

        solution.cost += alert_cost

        return self
class DynamicGeneticFormula:
    def __init__(
            self,
            appr: Interval,
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
        self.appr: Interval = appr
        self.bounds: tuple = bounds

        self.alert_costs: list = alert_costs
        self.decay_unit: tuple = decay_unit

        self.computation_rate: int = computation_rate
        self.m_stagnation: float = m_stagnation
        self.m_flips: int = m_flips
        self.n_pool: int = n_pool
        self.m_tops: int  = m_tops
        self.n_sel: int = n_sel
        self.n_precisions = n_precisions
        self.n_costs = n_costs

        self.k_mat: float = k_mat
        self.k_mut: float = k_mut

        self.cost_table: dict = {
            (0, x): [('', 0)]
            for x in Interval([bounds]).range()
        }
        self.time: int = 1
        self.elite = []
        self.result = None

        self.probability_distributions: dict = probability_distributions
        self.byzantine_fault_tolerance: int = byzantine_fault_tolerance
    def __iadd__(self, problem: UncertainByzantineProblem):
        import time as timer
        start = None
        partitions = [(Interval([x]), c) for x, c in self.alert_costs]
        partitions += [(~Interval([x for x, _ in self.alert_costs]), 0)]
        i_bounds = Interval([self.bounds])
        for time in range(self.time, self.time + self.computation_rate):
            cnt = 0
            lmt = 1 + (self.bounds[1][0] - self.bounds[0][0]) * 4 + 4
            time_minus_1 = time - 1

            for x in i_bounds.range():
                for i, c in partitions:
                    xi = Interval([x])
                    if xi in i:
                        x_minus_1 = ((xi + self.decay_unit) & i_bounds)[0]
                        self.cost_table[(time, x)] = [([], self.cost_table[(time_minus_1, x_minus_1)][0][1] + c)]

            #d_lower = self.decay_unit[0][0] * time_minus_1
            #d_open = self.decay_unit[0][1] | time_minus_1 is 0
            #d_upper = self.decay_unit[1][0] * time_minus_1
            #d_closed = self.decay_unit[1][1] & time_minus_1 is not 0
            #decay = ((d_lower, d_open), (d_upper, d_closed))
            #decay_alert_costs = [((Interval([i]) + decay)[0], c) for i, c in self.alert_costs]

            if (time, self.bounds) not in self.cost_table:
                genetic.search(
                    time=time,
                    appr=self.bounds,
                    cost_table=self.cost_table,
                    n_pool=self.n_pool,
                    m_tops=self.m_tops,
                    n_sel=self.n_sel,
                    bounds=self.bounds,
                    alert_costs=self.alert_costs,
                    decay_unit=self.decay_unit,
                    m_stagnation=self.m_stagnation,
                    m_flips=self.m_flips,
                    n_precisions=self.n_precisions,
                    n_costs=self.n_costs,

                    k_mat=self.k_mat,
                    k_mut=self.k_mut,
                    elite=self.elite,

                    probability_distributions=self.probability_distributions,
                    byzantine_fault_tolerance=self.byzantine_fault_tolerance
                )

            for interval in Interval([self.bounds]).range():
                #(x for and_interval in problem.or_interval for x in and_interval):
                if (time, interval) not in self.cost_table:
                    genetic.search(
                        time=time,
                        appr=interval,
                        cost_table=self.cost_table,
                        n_pool=self.n_pool,
                        m_tops=self.m_tops,
                        n_sel=self.n_sel,
                        bounds=self.bounds,
                        alert_costs=self.alert_costs,
                        decay_unit=self.decay_unit,
                        m_stagnation=self.m_stagnation,
                        m_flips=self.m_flips,
                        n_precisions=self.n_precisions,
                        n_costs=self.n_costs,

                        k_mat=self.k_mat,
                        k_mut=self.k_mut,
                        elite=self.elite,

                        probability_distributions=self.probability_distributions,
                        byzantine_fault_tolerance=self.byzantine_fault_tolerance
                    )
                #print(str((time, interval)) + ' : ' + str(self.cost_table[(time, interval)]))
                if cnt is 0:
                    end = timer.time()
                    if start is not None: print(end - start)
                    print(str(time) + ': ' + str(interval))
                    lmt -= 4
                    start = timer.time()
                cnt += 1
                cnt %= lmt

            with open('log/cost_table_t_minus_' + str(time) + '_minutes.csv', 'w') as file:
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
                for c, row_value in sorted(self.cost_table.items(), key=lambda x: x[0]):
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

        self.time += self.computation_rate

        # Predict best probe combination
        self.result = [
            (self.n_costs[u], u, pos)
            for x in self.appr
            for u, comb in self.cost_table[(self.time - 1, x)][0][0]
            for pos in comb
        ]
        return self
class BatchSolution:
    def __init__(
            self,
            appr: Interval,
            bounds: tuple,

            input_source,

            location: int
    ):
        self.appr: Interval = appr
        self.bounds: tuple = bounds

        self.input_source = input_source

        self.location: int = location

        self.graph: Graph = Graph(
                node=Node(
                    label=str(appr)
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
        csv_content += [self.appr]

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
            snapshot = Interval(self.appr[:])

            self.cost = sum(x for x, _, _ in formula.result)
            interval = Interval([])
            lower_bounds, upper_bounds = self.bounds
            for location, imprecision, _, does_detect, _ in batch:
                if does_detect:
                    interval.intervals = [
                        ((location - imprecision, True), (location + imprecision, False))
                    ]
                else:
                    interval.intervals = [
                        (lower_bounds, (location - imprecision, True)),
                        ((location + imprecision, False), upper_bounds)
                    ]
                self.appr &= interval

            # Update state
            self.graph += [
                Hyperedge(
                    sources=[interval],
                    targets=[x for x in self.appr if x in interval],
                    weight=self.cost,
                    label=str(batch)
                ) for interval in snapshot
            ]
            self.batches += [batch]
        else:
            self.batches += [None]

        return self

def search(use_case):
    solution = BatchSolution(
        appr=use_case.appr,
        bounds=use_case.bounds,

        input_source=use_case.method(use_case.argument),

        location=use_case.backend_location
    )
    problem = UncertainByzantineProblem(
        alert_costs=use_case.alert_costs,
        decay_unit=use_case.decay_unit
    )
    formula = DynamicGeneticFormula(
        appr=use_case.appr,
        bounds=use_case.bounds,

        alert_costs=use_case.alert_costs,
        decay_unit=use_case.decay_unit,

        computation_rate=use_case.computation_rate,
        m_stagnation=use_case.m_stagnation,
        m_flips=use_case.m_flips,

        n_pool=use_case.n_pool,
        m_tops=use_case.m_tops,
        n_sel=use_case.n_sel,
        n_precisions=use_case.n_precisions,
        n_costs=use_case.n_costs,

        k_mat=use_case.k_mat,
        k_mut=use_case.k_mut,

        probability_distributions=use_case.probability_distributions,
        byzantine_fault_tolerance=use_case.byzantine_fault_tolerance
    )

    while True:
        #yield str(solution)

        problem += solution
        formula += problem
        solution += formula
