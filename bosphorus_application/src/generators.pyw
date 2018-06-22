# coding=utf-8
"""Generators

"""
import csv
from dynamic import dynamic
from genetic import domain, chromosome_size, generator
import graphs
from intervals import AbsoluteUncertainty, Uncertainty, Interval, IntervalExpression, LeftEndpoint, RightEndpoint
import math
import random
import time
import typing


def generate_submarine(location):
    """
    :rtype: object

    """
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

class Alert:
    """Alert

    """

    def __init__(self, interval, cost, message):
        self.interval = interval
        self.cost = cost
        self.message = message

    @staticmethod
    def trigger():
        """
        :rtype: object

        """
        # StateMachine.receive(win_input)
        # sys.exit(0)

    def __repr__(self):
        return self.interval
class RedAlert(Alert):
    """Red alert

    """
    interval_expression = IntervalExpression([Interval(
        left=LeftEndpoint(40, False, True),
        right=RightEndpoint(45, False, True)
    )])
    cost = 1000
    message = 'RED ALERT!!!'

    def __init__(self):
        super().__init__(
            interval=RedAlert.interval_expression,
            cost=RedAlert.cost,
            message=RedAlert.message
        )
class YellowAlert(Alert):
    """Yellow alert

    """
    interval_expression = IntervalExpression([Interval(
        left=LeftEndpoint(45, True, False),
        right=RightEndpoint(70, False, True)
    )])
    cost = 50
    message = 'Yellow alert!'

    def __init__(self):
        super().__init__(
            interval=YellowAlert.interval_expression,
            cost=YellowAlert.cost,
            message=YellowAlert.message
        )

class Probe:
    """Probe

    """
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
        """

        :return:
        """
        # Calculate measurements
        values = zip(self.location, Probe.submarine_location)
        distance = sum((x[0] - x[1]) ** 2 for x in values) ** 0.5
        reply = str(distance <= self.precision)

        return reply
class Measurement:
    """Measurement

    """

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
    def __deepcopy__(self, memodict={}):
        return Measurement(self.label, self.location, self.precision, self.cost, self.has_detected_submarine, self.value, self.is_lying)

    def __iadd__(self, uncertainty: Uncertainty):
        self.value += uncertainty
        self.value &= domain()
        return self
    def __add__(self, uncertainty: Uncertainty):
        result = self.__deepcopy__()
        result += uncertainty
        return result
class Batch:
    """Batch

    """

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
    def __deepcopy__(self, memodict={}):
        return Batch(self.label, self.timestamp, self.measurements)

    def __iadd__(self, uncertainty: Uncertainty):
        self.measurements = [x + uncertainty for x in self]
        self.measurements = [x for x in self if x.value in domain() and not x.value == domain()]
        self.decay += uncertainty.absolute
        return self
    def __add__(self, uncertainty: Uncertainty):
        result = self.__deepcopy__()
        result += uncertainty
        return result

class ShipState:
    """Ship state

    """

    def __init__(self, location, timestamp, total_cost, graph, batches, state, probe_counter, batch_counter, submarine, genes):
        self.location = location
        self.timestamp = timestamp
        self.total_cost = total_cost
        self.graph = graph
        self.batches = batches
        self.state = state
        self.probe_counter = probe_counter
        self.batch_counter = batch_counter
        self.submarine = submarine
        self.genes = genes
class AlarmOutput:
    """Alarm output

    """

    def __init__(self, state: ShipState):
        self.state: ShipState = state
class HelicopterOutput:
    """Helicopter output

    """

    def __init__(self, processes: list, state: ShipState):
        self.processes: list = processes
        self.state: ShipState = state
class ClockOutput:
    """Clock output

    """

    def __init__(self, decay: int, state: ShipState):
        self.decay: int = decay
        self.state: ShipState = state
class HelicopterInput:
    """Helicopter input

    """

    def __init__(self, state: ShipState):
        self.state: ShipState = state
class ClockInput:
    """Clock input

    """

    def __init__(self, state: ShipState):
        self.state: ShipState = state

class Solution:
    """Solution

    """

    def __init__(self, output: list):
        self.output: list = output
class Problem:
    """Problem

    """

    def __init__(self, inputs: list):
        self.inputs: list = inputs
class Formula:
    """Formula

    """

    def __init__(self, search_function: typing.Callable[[list], Solution], parameters: list):
        self.search_function: typing.Callable[[list], Solution] = search_function
        self.parameters: list = parameters

def wait(clock_output: ClockOutput) -> ClockInput:
    """

    :return:
    :param clock_output:
    :return:
    """
    decay = clock_output.decay
    state = clock_output.state

    state.timestamp += 1
    Probe.submarine_location, _ = next(state.submarine)

    # Create log
    sources = state.state
    targets = state.state.__deepcopy__()
    targets += AbsoluteUncertainty(0, decay)
    targets &= domain()
    state.batches = [x + AbsoluteUncertainty(0, decay) for x in state.batches]
    state.batches = [x for x in state.batches if len(x) > 0]

    for target in targets:
        sub_sources = [source for source in sources if source in target]

        # Update graph
        state.graph += graphs.Hyperedge(
            sources=sub_sources,
            targets=[target],
            weight=0,
            label='Wait'
        )

    state.state.intervals = targets.intervals

    inputs = ClockInput(state)
    return inputs
def try_alert(alarm_output: AlarmOutput):
    """

    :param alarm_output:
    """
    state = alarm_output.state

    for alert in [RedAlert(), YellowAlert()]:
        if (state.state & alert.interval) != IntervalExpression.empty():
            state.total_cost += alert.cost
            alert.trigger()
            break
