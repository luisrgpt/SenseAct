# coding=utf-8
"""Submarines and probes

"""

import copy
import csv
from deap import algorithms, base, creator, tools
import graphs
import intervals
import itertools
import math
import os
import random
import socket
import sys
import time
import threading
import typing

###############################################################################
# World
#
# Properties:
# - list of locations
#


class InterfaceHandler(threading.Thread):
    """Interface handler

    """
    stop_flag: threading.Event = None
    play_flag: threading.Event = None

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        InterfaceHandler.play_flag = threading.Event()
        InterfaceHandler.stop_flag = threading.Event()

    @staticmethod
    def wait():
        """
        :rtype: object

        """
        InterfaceHandler.play_flag.wait()
        if InterfaceHandler.stop_flag.wait(0):
            sys.exit()

    # noinspection PyProtectedMember
    def run(self):
        """
        :rtype: object

        """
        while True:
            try:
                message = self.client_socket.recv(10)
            except OSError:
                os._exit(1)
            else:
                code = message.decode('utf8')
                if code == 'quit':
                    os._exit(1)
                elif code == 'next':
                    InterfaceHandler.play_flag.set()
                    InterfaceHandler.play_flag.clear()
                # elif code == 'pause':
                #    InterfaceHandler.is_waiting = True
                # elif code == 'play':
                #    InterfaceHandler.is_waiting = False
                elif code == 'stop':
                    InterfaceHandler.stop_flag.set()
                    InterfaceHandler.play_flag.set()
                    InterfaceHandler.play_flag.clear()
                # elif code == 'repeat_all':
                #    InterfaceHandler.reset_condition_is_not_satisfied = False
                #    InterfaceHandler.is_waiting = False


class Simulation:
    """Simulation

    """
    log_writer: csv.writer = None
    agents: list = None
    client_socket: socket.socket = None
    lock: threading.Lock = None
    log_prefix = './log/'
    log_suffix = '.csv'
    frame_per_second = 1

    @staticmethod
    def restart():
        """
        :rtype: object

        """
        with Simulation.lock:
            Simulation.client_socket.send('reset'.encode('utf8'))
            Simulation.stack = []
            Simulation.dictionary = {}

            Simulation.log_file_name = (
                Simulation.log_prefix +
                str(time.strftime('%Y_%m_%d_%H_%M_%S')) +
                Simulation.log_suffix
            )
            if not os.path.exists(Simulation.log_prefix):
                os.makedirs(Simulation.log_prefix)

            time.sleep(1)

            Simulation.agents = []
            Simulation.probes = []

            Simulation.win_condition_is_not_satisfied = True
            Simulation.lose_condition_is_not_satisfied = True

            if Simulation.log_file is not None:
                Simulation.log_file.close()
            Simulation.log_file = open(Simulation.log_file_name, 'a+', newline='')
            Simulation.log_writer = csv.writer(Simulation.log_file)

    @staticmethod
    def start():
        """
        :rtype: object

        """
        Simulation.lock = threading.Lock()
        Simulation.log_file = None

        hostname = socket.gethostname()
        port = 3000
        server_socket = socket.socket()
        server_socket.bind((hostname, port))
        server_socket.listen(1)
        Simulation.client_socket, _ = server_socket.accept()
        InterfaceHandler(Simulation.client_socket).start()

        Simulation.restart()

    @staticmethod
    def put(csv_content):
        """

        :param csv_content:
        """
        csv_content = list(map(lambda value: str(value), csv_content))
        csv_content.insert(0, time.strftime('%Y_%m_%d_%H_%M_%S'))

        stream = csv.StringIO()
        writer = csv.writer(stream)
        writer.writerow(csv_content)
        stream_value = stream.getvalue()
        message = stream_value.encode('utf8')

        with Simulation.lock:
            Simulation.client_socket.send(message)
            Simulation.log_writer.writerow(csv_content)

    @staticmethod
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

###############################################################################
# Movable
#
# Properties:
# - identification
# - initial location
# - movement heuristic
# 
# Behaviour:
# - moves according to previous location
#


