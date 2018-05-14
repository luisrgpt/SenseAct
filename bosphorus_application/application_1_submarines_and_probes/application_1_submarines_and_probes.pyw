import ast
import asyncio
import atexit
import csv
import functools
import graphs
import intervals
import math
import os
import queue
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
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        InterfaceHandler.play_flag = threading.Event()
        InterfaceHandler.stop_flag = threading.Event()

    def wait():
        InterfaceHandler.play_flag.wait()
        if InterfaceHandler.stop_flag.wait(0):
            sys.exit()

    def run(self):
        while True:
            try:
                message = self.client_socket.recv(10)
            except:
                os._exit(1)
            else:
                code = message.decode('utf8')
                if code == 'quit':
                    os._exit(1)
                elif code == 'next':
                    InterfaceHandler.play_flag.set()
                    InterfaceHandler.play_flag.clear()
                #elif code == 'pause':
                #    InterfaceHandler.is_waiting = True
                #elif code == 'play':
                #    InterfaceHandler.is_waiting = False
                elif code == 'stop':
                    InterfaceHandler.stop_flag.set()
                    InterfaceHandler.play_flag.set()
                    InterfaceHandler.play_flag.clear()
                #elif code == 'repeat_all':
                #    InterfaceHandler.reset_condition_is_not_satisfied = False
                #    InterfaceHandler.is_waiting = False

class Simulation:
    log_prefix = './log/'
    log_suffix = '.csv'
    frame_per_second = 1

    def restart():
        with Simulation.lock:
            Simulation.client_socket.send('reset'.encode('utf8'))
            Simulation.stack = []
            Simulation.dictionary = {}

            Simulation.log_file_name = Simulation.log_prefix + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + Simulation.log_suffix
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

    def start():
        Simulation.lock = threading.Lock()
        Simulation.log_file = None

        hostname = socket.gethostname()
        port = 3000
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((hostname, port))
        server_socket.listen(1)
        Simulation.client_socket, _ = server_socket.accept()
        InterfaceHandler(Simulation.client_socket).start()
        
        Simulation.restart()
        #Simulation.awareness_handlers = {}


    def put(csv_content):
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

    def domain():
        return intervals.IntervalExpression([intervals.Interval(intervals.LeftEndpoint(0, False, True), intervals.RightEndpoint(100, False, True))])

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
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        while True:
            InterfaceHandler.wait()
            self.state.movement()

class Movable:
    def __init__(self, type_id, id, location, movement):
        self.type_id = type_id
        self.id = id
        self.location = location
        self.movement = movement
        MovementHandler(self).start()

    def __hash__(self):
        return hash(self.id)

###############################################################################
# Awareable
#
# Properties
# - memory
# - awareness heuristic
#
# Behaviour:
# - listens to external messages

#class socket_handler(threading.Thread):
#    def __init__(self, state, socket):
#        super().__init__()
#        self.state = state
#        self.socket = socket

#    def restart(self, new_state):
#        self.state = new_state

#    def run(self):
#        while(True):
#            # Receive message
#            message = self.socket.recv(10)
#            # Process message
#            self.state.awareness(message.decode('ascii'))

#class awareness_handler(threading.Thread):
#    def __init__(self, state):
#        super().__init__()
#        self.state = state
#        self.socket_handlers = []

#    def restart(self, new_state):
#        new_state.socket = self.state.socket
#        new_state.client_socket = self.state.client_socket
#        self.state = new_state
#        for socket_handler in self.socket_handlers:
#            socket_handler.restart(self.state)

#    def run(self):
#        while(True):
#            # Establish connection
#            self.client_socket, _ = self.state.socket.accept()

#            if self.state.type_id != 'ship':
#                # Receive message
#                self.socket_handlers.append(socket_handler(self.state, self.client_socket))
#                self.socket_handlers[-1].start()
#            else:
#                time.sleep(1000000)

#class awareable:
#    def no_awareness(message):
#        pass

#    def __init__(self, awareness = no_awareness):
#        self.awareness = awareness

#        # Get port
#        if self.type_id == 'ship':
#            self.port = 10040
#        elif self.type_id == 'submarine':
#            self.port = 10050
#        elif self.type_id == 'probe':
#            self.port = 20000 + int(self.id)

