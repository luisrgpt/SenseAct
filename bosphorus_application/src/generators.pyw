# coding=utf-8
import csv
from graphs import Graph, Node, Hyperedge
from intervals import AbsoluteUncertainty, Uncertainty, Interval, IntervalExpression, LeftEndpoint, RightEndpoint
import math
import random
from time import strftime
from itertools import chain
import genetic

domain = IntervalExpression([Interval(
    left=LeftEndpoint(0, False, True),
    right=RightEndpoint(100, False, True)
)])
red_alert_interval = IntervalExpression([Interval(
    left=LeftEndpoint(40, False, True),
    right=RightEndpoint(45, False, True)
)])
yellow_alert_interval = IntervalExpression([Interval(
    left=LeftEndpoint(45, True, False),
    right=RightEndpoint(70, False, True)
)])
red_alert_cost = 1000
yellow_alert_cost = 50
def get_alarm_cost(location):
    return (
        red_alert_cost
        if len(location & red_alert_interval) > 0
        else
        yellow_alert_cost
        if len(location & yellow_alert_interval) > 0
        else
        0
    )
def generate_submarine(location):
    timestamp = 0
    while True:
        yield location, timestamp

        velocity = [-x for x in location]
        norm = math.sqrt(sum(x**2 for x in velocity))
        if norm == 0:
            raise StopIteration()

        normalized_vector = [x / norm for x in velocity]

        location = [x[0] + x[1] for x in zip(location, normalized_vector)]
        timestamp += 1

class Probe:
    submarine_location = None

    def __init__(self, cost: int, precision: int, location: list):
        self.cost: int = cost
        self.precision: int = precision
        self.location = location
        self.interval = IntervalExpression([Interval(
            left=LeftEndpoint(location[0] - precision, False, True),
            right=RightEndpoint(location[0] + precision, False, True)
        )])

    def synchronous_read(self):
        # Calculate measurements
        values = zip(self.location, Probe.submarine_location)
        distance = sum((x[0] - x[1]) ** 2 for x in values) ** 0.5
        reply = str(distance <= self.precision)

        return reply
class Measurement:
    def __init__(self, label, location, precision, cost, has_detected_submarine, value: list, is_lying: bool):
        self.label: int = label
        self.location = location
        self.precision = precision
        self.cost = cost
        self.has_detected_submarine = has_detected_submarine
        self.value = value
        self.is_lying: bool = is_lying
    def __repr__(self):
        return str(self.location) + ": " + str(self.has_detected_submarine)
    def __deepcopy__(self, memodict=None):
        return Measurement(
            self.label,
            self.location,
            self.precision,
            self.cost,
            self.has_detected_submarine,
            self.value,
            self.is_lying
        )

    def __iadd__(self, uncertainty: Uncertainty):
        self.value += uncertainty
        self.value &= domain
        return self
    def __add__(self, uncertainty: Uncertainty):
        result = self.__deepcopy__()
        result += uncertainty
        return result
class Batch:
    def __init__(self, label: int, timestamp: int, measurements: list):
        self.label: int = label
        self.timestamp: int = timestamp
        self.measurements: list = measurements
        self.type_id = 'batch'
        self.decay = 0
    def __len__(self):
        return self.measurements.__len__()
    def __iter__(self):
        return self.measurements.__iter__()
    def __repr__(self):
        return '\n'.join([str(x) for x in self])
    def __deepcopy__(self, memodict=None):
        return Batch(self.label, self.timestamp, self.measurements)

    def __iadd__(self, uncertainty: Uncertainty):
        self.measurements = [x + uncertainty for x in self]
        self.measurements = [x for x in self if x.value in domain and not x.value == domain]
        self.decay += uncertainty.absolute
        return self
    def __add__(self, uncertainty: Uncertainty):
        result = self.__deepcopy__()
        result += uncertainty
        return result