class MovementHandler(threading.Thread):
    """Movement handler

    """
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        """
        :rtype: object

        """
        while True:
            InterfaceHandler.wait()
            self.state.movement()


class Movable:
    """Movable

    """
    def __init__(self, type_id, label, location, movement):
        self.type_id = type_id
        self.label = label
        self.location = location
        self.movement = movement
        MovementHandler(self).start()

###############################################################################
# Decidable
#
# Properties
# - strategy heuristic
#
# Behaviour:
# - chooses actions


class StrategyHandler(threading.Thread):
    """Strategy handler

    """
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        """
        :rtype: object

        """
        self.state.strategy()


class Decidable:
    """Decidable

    """

    def __init__(self, strategy):
        self.strategy = strategy

    def deploy(self):
        """
        :rtype: object

        """
        StrategyHandler(self).start()

###############################################################################
# Probe
#
# Inheritance
# - Movable
# - Awareable
# - Decidable
#
# Properties:
# - cost
# - precision
#
# Behaviour:
# - measures its distance from other world objects 
# - sends measurement to submarine


class Process:
    """Process

    """
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
        submarine_location, _ = Submarine.get_values()
        Submarine.read_flag.set()
        values = zip(self.location, submarine_location)
        distance = sum((x[0] - x[1])**2 for x in values)**0.5
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
        self.value &= Simulation.domain()
        return self

    def __add__(self, uncertainty: intervals.Uncertainty):
        result = copy.deepcopy(self)
        result += uncertainty
        return result


class Batch:
    """Batch

    """
    def __init__(self, label: int, timestamp: int):
        self.label: int = label
        self.timestamp: int = timestamp
        self.measurements: list = []
        self.type_id = 'batch'
        self.decay = 0

    def __len__(self):
        return self.measurements.__len__()

    def __iter__(self):
        return self.measurements.__iter__()

    def __iadd__(self, uncertainty: intervals.Uncertainty):
        self.measurements = [x + uncertainty for x in self]
        self.measurements = [x for x in self if x.value in Simulation.domain() and not x.value == Simulation.domain()]
        self.decay += uncertainty.absolute
        return self

    def __add__(self, uncertainty: intervals.Uncertainty):
        result = copy.deepcopy(self)
        result += uncertainty
        return result

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
        Simulation.client_socket.send('win'.encode('utf8'))
        InterfaceHandler.wait()

    def __repr__(self):
        return self.interval


class RedAlert(Alert):
    """Red alert

    """
    interval_expression = intervals.IntervalExpression([intervals.Interval(
        left=intervals.LeftEndpoint(40, False, True),
        right=intervals.RightEndpoint(45, False, True)
    )])
    cost = 10
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
    cost = 5
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
    def __init__(self, location, timestamp, total_cost, graph, batches, state, probe_counter, batch_counter):
        self.location = location
        self.timestamp = timestamp
        self.total_cost = total_cost
        self.graph = graph
        self.batches = batches
        self.state = state
        self.probe_counter = probe_counter
        self.batch_counter = batch_counter


class AlarmOutput:
    """Alarm output

    """
    def __init__(self, alert: Alert, state: ShipState):
        self.alert: Alert = alert
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
# Inheritance
# - Movable
# - Awareable
# - Decidable
#
# Properties
# - balance
# - list of probes
#
# Behaviour:
# - sends probes and attacks if detects enemy submarines
# OR
# - hacks probes and moves towards enemy submarines