#        if self.port in Simulation.awareness_handlers:
#            Simulation.awareness_handlers[self.port].restart(self)
#        else:
#            # Create a TCP server socket object
#            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#            # Get local machine name
#            self.hostname = socket.gethostname()
#            # TCP bind to hostname on the port.
#            self.socket.bind((self.hostname, self.port))
#            # Queue up to 10 requests
#            self.socket.listen(10)

#            # Create a TCP client socket object
#            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#            # Establish connection
#            self.client_socket.connect((self.hostname, self.port))

#            Simulation.awareness_handlers[self.port] = awareness_handler(self)
#            Simulation.awareness_handlers[self.port].start()


#    def __hash__(self):
#        return hash(self.id)

###############################################################################
# Decidable
#
# Properties
# - strategy heuristic
#
# Behaviour:
# - chooses actions

class StrategyHandler(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        self.state.strategy()

class Decidable:
    def no_strategy():
        pass

    def __init__(self, strategy = no_strategy):
        self.strategy = strategy

    def deploy(self):
        StrategyHandler(self).start()

    def __hash__(self):
        return hash(self.id)

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

#class probe(movable, awareable):
#    def movement(self):
#        pass

#    def awareness(self, request):
#        if request == 'submarine':
#            Simulation.update(self, [['HACKED!!!']])
#        elif request == 'ship':
#            # Send message
#            reply = self.value.encode('ascii')
#            self.owner.client_socket.send(reply)
#        else:
#            # Parse message
#            submarine_location = ast.literal_eval(request)
#            # Calculate measurements
#            distance = math.sqrt(sum((value[0] - value[1])**2 for value in zip(self.location, submarine_location)))
#            if distance <= self.precision:
#                self.value = 'yes'
#                # Update log
#                Simulation.update(self, [[4, self.value]])
#            elif self.value == 'yes':
#                self.value = 'no'
#                # Update log
#                Simulation.update(self, [[4, self.value]])

#    def __init__(self, id, location, owner, cost, precision):
#        self.cost : int = cost
#        self.precision : int = precision
#        self.value : int = 'no'
#        self.owner = owner
#        self.interval = []
#        for value in location:
#            interval_left  = intervals.left_endpoint(value - precision, True, False)
#            interval_right = intervals.right_endpoint(value + precision, True, False)
#            interval_expression = intervals.interval_expression([intervals.interval(interval_left, interval_right)])
#            self.interval.append(interval_expression)
#        csv_content = []
#        csv_content.append('probe')
#        csv_content.append(id)
#        csv_content.append(self.interval)
#        csv_content.append(self.value)

#        # Create log
#        Simulation.put(csv_content)

#        movable.__init__(self, 'probe', id, location, self.movement)
#        awareable.__init__(self, self.awareness)
#        #decidable.__init__(self, self.strategy)

#    def __hash__(self):
#        return movable.__hash__(self)

#class low_probe(probe) :
#    def __init__(self, id, location, owner):
#        super().__init__(id, location, owner, 1, 5)

#    def __hash__(self):
#        return super().__hash__()

#class high_probe(probe) :
#    def __init__(self, id, location, owner):
#        super().__init__(id, location, owner, 10, 3)

#    def __hash__(self):
#        return super().__hash__()

#class perfect_probe(probe) :
#    def __init__(self, id, location, owner):
#        super().__init__(id, location, owner, 0, 0)

#    def __hash__(self):
#        return super().__hash__()

class Process:
    def __init__(self, cost: int, precision: int, location: list):
        self.cost : int = cost
        self.precision : int = precision
        self.location = location
        self.interval = []
        for value in location:
            interval_left  = intervals.LeftEndpoint(value - precision, False, True)
            interval_right = intervals.RightEndpoint(value + precision, False, True)
            interval_expression = intervals.IntervalExpression([intervals.Interval(interval_left, interval_right)])
            self.interval += [interval_expression]

    def synchronous_read(self):
        # Calculate measurements
        submarine_location, submarine_timestamp = Submarine.get_values()
        Submarine.read_flag.set()
        distance = math.sqrt(sum((value[0] - value[1])**2 for value in zip(self.location, submarine_location)))
        reply = str(distance < self.precision)

        return reply

class Measurement:
    def __init__(self, id, location, precision, cost, has_detected_submarine, value: list, is_lying: bool):
        self.id: int = id
        self.location = location
        self.precision = precision
        self.cost = cost
        self.has_detected_submarine = has_detected_submarine
        self.value: list = value
        self.is_lying: bool = is_lying

    def addition(self, uncertainty):
        self.value = list(map(lambda value: value.addition(uncertainty).intersection(Simulation.domain()), self.value))
        return self

    def is_valid(self):
        return all(value != intervals.IntervalExpression.empty() and value != Simulation.domain() for value in self.value)

class Batch:
    def __init__(self, id: int, timestamp: int):
        self.id: int = id
        self.timestamp: int = timestamp
        self.measurements: list = []
        self.type_id = 'batch'
        self.decay = 0

    def update(self, uncertainty):
        self.measurements = list(map(lambda value: value.addition(uncertainty), self.measurements))
        self.measurements = list(filter(lambda value: value.is_valid(), self.measurements))
        self.decay += uncertainty.absolute

###############################################################################
# Alert

class Alert:
    def __init__(self, range, cost, message):
        self.range = range
        self.cost = cost
        self.message = message

    def trigger(self):
        pass

    def __repr__(self):
        return self.range

class RedAlert(Alert):
    def __init__(self):
        interval_left  = intervals.LeftEndpoint(40, False, True)
        interval_right = intervals.RightEndpoint(45, False, True)
        interval_expression = intervals.IntervalExpression([intervals.Interval(interval_left, interval_right)])
        super().__init__([interval_expression], 10, 'RED ALERT!!!')

    def trigger(self):
        Simulation.client_socket.send('win'.encode('utf8'))
        InterfaceHandler.wait()

class YellowAlert(Alert):
    def __init__(self):
        interval_left  = intervals.LeftEndpoint(45, True, False)
        interval_right = intervals.RightEndpoint(70, False, True)
        interval_expression = intervals.IntervalExpression([intervals.Interval(interval_left, interval_right)])
        super().__init__([interval_expression], 5, 'Yellow alert!')


class ShipState():
    def __init__(self, location, timestamp, total_cost, graph, batches, state):
        self.location = location
        self.timestamp = timestamp
        self.total_cost = total_cost
        self.graph = graph
        self.batches = batches
        self.state = state

class AlarmOutput:
    def __init__(self, alert: Alert, state: ShipState):
        self.alert: Alert = alert
        self.state: ShipState = state

class HelicopterOutput:
    def __init__(self, processes: list, state: ShipState):
        self.processes: list = processes
        self.state: ShipState = state

class ClockOutput:
    def __init__(self, decay: int, state: ShipState):
        self.decay: int = decay
        self.state: ShipState = state

class HelicopterInput:
    def __init__(self, state: ShipState):
        self.state: ShipState = state

class ClockInput:
    def __init__(self, state: ShipState):
        self.state: ShipState = state

class Solution:
    def __init__(self, output: list):
        self.output: list = output

class Problem:
    def __init__(self, input: list):
        self.input: list = input

class Formula:
    def __init__(self, function: typing.Callable[[Problem], Solution], parameters: list):
        self.function: typing.Callable[[list], Solution] = function
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
    def no_movement(self):
        pass

    def wait(self, clock_output: ClockOutput) -> ClockInput:
        decay = clock_output.decay
        state = clock_output.state

        # Create log
        # Ship
        result = [Simulation.domain()] * len(state.location)
        for batch in state.batches:
            for measurement in batch.measurements:
                function = lambda value: value[0].intersection(value[1])
                parameters = zip(result, measurement.value)
                result = list(map(function, parameters))
        csv_content = [state.location]
        csv_content += [state.timestamp]
        csv_content += [state.total_cost]
        csv_content += [result]

        # Submarine
        submarine_location, submarine_timestamp = Submarine.get_values()
        csv_content += [submarine_location]
        csv_content += [submarine_timestamp]

        # Graph
        csv_content += [state.graph.save_into_disk_and_get_file_name('../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX')]

        # Probes
        for batch in state.batches:
            for measurement in batch.measurements:
                csv_content += [measurement.id]
                csv_content += [batch.id]
                csv_content += [batch.timestamp]
                csv_content += [measurement.location]
                csv_content += [measurement.precision]
                csv_content += [batch.decay]
                csv_content += [measurement.cost]
                csv_content += [measurement.has_detected_submarine]
                csv_content += [measurement.value]
        Simulation.put(csv_content)
        InterfaceHandler.wait()
        state.timestamp += 1

        # Create log
        empty_batches = []
        for batch in state.batches:
            batch.update(intervals.AbsoluteUncertainty(0, decay))
            if len(batch.measurements) == 0:
                empty_batches += [batch]
        for batch in empty_batches:
            state.batches.remove(batch)

        # Generate result
        result = [Simulation.domain()] * len(state.location)
        for batch in state.batches:
            for measurement in batch.measurements:
                function = lambda value: value[0].intersection(value[1])
                parameters = zip(result, measurement.value)
                result = list(map(function, parameters))
        function = lambda value: value.intervals
        dimensions = list(map(function, result))

        function = lambda value: [value]
        targets = list(map(function, dimensions[0]))
        function = lambda value: value[0] + [value[1]] 
        for dimension in dimensions[1:]:
            targets = list(map(function, zip(targets, dimension)))

        for target in targets:
            sources = []
            for source in state.state:
                if all(value[0].contains(value[1]) for value in zip(target, source)):
                    sources += [source]

            print("sources " + str(sources))
            print("target " + str([target]))

            # Update graph
            state.graph += graphs.Hyperedge(
                sources = sources,
                targets = [target],
                weight = 0,
                label = 't' + str(state.timestamp)
            )

        state.state = targets

        input = ClockInput(state)
        return input

    def try_alert(self, alarm_output: AlarmOutput):
        alert = alarm_output.alert
        state = alarm_output.state

        result = [Simulation.domain()] * len(state.location)
        for batch in state.batches:
            for measurement in batch.measurements:
                function = lambda value: value[0].intersection(value[1])
                parameters = zip(result, measurement.value)
                result = list(map(function, parameters))

        if all(zip_value[0].contains(zip_value[1]) for zip_value in zip(alert.range, result)):
            state.total_cost = alert.cost

            alert.trigger()

    def get_fresh_measurements(self, helicopter_output: HelicopterOutput) -> HelicopterInput:
        processes = helicopter_output.processes
        state = helicopter_output.state

        # Heuristic Ephemeral Interval Byzantine Register
        batch_id = len(state.batches) + 1
        batch_timestamp = state.timestamp
        batch = Batch(batch_id, batch_timestamp)

        cost = 0
        for probe in processes:
            cost += probe.cost

            reply = probe.synchronous_read()
            if reply == 'True':
                measurement = Measurement(self.probe_counter, probe.location, probe.precision, probe.cost, reply, probe.interval, False)
            else:
                measurement = Measurement(self.probe_counter, probe.location, probe.precision, probe.cost, reply, list(map(lambda value: value.negation().intersection(Simulation.domain()), probe.interval)), False)

            batch.measurements += [measurement]
            self.probe_counter += 1

        state.batches += [batch]
        state.total_cost += cost

        # Generate result
        result = [Simulation.domain()] * len(state.location)
        for batch in state.batches:
            for measurement in batch.measurements:
                function = lambda value: value[0].intersection(value[1])
                parameters = zip(result, measurement.value)
                result = list(map(function, parameters))
        function = lambda value: value.intervals
        dimensions = list(map(function, result))

        function = lambda value: [value]
        targets = list(map(function, dimensions[0]))
        function = lambda value: value[0] + [value[1]] 
        for dimension in dimensions[1:]:
            targets = list(map(function, zip(targets, dimension)))

        print("sources " + str([state.state]))
        for source in state.state:
            sub_targets = []
            for target in targets:
                if all(value[0].contains(value[1]) for value in zip(source, target)):
                    sub_targets += [target]

            print("source " + str([source]))
            print("targets " + str(targets))

            # Update graph
            state.graph += graphs.Hyperedge(
                sources = [source],
                targets = sub_targets,
                weight = cost,
                label = 'b' + str(batch.id)
            )

        state.state = targets

        input = HelicopterInput(state)
        return input

    #def awareness(self, message):
    #    pass

    # Problem solving search algorithm
    def strategy(self):
        def search(parameters: list) -> Solution:
            processes = []
            for n in range(1, random.randint(3, 4)):
                processes += [Process(10, 3, [random.randint(0 + 3, 100 - 3)])]

            output = [AlarmOutput(parameters[1], parameters[0])]
            output += [ClockOutput(parameters[2], parameters[0])]
            output += [HelicopterOutput(processes, parameters[0])]

            solution = Solution(output)

            return solution

        def formulate(problem: Problem) -> Formula:
            for input in problem.input:
                if type(input) == HelicopterInput:
                    state = input.state
                elif type(input) == ClockInput:
                    state = input.state

            parameters = [state]
            parameters += [RedAlert()]
            parameters += [1]

            formula = Formula(search, parameters)
            return formula

        def apply(formula: Formula) -> Solution:
            return formula.function(formula.parameters)

        def execute(solution: Solution) -> Problem:
            input = []
            for output in solution.output:
                if type(output) == AlarmOutput:
                    self.try_alert(output)
                elif type(output) == HelicopterOutput:
                    if len(input) > 0 and (type(input[-1]) == ClockInput or type(input[-1]) == HelicopterOutput):
                        output.state = input[-1].state
                        input[-1] = self.get_fresh_measurements(output)
                    else:
                        input += [self.get_fresh_measurements(output)]
                elif type(output) == ClockOutput:
                    if len(input) > 0 and (type(input[-1]) == ClockInput or type(input[-1]) == HelicopterOutput):
                        output.state = input[-1].state
                        input[-1] = [self.wait(output)]
                    else:
                        input += [self.wait(output)]
            problem = Problem(input)

            return problem

        # Problem Solving Search Algorithm
        graph = graphs.Graph(
            node = graphs.Node(Simulation.domain().intervals * len(self.location))
        )

        initial_state = ShipState(
            location = self.location,
            timestamp = 0,
            total_cost = 0,
            graph = graph,
            batches = [],
            state = [Simulation.domain().intervals * len(self.location)]
        )
        input = [ClockInput(initial_state)]
        problem = Problem(input)
        while True:
            formula = formulate(problem)
            solution = apply(formula)
            problem = execute(solution)

    def __init__(self, location):
        self.probe_counter = 1

        Movable.__init__(self, 'ship', 'ship', location, self.no_movement)
        #awareable.__init__(self, self.awareness)
        Decidable.__init__(self, self.strategy)

    def __hash__(self):
        return Movable.__hash__(self)

    def __hash__(self):
        return super().__hash__()

class Submarine(Movable, Decidable):
    #lock = threading.Lock()
    def get_values():
        Submarine.read_flag.wait()
        Submarine.read_flag.clear()
        return Submarine.location, Submarine.timestamp

    def move_to_submarine(self):
        velocity = list(map(lambda value: -value, Submarine.location))
        norm = math.sqrt(sum(value**2 for value in velocity))
        if norm == 0:
            Simulation.client_socket.send('lose'.encode('utf8'))
            InterfaceHandler.wait()

        normalized_vector = list(map(lambda value: value / norm, velocity))

        Submarine.location = list(map(lambda value: value[0] + value[1], zip(Submarine.location, normalized_vector)))
        Submarine.timestamp += 1
        Submarine.read_flag.set()

        #request = str(self.location).encode('ascii')
        #for client in Simulation.probes:
        #    client.client_socket.send(request)

    #def awareness(self, message):
    #    pass

    def hack_random_probe(self):
        pass

        #random_probe_socket = random.choice(list(Simulation.probes)).client_socket

        #random_probe_socket.send(self.type_id.encode('ascii'))

    def __init__(self, location):
        Submarine.read_flag = threading.Event()

        Submarine.location = location
        Submarine.timestamp = 0
        Submarine.read_flag.set()
        #Submarine.speed = 0

        Movable.__init__(self, 'submarine', 'submarine', location, self.move_to_submarine)
        #awareable.__init__(self, self.awareness)
        Decidable.__init__(self, self.hack_random_probe)

    def __hash__(self):
        return super().__hash__()

#graphs.test()
#intervals.test()
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