def get_fresh_measurements(helicopter_output: HelicopterOutput) -> HelicopterInput:
    """

    :param helicopter_output:
    :return:
    """
    processes = helicopter_output.processes
    state = helicopter_output.state

    # Heuristic Ephemeral Interval Byzantine Register
    measurements = []
    for probe in processes:
        state.total_cost += probe.cost

        reply = probe.synchronous_read()
        if reply == 'True':
            value = probe.interval
        else:
            value = ~probe.interval & domain()

        measurements += [Measurement(
            label=state.probe_counter,
            location=probe.location,
            precision=probe.precision,
            cost=probe.cost,
            has_detected_submarine=reply == 'True',
            value=value,
            is_lying=False
        )]

        state.probe_counter += 1

    if len(measurements) > 0:
        batch = Batch(
            label=state.batch_counter,
            timestamp=state.timestamp,
            measurements=measurements
        )
        state.batches += [batch]
        state.batch_counter += 1

        # Generate result
        sources = state.state
        targets = state.state.__deepcopy__()
        cost = sum(x.cost for x in batch)

        for probe in batch:
            targets &= probe.value

        for source in sources:
            sub_targets = [target for target in targets if target in source]

            # Update graph
            state.graph += graphs.Hyperedge(
                sources=[source],
                targets=sub_targets,
                weight=cost,
                label=str(batch)
            )

        state.state.intervals = targets.intervals

    inputs = HelicopterInput(state)
    return inputs

def search(parameters: list) -> Solution:
    """

    :param parameters:
    :return:
    """
    gene_pool = next(parameters[0].genes)
    chosen_chromosome = random.choice(gene_pool)
    processes = []
    for gene_is_active, position in zip(chosen_chromosome, range(0, chromosome_size)):
        if gene_is_active:
            processes += [Probe(10, 3, [position])]
    # print(len(processes))

    output = [ClockOutput(parameters[1], parameters[0])]
    output += [HelicopterOutput(processes, parameters[0])]
    output += [AlarmOutput(parameters[0])]


    return Solution(output)

# Search algorithm
def formulate(problem: Problem) -> Formula:
    """

    :param problem:
    :return:
    """
    state = None
    for x in problem.inputs:
        if type(x) == HelicopterInput:
            state = x.state
        elif type(x) == ClockInput:
            state = x.state

    parameters = [state]
    parameters += [1]

    return Formula(search, parameters)
def apply(formula: Formula) -> Solution:
    """

    :param formula:
    :return:
    """
    return formula.search_function(formula.parameters)
def execute(solution: Solution) -> Problem:
    """

    :param solution:
    :return:
    """
    inputs = []
    for x in solution.output:
        if type(x) == AlarmOutput:
            try_alert(x)
        elif type(x) == HelicopterOutput:
            if len(inputs) > 0 and (type(inputs[-1]) == ClockInput or type(inputs[-1]) == HelicopterOutput):
                x.state = inputs[-1].state
                inputs[-1] = get_fresh_measurements(x)
            else:
                inputs += [get_fresh_measurements(x)]
        elif type(x) == ClockOutput:
            if len(inputs) > 0 and (type(inputs[-1]) == ClockInput or type(inputs[-1]) == HelicopterOutput):
                x.state = inputs[-1].state
                inputs[-1] = [wait(x)]
            else:
                inputs += [wait(x)]

    return Problem(inputs)

def generate_ship(location):
    state = domain()
    cost = {
        str((0, x)): {
            "": (
                RedAlert.cost
                if (x & RedAlert.interval_expression[0]) != Interval.empty()
                else
                YellowAlert.cost
                if (x & YellowAlert.interval_expression[0]) != Interval.empty()
                else
                0
            )
        } for x in Interval(
            left=LeftEndpoint(0, False, True),
            right=RightEndpoint(100, False, True)
        )
    }
    time = 1
    genetic = generator(state, cost, time)

    gen = dynamic(100, state, cost, genetic, time)

    submarine = generate_submarine([random.randint(0, 100)])

    problem = Problem([ClockInput(
        ShipState(
            location=location,
            timestamp=0,
            total_cost=0,
            graph=graphs.Graph(
                node=graphs.Node(
                    label=domain().intervals[0]
                )
            ),
            batches=[],
            state=state,
            probe_counter=1,
            batch_counter=1,
            submarine=submarine,
            genes=genetic
        )
    )])
    for _ in gen:
        state = problem.inputs[0].state

        # Create log
        # Ship
        csv_content = [time.strftime('%Y_%m_%d_%H_%M_%S')]
        csv_content += [state.location]
        csv_content += [state.timestamp]
        csv_content += [state.total_cost]
        csv_content += [state.state]

        # Submarine
        csv_content += [Probe.submarine_location]
        csv_content += [state.timestamp]

        # Graph
        csv_content += [state.graph.save_into_disk_and_get_file_name(
            '../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX'
        )]

        # Probes
        for batch in state.batches:
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
        stream_value = stream.getvalue()

        yield stream_value


        formula = formulate(problem)
        solution = apply(formula)
        problem = execute(solution)

def test():
    state = domain()
    cost = {
        str((0, x)): {
            "": (
                RedAlert.cost
                if (x & RedAlert.interval_expression[0]) != Interval.empty()
                else
                YellowAlert.cost
                if (x & YellowAlert.interval_expression[0]) != Interval.empty()
                else
                0
            )
        } for x in Interval(
            left=LeftEndpoint(0, False, True),
            right=RightEndpoint(100, False, True)
        )
    }
    time = 1
    genetic = generator(state, cost, time)

    gen = dynamic(100, state, cost, genetic, time)

    for _ in gen:
        print(cost)