class ByzantineProblem:
    def __init__(self, ship_location, submarine_location, computation_rate):
        self.location = ship_location
        self.timestamp = 0
        self.total_cost = 0
        self.graph = Graph(
                node=Node(
                    label=str(submarine_location)
                )
            )
        self.batches: list = []
        self.submarine_location: IntervalExpression = submarine_location
        self.probe_counter: int = 1
        self.batch_counter: int = 1
        self.submarine = generate_submarine([random.randint(0, 100)])
        self.computation_rate = computation_rate
    def __repr__(self):
        # Create log
        # Ship
        csv_content = [strftime('%Y_%m_%d_%H_%M_%S')]
        csv_content += [self.location]
        csv_content += [self.timestamp]
        csv_content += [self.total_cost]
        csv_content += [self.submarine_location]

        # Submarine
        csv_content += [Probe.submarine_location]
        csv_content += [self.timestamp]

        # Graph
        csv_content += [self.graph.save_into_disk_and_get_file_name(
            '../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX'
        )]

        # Probes
        for batch in self.batches:
            for probe in batch:
                csv_content += [probe.label]
                csv_content += [batch.label]
                csv_content += [batch.timestamp]
                csv_content += [probe.location]
                csv_content += [probe.precision]
                csv_content += [batch.decay]
                csv_content += [probe.cost]
                csv_content += [probe.has_detected_submarine]
                csv_content += [probe.value]

        csv_content = list(map(lambda value: str(value), csv_content))

        stream = csv.StringIO()
        writer = csv.writer(stream)
        writer.writerow(csv_content)
        return stream.getvalue()

    def __iadd__(self, solution):
        self.timestamp += 1
        Probe.submarine_location, _ = next(self.submarine)

        # Create log
        sources = self.submarine_location
        targets = self.submarine_location.__deepcopy__()
        targets += AbsoluteUncertainty(0, 1)
        targets &= domain
        self.batches = [x + AbsoluteUncertainty(0, 1) for x in self.batches]
        self.batches = [x for x in self.batches if len(x) > 0]
        for target in targets:
            sub_sources = [source for source in sources if source in target]

            # Update graph
            self.graph += Hyperedge(
                sources=sub_sources,
                targets=[target],
                weight=0,
                label='Wait'
            )
        self.submarine_location.intervals = targets.intervals

        # Heuristic Ephemeral Interval Byzantine Register
        measurements = []
        for probe in solution.processes:
            self.total_cost += probe.cost

            reply = probe.synchronous_read()
            if reply == 'True':
                value = probe.interval
            else:
                value = ~probe.interval & domain

            measurements += [Measurement(
                label=self.probe_counter,
                location=probe.location,
                precision=probe.precision,
                cost=probe.cost,
                has_detected_submarine=reply == 'True',
                value=value,
                is_lying=False
            )]
            self.probe_counter += 1
        if len(measurements) > 0:
            batch = Batch(
                label=self.batch_counter,
                timestamp=self.timestamp,
                measurements=measurements
            )
            self.batches += [batch]
            self.batch_counter += 1
            # Generate result
            sources = self.submarine_location
            targets = self.submarine_location.__deepcopy__()
            cost = sum(x.cost for x in batch)
            for probe in batch:
                targets &= probe.value
            for source in sources:
                sub_targets = [target for target in targets if target in source]

                # Update graph
                self.graph += Hyperedge(
                    sources=[source],
                    targets=sub_targets,
                    weight=cost,
                    label=str(batch)
                )
            self.submarine_location.intervals = targets.intervals

        self.total_cost += get_alarm_cost(self.submarine_location)

        return self
class DynamicFormula:
    def __init__(self):
        self.submarine_location = None
        self.cost = {str((0, x)): {"": get_alarm_cost(x)} for x in domain}
        self.depth = 1
    def __iadd__(self, problem: ByzantineProblem):
        print(problem.submarine_location)
        for time in range(1, problem.computation_rate):
            for sub_interval in zip(chain.from_iterable(problem.submarine_location)):
                top5 = genetic.search(problem.submarine_location, self.cost, self.depth, 5)
                self.cost[str((time, sub_interval))] = {
                    str(x): genetic.evaluate(sub_interval, problem.submarine_location, self.cost, time)
                    for x in top5
                }

                print(str((time, sub_interval)) + ": " + str(list(self.cost[str((time, sub_interval))].values())))
            self.depth += 1

        self.submarine_location = problem.submarine_location
        return self
class GeneticSolution:
    def __init__(self):
        self.processes: list = []

    def __iadd__(self, formula: DynamicFormula):
        chosen_chromosome = genetic.search(formula.submarine_location, formula.cost, formula.depth, 1)[0]
        self.processes = []
        for gene_is_active, position in enumerate(chosen_chromosome):
            if gene_is_active:
                self.processes += [Probe(10, 3, [position])]

        return self

def ship(ship_location, submarine_location, computation_rate):
    problem = ByzantineProblem(
        ship_location=ship_location,
        submarine_location=submarine_location,
        computation_rate=computation_rate
    )
    formula = DynamicFormula()
    solution = GeneticSolution()

    while True:
        yield str(problem)

        formula += problem
        solution += formula
        problem += solution
