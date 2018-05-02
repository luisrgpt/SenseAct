import ast
import asyncio
import atexit
import csv
import functools
import intervals
import math
import os
import queue
import random
import socket
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
        InterfaceHandler.is_waiting = False

    def run(self):
        while True:
            try:
                message = self.client_socket.recv(10)
            except:
                os._exit(1)
            else:
                code = message.decode('utf8')
                if code == "quit":
                    os._exit(1)
                elif code == "pause":
                    InterfaceHandler.is_waiting = True
                elif code == "play":
                    InterfaceHandler.is_waiting = False
                elif code == "stop":
                    InterfaceHandler.reset_condition_is_not_satisfied = False
                    InterfaceHandler.is_waiting = True
                elif code == "repeat_all":
                    InterfaceHandler.reset_condition_is_not_satisfied = False
                    InterfaceHandler.is_waiting = False

class Simulation:
    log_prefix = './log/'
    log_suffix = '.csv'
    frame_per_second = 1

    def wait(frames):
        while InterfaceHandler.is_waiting:
            time.sleep(1 / Simulation.frame_per_second)
        time.sleep(frames / Simulation.frame_per_second)

    def restart():
        with Simulation.lock:
            Simulation.client_socket.send('reset'.encode('utf8'))
            Simulation.stack = []

            Simulation.dictionary = {}

            Simulation.log_file_name = Simulation.log_prefix + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + Simulation.log_suffix
            if not os.path.exists(Simulation.log_prefix):
                os.makedirs(Simulation.log_prefix)

            Simulation.wait(1)

            Simulation.agents = []
            Simulation.probes = []

            Simulation.win_condition_is_not_satisfied = True
            Simulation.lose_condition_is_not_satisfied = True
            InterfaceHandler.reset_condition_is_not_satisfied = True

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
        csv_content = list(map(lambda value:  str(value), csv_content))

        csv_content.insert(0, time.strftime('%Y_%m_%d_%H_%M_%S'))
        if csv_content[1] == 'batch':
            index = csv_content[1] + '_' + csv_content[2]
        else:
            index = csv_content[1]

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
        while Simulation.win_condition_is_not_satisfied \
          and Simulation.lose_condition_is_not_satisfied \
          and InterfaceHandler.reset_condition_is_not_satisfied:
            self.state.movement()
            Simulation.wait(1)

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
        distance = math.sqrt(sum((value[0] - value[1])**2 for value in zip(self.location, Submarine.location)))
        reply = str(distance <= self.precision)

        return reply

class Measurement:
    def __init__(self, value: list, is_lying: bool):
        self.value: list = value
        self.is_lying: bool = is_lying

    def __repr__(self):
        return str(self.value) + ('_LYING' if self.is_lying else '')  

    def addition(self, uncertainty):
        self.value = list(map(lambda value: value.addition(uncertainty).intersection(Simulation.domain()), self.value))
        return self

    def is_valid(self):
        return all(value != intervals.IntervalExpression.empty() and value != Simulation.domain() for value in self.value)

class Batch:
    def __init__(self, timestamp: int):
        self.timestamp: int = timestamp
        self.measurements: list = []
        self.type_id = 'batch'

        # Create log
        csv_content  = [self.type_id]
        csv_content += [self.timestamp]
        csv_content += self.measurements
        Simulation.put(csv_content)

    def __repr__(self):
        csv_content  = self.type_id + ","
        csv_content += str(self.timestamp) + ","
        csv_content += str(self.measurements)
        return csv_content

    def update(self, uncertainty):
        self.measurements = list(map(lambda value: value.addition(uncertainty), self.measurements))
        self.measurements = list(filter(lambda value: value.is_valid(), self.measurements))

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
        Simulation.win_condition_is_not_satisfied = False

class YellowAlert(Alert):
    def __init__(self):
        interval_left  = intervals.LeftEndpoint(45, True, False)
        interval_right = intervals.RightEndpoint(70, False, True)
        interval_expression = intervals.IntervalExpression([intervals.Interval(interval_left, interval_right)])
        super().__init__([interval_expression], 5, 'Yellow alert!')




class AlarmOutput:
    def __init__(self, alert: Alert, result: list):
        self.alert: Alert = alert
        self.result: list = result

class HelicopterOutput:
    def __init__(self, processes: list, timestamp: int):
        self.processes: list = processes
        self.timestamp: int = timestamp

