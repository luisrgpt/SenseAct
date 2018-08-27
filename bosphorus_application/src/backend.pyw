# coding=utf-8

from graphs import Graph, Node, Hyperedge
from intervals import Interval
import algorithm

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

            decay = (solution.timestamp - timestamp) * self.decay_unit[1][0]
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
        for appr_yes in solution.appr:
            for x, cost in self.alert_costs:
                if alert_cost < cost and (appr_yes if x[1] <= appr_yes[1] else x)[0] < (appr_yes if appr_yes[0] <= x[0] else x)[1]:
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
        self.cost_table: dict = algorithm.build(
            bounds=bounds,
    
            alert_costs=alert_costs,
            decay_unit=decay_unit,
    
            computation_rate=computation_rate,
            m_stagnation=m_stagnation,
            m_flips=m_flips,
    
            n_pool=n_pool,
            m_tops=m_tops,
            n_sel=n_sel,
            n_precisions=n_precisions,
            n_costs=n_costs,
    
            k_mat=k_mat,
            k_mut=k_mut,
    
            probability_distributions=probability_distributions,
            byzantine_fault_tolerance=byzantine_fault_tolerance
        )
        self.n_costs: dict = n_costs
        self.appr = appr
        self.time = computation_rate
        self.result = None
    def __iadd__(self, problem: UncertainByzantineProblem):
        # Predict best probe combination
        self.result = [
            (self.n_costs[u], u, pos)
            for x in self.appr
            for u, comb in self.cost_table[(self.time, x)][0][0]
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