class Ship(Movable, Decidable):
    """Ship

    """
    def no_movement(self):
        """
        :rtype: object

        """
        pass

    @staticmethod
    def wait(clock_output: ClockOutput) -> ClockInput:
        """

        :return:
        :param clock_output:
        :return:
        """
        decay = clock_output.decay
        state = clock_output.state

        # Create log
        # Ship
        csv_content = [state.location]
        csv_content += [state.timestamp]
        csv_content += [state.total_cost]
        csv_content += [state.state]

        # Submarine
        submarine_location, submarine_timestamp = Submarine.get_values()
        csv_content += [submarine_location]
        csv_content += [submarine_timestamp]

        # Graph
        csv_content += [state.graph.save_into_disk_and_get_file_name(
            '../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX'
        )]

        # Probes
        for batch in state.batches:
            for probe in batch:
                csv_content += [probe.id]
                csv_content += [batch.id]
                csv_content += [batch.timestamp]
                csv_content += [probe.location]
                csv_content += [probe.precision]
                csv_content += [batch.decay]
                csv_content += [probe.cost]
                csv_content += [probe.has_detected_submarine]
                csv_content += [probe.value]
        Simulation.put(csv_content)
        InterfaceHandler.wait()
        state.timestamp += 1

        # Create log
        sources = state.state
        targets = copy.deepcopy(state.state)
        targets += intervals.AbsoluteUncertainty(0, decay)
        targets &= Simulation.domain()
        state.batches = [x + intervals.AbsoluteUncertainty(0, decay) for x in state.batches]
        state.batches = [x for x in state.batches if len(x) > 0]

        for target in targets:
            sub_sources = [source for source in sources if source in target]

            # Update graph
            state.graph += graphs.Hyperedge(
                sources=sub_sources,
                targets=[target],
                weight=0,
                label='t' + str(state.timestamp)
            )

        state.state = targets

        inputs = ClockInput(state)
        return inputs

    @staticmethod
    def try_alert(alarm_output: AlarmOutput):
        """

        :param alarm_output:
        """
        alert = alarm_output.alert
        state = alarm_output.state

        if state.state in alert.interval:
            state.total_cost = alert.cost
            alert.trigger()

    @staticmethod
    def get_fresh_measurements(helicopter_output: HelicopterOutput) -> HelicopterInput:
        """

        :param helicopter_output:
        :return:
        """
        processes = helicopter_output.processes
        state = helicopter_output.state

        # Heuristic Ephemeral Interval Byzantine Register
        batch = Batch(
            label=state.batch_counter,
            timestamp=state.timestamp
        )

        cost = 0
        for probe in processes:
            cost += probe.cost

            reply = probe.synchronous_read()
            if reply == 'True':
                value = probe.interval
            else:
                value = ~probe.interval & Simulation.domain()
            
            batch.measurements += [Measurement(
                label=state.probe_counter,
                location=probe.location,
                precision=probe.precision,
                cost=probe.cost,
                has_detected_submarine=reply == 'True',
                value=value,
                is_lying=False
            )]

            state.probe_counter += 1

        state.batches += [batch]
        state.batch_counter += 1
        state.total_cost += cost

        # Generate result
        sources = state.state
        targets = copy.deepcopy(state.state)
        for probe in batch:
            targets &= probe.value

        for source in sources:
            sub_targets = [target for target in targets if target in source]

            # Update graph
            state.graph += graphs.Hyperedge(
                sources=[source],
                targets=sub_targets,
                weight=cost,
                label='b' + str(batch.label)
            )

        state.state = targets

        inputs = HelicopterInput(state)
        return inputs

    # Problem solving search algorithm
    def strategy(self):
        """

        :return:
        """
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

            # Get all genes from chromosome
            genes = [index for index, value in enumerate(chromosome) if value]
            cost = len(genes) * 10

            # Generate domain of answers
            answers_domain = list(itertools.product(*[(False, True) for _ in genes]))
            n_answers = len(answers_domain)
            # For each combination of answers
            for answers in answers_domain:
                for gene, answer_is_true in zip(genes, answers):
                    targets = intervals.IntervalExpression(
                        [intervals.Interval(
                            left=intervals.LeftEndpoint(gene - 3, False, True),
                            right=intervals.RightEndpoint(gene + 3, False, True)
                        )]
                    )
                    targets = targets if answer_is_true else ~targets
                    targets &= state
                    
                    cost += (
                        YellowAlert.cost / n_answers if targets in YellowAlert.interval_expression
                        else 
                        RedAlert.cost / n_answers if targets in RedAlert.interval_expression
                        else
                        0
                    )

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
            HIGH = len(chromosome) - 1

            flip_signal = number_of_flips > 0

            # for each number of flips
            for x in range(abs(number_of_flips)):
                # break loop if all genes are flipped
                if all(y == flip_signal for y in chromosome):
                    break

                # repeat until gene is the opposite of its flip
                y = random.randint(0, HIGH)
                while chromosome[y] == flip_signal:
                    y = random.randint(0, HIGH)
                # flip value
                chromosome[y] = type(chromosome[y])(not chromosome[y])
    
            return chromosome,

        # Start parameters
        gene_pool_size = 100
        chromosome_size = 101
        percentage = 2
        # Mutate parameters
        mut_parameter = 2
        # Select parameters
        # k = 10
        # Algorithm parameters
        cx_pb = 1
        mut_pb = 1
        n_gen = 10
        verbose = False
        
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

        def search(parameters: list) -> Solution:
            """

            :param parameters:
            :return:
            """
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
                    processes += [Process(10, 3, [position])]
            print(len(processes))

            output = [AlarmOutput(parameters[1], parameters[0])]
            output += [ClockOutput(parameters[2], parameters[0])]
            output += [HelicopterOutput(processes, parameters[0])]

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
            parameters += [RedAlert()]
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
                    self.try_alert(x)
                elif type(x) == HelicopterOutput:
                    if len(inputs) > 0 and (type(inputs[-1]) == ClockInput or type(inputs[-1]) == HelicopterOutput):
                        x.state = inputs[-1].state
                        inputs[-1] = self.get_fresh_measurements(x)
                    else:
                        inputs += [self.get_fresh_measurements(x)]
                elif type(x) == ClockOutput:
                    if len(inputs) > 0 and (type(inputs[-1]) == ClockInput or type(inputs[-1]) == HelicopterOutput):
                        x.state = inputs[-1].state
                        inputs[-1] = [self.wait(x)]
                    else:
                        inputs += [self.wait(x)]

            return Problem(inputs)

        # Problem Solving Search Algorithm
        graph = graphs.Graph(
            node=graphs.Node(
                label=Simulation.domain().intervals[0]
            )
        )

        initial_state = ShipState(
            location=self.location,
            timestamp=0,
            total_cost=0,
            graph=graph,
            batches=[],
            state=Simulation.domain(),
            probe_counter=1,
            batch_counter=1
        )
        inputs = [ClockInput(initial_state)]
        problem = Problem(inputs)
        while True:
            formula = formulate(problem)
            solution = apply(formula)
            problem = execute(solution)

    def __init__(self, location):
        Movable.__init__(self, 'ship', 'ship', location, self.no_movement)
        Decidable.__init__(self, self.strategy)