class ClockOutput:
    def __init__(self, result: list, timestamp: int, frame: int, decay: int):
        self.result: list = result
        self.timestamp: int = timestamp
        self.frame: int = frame
        self.decay: int = decay

class Memory:
    def __init__(self, total_cost: int):
        self.total_cost: int = total_cost

class HelicopterInput:
    def __init__(self, batch: Batch, cost: int):
        self.batch: Batch = batch
        self.cost: int = cost

class ClockInput:
    def __init__(self, decayed_result: list, incremented_timestamp: int):
        self.decayed_result: list = decayed_result
        self.incremented_timestamp: int = incremented_timestamp

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

    def wait(self, timestamp, result, frame, decay):
        Simulation.wait(frame)
        timestamp += frame
        result = list(map(lambda value: value.addition(intervals.AbsoluteUncertainty(0, decay)).intersection(Simulation.domain()), result))

        # Create log
        for batch in self.batches:
            batch.update(intervals.AbsoluteUncertainty(0, decay))
            csv_content  = [batch.type_id]
            csv_content += [batch.timestamp]
            csv_content += batch.measurements
            Simulation.put(csv_content)

        input = ClockInput(result, timestamp)
        return input

    def try_alert(self, alert, value):
        if all(zip_value[0].contains(zip_value[1]) for zip_value in zip(alert.range, value)):
            cost = alert.cost

            # Create log
            self.total_cost += cost
            csv_content = [self.type_id]
            csv_content += [self.location]
            csv_content += [self.total_cost]
            csv_content += [self.result]
            csv_content += self.alerts
            csv_content += [alert.message]
            Simulation.put(csv_content)

            alert.trigger()

    def get_fresh_measurements(self, processes, timestamp):
        # Heuristic Ephemeral Interval Byzantine Register
        batch = Batch(timestamp)
        cost = 0
        for probe in processes:
            cost += probe.cost

            reply = probe.synchronous_read()
            if reply == 'True':
                measurement = Measurement(probe.interval, False)
            else:
                measurement = Measurement(list(map(lambda value: value.negation().intersection(Simulation.domain()), probe.interval)), False)
            batch.measurements += [measurement]

        self.batches += [batch]
        csv_content  = [batch.type_id]
        csv_content += [batch.timestamp]
        csv_content += batch.measurements
        Simulation.put(csv_content)

        # Create log
        self.total_cost += cost
        csv_content = [self.type_id]
        csv_content += [self.location]
        csv_content += [self.total_cost]
        csv_content += [self.result]
        csv_content += self.alerts
        Simulation.put(csv_content)

        input = HelicopterInput(batch, cost)
        return input

    #def awareness(self, message):
    #    pass

    # Problem solving search algorithm
    def strategy(self):
        def search(parameters: list) -> Solution:
            processes = []
            for n in range(1, random.randint(3, 4)):
                processes += [Process(10, 3, [random.randint(0 + 3, 100 - 3)])]

            output = [AlarmOutput(parameters[0], parameters[1])]
            output += [HelicopterOutput(processes, parameters[2])]
            output += [ClockOutput(parameters[1], parameters[2], parameters[3], parameters[4])]
            output += [Memory(parameters[5])]

            solution = Solution(output)

            return solution

        def formulate(problem: Problem) -> Formula:
            batch = None
            for input in problem.input:
                if type(input) == HelicopterInput:
                    batch = input.batch
                    cost = input.cost
                elif type(input) == ClockInput:
                    result = input.decayed_result
                    timestamp = input.incremented_timestamp
                elif type(input) == Memory:
                    total_cost = input.total_cost

            if batch is not None:
                total_cost += cost

                #if len(batch.measurements) > 0:
                #    print(batch.measurements)
                for measurement in batch.measurements:
                    function = lambda value: value[0].intersection(value[1])
                    parameters = zip(result, measurement.value)
                    intersection = list(map(function, parameters))

                    #print(str(result) + " and " + str(measurement.value) + " <=> " + str(intersection))
                    #if all(value == intervals.IntervalExpression.empty() for value in result) \
                    #or all(value == intervals.IntervalExpression.empty() for value in measurement.value) \
                    #or all(value == intervals.IntervalExpression.empty() for value in intersection):
                    #    InterfaceHandler.is_waiting = True
                    #    time.sleep(10000)

                    result = intersection

                #if len(batch.measurements) > 0:
                #    print("")
                #    print("")
                #    print("")
                #    print("")
                #    print("")

            # Create log
            self.result = result
            csv_content = [self.type_id]
            csv_content += [self.location]
            csv_content += [self.total_cost]
            csv_content += [self.result]
            csv_content += self.alerts
            Simulation.put(csv_content)

            with Submarine.lock:
                max_speed = Submarine.speed
                Submarine.speed = 0

            parameters = [RedAlert()]
            parameters += [result]
            parameters += [timestamp]
            parameters += [1]
            parameters += [max_speed]
            parameters += [total_cost]

            formula = Formula(search, parameters)
            return formula

        def apply(formula: Formula) -> Solution:
            return formula.function(formula.parameters)

        def execute(solution: Solution) -> Problem:
            input = []
            for output in solution.output:
                if type(output) == AlarmOutput:
                    self.try_alert(output.alert, output.result)
                elif type(output) == HelicopterOutput:
                    input += [self.get_fresh_measurements(output.processes, output.timestamp)]
                elif type(output) == ClockOutput:
                    input += [self.wait(output.timestamp, output.result, output.frame, output.decay)]
                elif type(output) == Memory:
                    input += [output]
            problem = Problem(input)

            return problem

        # Problem Solving Search Algorithm
        input = [ClockInput([Simulation.domain()] * len(self.location), 0)]
        input += [Memory(0)]
        problem = Problem(input)
        while Simulation.win_condition_is_not_satisfied \
          and Simulation.lose_condition_is_not_satisfied \
          and InterfaceHandler.reset_condition_is_not_satisfied:
            formula = formulate(problem)
            solution = apply(formula)
            problem = execute(solution)

    def __init__(self, location):
        self.total_cost = 0
        self.result = [Simulation.domain()] * len(location)
        self.alerts = []
        self.probes = []
        self.batches = []

        Movable.__init__(self, 'ship', 'ship', location, self.no_movement)
        #awareable.__init__(self, self.awareness)
        Decidable.__init__(self, self.strategy)

        # Create log
        csv_content = [self.type_id]
        csv_content += [self.location]
        csv_content += [self.total_cost]
        csv_content += [self.result]
        csv_content += self.alerts
        Simulation.put(csv_content)

    def __hash__(self):
        return Movable.__hash__(self)

    def __hash__(self):
        return super().__hash__()

