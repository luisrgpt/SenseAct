# coding=utf-8
"""Generators

"""

import copy
import csv
from deap import algorithms, base, creator, tools
import graphs
import intervals
import math
import random
import time
import typing


def generate_submarine(location):
    """
    :rtype: object

    """
    timestamp = 0
    norm = 1
    while norm > 0:
        yield location, timestamp

        velocity = [-x for x in location]
        norm = math.sqrt(sum(x**2 for x in velocity))

        normalized_vector = [x / norm for x in velocity]

        location = [x[0] + x[1] for x in zip(location, normalized_vector)]
        timestamp += 1


def domain():
    """

    :return:
    """
    return intervals.IntervalExpression(
        intervals=[intervals.Interval(
            left=intervals.LeftEndpoint(0, False, True),
            right=intervals.RightEndpoint(100, False, True)
        )]
    )


class Probe:
    """Probe

    """
    submarine_location = None

    def __init__(self, cost: int, precision: int, location: list):
        self.cost: int = cost
        self.precision: int = precision
        self.location = location
        self.interval = intervals.IntervalExpression([intervals.Interval(
            left=intervals.LeftEndpoint(location[0] - precision, False, True),
            right=intervals.RightEndpoint(location[0] + precision, False, True)
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

    def __iadd__(self, uncertainty: intervals.Uncertainty):
        self.value += uncertainty
        self.value &= domain()
        return self

    def __add__(self, uncertainty: intervals.Uncertainty):
        result = copy.deepcopy(self)
        result += uncertainty
        return result

    def __repr__(self):
        return str(self.location) + ": " + str(self.has_detected_submarine)


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

    def __iadd__(self, uncertainty: intervals.Uncertainty):
        self.measurements = [x + uncertainty for x in self]
        self.measurements = [x for x in self if x.value in domain() and not x.value == domain()]
        self.decay += uncertainty.absolute
        return self

    def __add__(self, uncertainty: intervals.Uncertainty):
        result = copy.deepcopy(self)
        result += uncertainty
        return result

    def __repr__(self):
        return '\n'.join([str(x) for x in self])


###############################################################################
# Alert


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
    interval_expression = intervals.IntervalExpression([intervals.Interval(
        left=intervals.LeftEndpoint(40, False, True),
        right=intervals.RightEndpoint(45, False, True)
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
    interval_expression = intervals.IntervalExpression([intervals.Interval(
        left=intervals.LeftEndpoint(45, True, False),
        right=intervals.RightEndpoint(70, False, True)
    )])
    cost = 50
    message = 'Yellow alert!'

    def __init__(self):
        super().__init__(
            interval=YellowAlert.interval_expression,
            cost=YellowAlert.cost,
            message=YellowAlert.message
        )


class ShipState:
    """Ship state

    """

    def __init__(self, location, timestamp, total_cost, graph, batches, state, probe_counter, batch_counter, submarine):
        self.location = location
        self.timestamp = timestamp
        self.total_cost = total_cost
        self.graph = graph
        self.batches = batches
        self.state = state
        self.probe_counter = probe_counter
        self.batch_counter = batch_counter
        self.submarine = submarine


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


###############################################################################
# Submarine
#
# Properties
# - balance
# - list of probes
#
# Behaviour:
# - sends probes and attacks if detects enemy submarines
# OR
# - hacks probes and moves towards enemy submarines

# Start parameters
gene_pool_size = 10
chromosome_size = 101
percentage = 2
# Mutate parameters
mut_parameter = 2
# Select parameters
# k = 10
# Algorithm parameters
cx_pb = 1
mut_pb = 1
n_gen = 100
verbose = True


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
    targets = copy.deepcopy(state.state)
    targets += intervals.AbsoluteUncertainty(0, decay)
    targets &= domain()
    state.batches = [x + intervals.AbsoluteUncertainty(0, decay) for x in state.batches]
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

    state.state = targets

    inputs = ClockInput(state)
    return inputs


def try_alert(alarm_output: AlarmOutput):
    """

    :param alarm_output:
    """
    state = alarm_output.state

    for alert in [RedAlert(), YellowAlert()]:
        if (state.state & alert.interval) != intervals.IntervalExpression.empty():
            state.total_cost = alert.cost
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
        targets = copy.deepcopy(state.state)
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

        state.state = targets

    inputs = HelicopterInput(state)
    return inputs


def gen_gene(to_true_gen_pb: int):
    """

    :type to_true_gen_pb: int
    :param to_true_gen_pb:
    :return:
    """
    return random.randint(1, 100) <= to_true_gen_pb


def eval_probes(chromosome: list, state: intervals.IntervalExpression):
    """

    :type state: intervals.IntervalExpression
    :param state:
    :type chromosome: list
    :param chromosome:
    :return:
    """
    # current = time.time()
    # Get all genes from chromosome
    genes = [index for index, value in enumerate(chromosome) if value]

    # When there are no probes to send
    if len(genes) == 0:
        cost = (
            RedAlert.cost
            if (state & RedAlert.interval_expression) != intervals.IntervalExpression.empty()
            else
            YellowAlert.cost
            if (state & YellowAlert.interval_expression) != intervals.IntervalExpression.empty()
            else
            0
        )
        return cost,

    answers = intervals.IntervalExpression(
        [intervals.Interval(
            left=intervals.LeftEndpoint(gene - 3, False, True),
            right=intervals.RightEndpoint(gene + 3, False, True)
        ) for gene in genes]
    ).intervals
    n_answers = len(answers) + 1

    # First criteria: cost of sum of all probes
    cost = len(genes) * 10

    # Second criteria: cost when all probes reply no
    noes = answers
    new_state = ~intervals.IntervalExpression(noes)
    new_state &= state
    cost += (
                RedAlert.cost
                if (new_state & RedAlert.interval_expression) != intervals.IntervalExpression.empty()
                else
                YellowAlert.cost
                if (new_state & YellowAlert.interval_expression) != intervals.IntervalExpression.empty()
                else
                0
            ) / n_answers

    # Third criteria: cost when certain probes reply yes
    for position, yes in enumerate(answers):
        noes = answers[:position - 1] + answers[position + 1:]
        new_state = ~intervals.IntervalExpression(noes)
        new_state |= intervals.IntervalExpression([yes])
        new_state &= state
        cost += (
                    RedAlert.cost
                    if (new_state & RedAlert.interval_expression) != intervals.IntervalExpression.empty()
                    else
                    YellowAlert.cost
                    if (new_state & YellowAlert.interval_expression) != intervals.IntervalExpression.empty()
                    else
                    0
                ) / n_answers

    # end = time.time()
    # diff = end - current
    # print("ev: " + str(genes) + " -> " + str(diff))
    return -cost,


# Assumption: both chromosomes have the same size
def cx_biased_one_point(chromosome_1: list, chromosome_2: list):
    """

    :type chromosome_1: list
    :param chromosome_1:
    :param chromosome_2:
    :return:
    """
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

    cx_point = random.randint(min_point, max_point)
    chromosome_1[cx_point:], chromosome_2[cx_point:] = chromosome_2[cx_point:], chromosome_1[cx_point:]

    return chromosome_1, chromosome_2


def mut_biased_flip_bit(chromosome: list, max_number_of_flips: int):
    """

    :type chromosome: list
    :param max_number_of_flips:
    :param chromosome:
    :return:
    """
    number_of_flips = random.randint(-max_number_of_flips, max_number_of_flips)
    high = len(chromosome) - 1

    flip_signal = number_of_flips > 0

    # for each number of flips
    for x in range(abs(number_of_flips)):
        # break loop if all genes are flipped
        if all(y == flip_signal for y in chromosome):
            break

        # repeat until gene is the opposite of its flip
        y = random.randint(0, high)
        while chromosome[y] == flip_signal:
            y = random.randint(0, high)
        # flip value
        chromosome[y] = type(chromosome[y])(not chromosome[y])

    return chromosome,


def search(parameters: list) -> Solution:
    """

    :param parameters:
    :return:
    """
    global toolbox
    toolbox.register(
        'evaluate',
        eval_probes,
        state=parameters[0].state
    )

    gene_pool = toolbox.gene_pool(
        n=gene_pool_size
    )

    gene_pool = algorithms.eaSimple(
        population=gene_pool,
        toolbox=toolbox,
        cxpb=cx_pb,
        mutpb=mut_pb,
        ngen=n_gen,
        verbose=verbose
    )

    chosen_chromosome = gene_pool[0][random.randint(0, len(gene_pool))]
    processes = []
    for gene_is_active, position in zip(chosen_chromosome, range(0, chromosome_size)):
        if gene_is_active:
            processes += [Probe(10, 3, [position])]
    # print(len(processes))

    output = [ClockOutput(parameters[1], parameters[0])]
    output += [HelicopterOutput(processes, parameters[0])]
    output += [AlarmOutput(parameters[0])]


    return Solution(output)


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


creator.create(
    'FitnessMax',
    base.Fitness,
    weights=(1.0,)
)
creator.create(
    'Chromosome',
    list,
    fitness=creator.FitnessMax
)

toolbox = base.Toolbox()
toolbox.register(
    'gene',
    gen_gene,
    to_true_gen_pb=percentage
)
toolbox.register(
    'chromosome',
    tools.initRepeat,
    creator.Chromosome,
    toolbox.gene,
    n=chromosome_size
)
toolbox.register(
    'gene_pool',
    tools.initRepeat,
    list,
    toolbox.chromosome
)
toolbox.register(
    'mate',
    cx_biased_one_point
)
toolbox.register(
    'mutate',
    mut_biased_flip_bit,
    max_number_of_flips=mut_parameter
)
toolbox.register(
    'select',
    tools.selBest
)


def generate_ship(location):
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
            state=domain(),
            probe_counter=1,
            batch_counter=1,
            submarine=submarine
        )
    )])
    while True:
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