class Submarine(Movable, Decidable):
    """Submarine

    """
    read_flag: threading.Event = None

    @staticmethod
    def get_values():
        """

        :return:
        """
        Submarine.read_flag.wait()
        Submarine.read_flag.clear()
        return Submarine.location, Submarine.timestamp

    @staticmethod
    def move_to_submarine():
        """
        :rtype: object

        """
        velocity = list(map(lambda value: -value, Submarine.location))
        norm = math.sqrt(sum(value**2 for value in velocity))
        if norm == 0:
            Simulation.client_socket.send('lose'.encode('utf8'))
            InterfaceHandler.wait()

        normalized_vector = list(map(lambda value: value / norm, velocity))

        Submarine.location = list(map(lambda value: value[0] + value[1], zip(Submarine.location, normalized_vector)))
        Submarine.timestamp += 1
        Submarine.read_flag.set()

    def hack_random_probe(self):
        """
        :rtype: object

        """
        pass

    def __init__(self, location):
        Submarine.read_flag = threading.Event()

        Submarine.location = location
        Submarine.timestamp = 0
        Submarine.read_flag.set()

        Movable.__init__(self, 'submarine', 'submarine', location, self.move_to_submarine)
        Decidable.__init__(self, self.hack_random_probe)


# graphs.test()
# intervals.test()
Simulation.start()
while True:
    InterfaceHandler.play_flag.wait()
    Simulation.agents.append(Ship([0]))
    Simulation.agents.append(Submarine([random.randint(0, 100)]))

    InterfaceHandler.stop_flag.clear()
    for machine in Simulation.agents:
        machine.deploy()

    Simulation.client_socket.send('enable_stop'.encode('utf8'))
    InterfaceHandler.stop_flag.wait()
    Simulation.restart()