class Submarine(Movable, Decidable):
    location = None
    lock = threading.Lock()

    def move_to_submarine(self):
        velocity = list(map(lambda value: -value, Submarine.location))
        norm = math.sqrt(sum(value**2 for value in velocity))
        if norm == 0:
            Simulation.lose_condition_is_not_satisfied = False
            return
        normalized_vector = list(map(lambda value: value / norm, velocity))
        Submarine.location = list(map(lambda value: value[0] + value[1], zip(Submarine.location, normalized_vector)))

        with Submarine.lock:
            Submarine.speed += 1
        #request = str(self.location).encode('ascii')
        #for client in Simulation.probes:
        #    client.client_socket.send(request)

        # Create log
        csv_content = [self.type_id]
        csv_content += [Submarine.location]
        Simulation.put(csv_content)

    #def awareness(self, message):
    #    pass

    def hack_random_probe(self):
        pass

        #random_probe_socket = random.choice(list(Simulation.probes)).client_socket
        
        #random_probe_socket.send(self.type_id.encode('ascii'))

    def __init__(self, location):
        Submarine.location = location
        Submarine.speed = 0

        Movable.__init__(self, 'submarine', 'submarine', location, self.move_to_submarine)
        #awareable.__init__(self, self.awareness)
        Decidable.__init__(self, self.hack_random_probe)

        # Create log
        csv_content = [self.type_id]
        csv_content += [Submarine.location]
        Simulation.put(csv_content)

    def __hash__(self):
        return super().__hash__()

#intervals.test()
Simulation.start()
while(True):
    Simulation.agents.append(Ship([0]))
    Simulation.agents.append(Submarine([random.randint(0, 100)]))

    for machine in Simulation.agents:
        machine.deploy()

    while Simulation.win_condition_is_not_satisfied \
      and Simulation.lose_condition_is_not_satisfied \
      and InterfaceHandler.reset_condition_is_not_satisfied:
        Simulation.wait(1)
    Simulation.restart()