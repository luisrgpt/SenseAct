import ast
import asyncio
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

###############################################################################
# World
#
# Properties:
# - list of locations
#

class Simulation:
    log_prefix = './log/'
    log_suffix = '.csv'
    frame_per_second = 1

    def restart():
        Simulation.lock.acquire()
        Simulation.client_socket.send(''.encode('utf8'))
        Simulation.stack = []

        Simulation.dictionary = {}

        Simulation.log_file_name = Simulation.log_prefix + str(time.strftime('%Y_%m_%d_%H_%M_%S')) + Simulation.log_suffix
        if not os.path.exists(Simulation.log_prefix):
            os.makedirs(Simulation.log_prefix)

        time.sleep(1 / Simulation.frame_per_second)

        Simulation.agents = []
        Simulation.probes = []

        Simulation.lose_condition_is_not_satisfied = True
        Simulation.win_condition_is_not_satisfied = True

        if Simulation.log_file is not None:
            Simulation.log_file.close()
        Simulation.log_file = open(Simulation.log_file_name, 'a+', newline='')
        Simulation.log_writer = csv.writer(Simulation.log_file)

        Simulation.lock.release()

    def start():
        Simulation.lock = threading.Lock()
        Simulation.log_file = None

        hostname = socket.gethostname()
        port = 3000
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((hostname, port))
        server_socket.listen(1)
        Simulation.client_socket, _ = server_socket.accept()

        Simulation.restart()

        Simulation.awareness_handlers = {}

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

        Simulation.lock.acquire()
        Simulation.client_socket.send(message)
        Simulation.log_writer.writerow(csv_content)
        Simulation.dictionary[index] = csv_content.copy()
        Simulation.lock.release()

    def update(key, csv_changes = []):
        csv_content = list(map(lambda value:  (value[0], str(value[1])) if len(value) == 2 else str(value[0]), csv_changes))

        csv_changes.append((0, time.strftime('%Y_%m_%d_%H_%M_%S')))

        if key.type_id == 'batch':
            index = key.type_id + '_' + str(key.timestamp)
        else:
            index = key.type_id

        if not index in Simulation.dictionary:
            return

        Simulation.lock.acquire()
        csv_content = Simulation.dictionary[index]

        for csv_change in csv_changes:
            if len(csv_change) == 1:
                csv_content.append(csv_change[0])
            elif len(csv_change) == 2:
                csv_content[csv_change[0]] = csv_change[1]

        stream = csv.StringIO()
        writer = csv.writer(stream)
        writer.writerow(csv_content)
        stream_value = stream.getvalue()
        message = stream_value.encode('utf8')
        Simulation.client_socket.send(message)
        Simulation.log_writer.writerow(csv_content)

        Simulation.dictionary[index] = csv_content.copy()
        Simulation.lock.release()

    def take_all(Simulation):
        Simulation.lock.acquire()
        log_content = Simulation.stack.copy()
        Simulation.stack = []
        Simulation.lock.release()

        return log_content

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
        while Simulation.win_condition_is_not_satisfied and Simulation.lose_condition_is_not_satisfied:
            self.state.movement()
            time.sleep(1 / Simulation.frame_per_second)

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
            interval_left  = intervals.LeftEndpoint(value - precision, True, False)
            interval_right = intervals.RightEndpoint(value + precision, True, False)
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

class Batch:
    def __init__(self, timestamp: int):
        self.timestamp: int = timestamp
        self.measurements: list = []
        self.type_id = 'batch'

        # Create log
        csv_content = []
        csv_content.append('batch')
        csv_content.append(self.timestamp)
        Simulation.put(csv_content)

    def add(self, measurement: Measurement):
        self.measurements.append(measurement)

        # Update log
        Simulation.update(self, [[measurement]])

    def update(self):
        result_measurements = []
        for index, measurement in enumerate(self.measurements):
            result_value = []
            for interval in measurement.value:
                result_value += [interval.addition(intervals.AbsoluteUncertainty(0, 1)).intersection(Simulation.domain())]
            result_measurement = Measurement(result_value, measurement.is_lying)
            result_measurements += [result_measurement]

            # Update log
            Simulation.update(self, [[3 + index, result_measurement]])

        self.measurements = result_measurements


###############################################################################
# Alert

class Alert:
    def __init__(self, range, cost, message):
        self.range = range
        self.cost = cost
        self.message = message

    def trigger(self):
        pass

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

    def create_alert(self, alert):
        self.alerts.append(alert)
        Simulation.update(self, [[3, self.balance], [alert.range]])
        return self

    def create_probe(self, probe):
        self.balance -= probe.cost
        Simulation.probes.append(probe)
        return self

    def create_perfect_probe(self, location):
        return self.create_probe(perfect_probe(len(Simulation.probes), location, self))

    def create_high_probe(self, location):
        return self.create_probe(high_probe(len(Simulation.probes), location, self))

    def create_low_probe(self, location):
        return self.create_probe(low_probe(len(Simulation.probes), location, self))

    def wait(frames):
        time.sleep(frames / Simulation.frame_per_second)

    def try_alert(self, alert, value):
        if all(zip_value[0].contains(zip_value[1]) for zip_value in zip(alert.range, value)):
            self.balance -= alert.cost
            Simulation.update(self, [[3, self.balance], [alert.message]])
            alert.trigger()

        return None

    def synchronous_reply_from_ephemeral_deployment(self, processes: list) -> Batch:
        batch = Batch(self.timestamp)
        for probe in processes:
            self.balance -= probe.cost
            Simulation.update(self, [[3, self.balance]])

            reply = probe.synchronous_read()
            if reply == 'True':
                measurement = Measurement(probe.interval, False)
            else:
                measurement = Measurement(list(map(lambda value: value.negation().intersection(Simulation.domain()), probe.interval)), False)
            batch.add(measurement)

        return batch

    def interval_byzantine_verification(self, batch: Batch) -> Batch:
        return batch

    def get_fresh_measurements(self, processes):
        # Heuristic Ephemeral Interval Byzantine Register
        batch = self.synchronous_reply_from_ephemeral_deployment(processes)
        verified_batch = self.interval_byzantine_verification(batch)

        return batch

    #def awareness(self, message):
    #    pass

    # Problem solving search algorithm
    def strategy(self):
        self.timestamp = 0

        class Problem:
            def __init__(self, heuristic = None, seed: list = []):
                self.heuristic = heuristic
                self.seed: list = seed

        class Formula:
            def __init__(self, processes: list, heuristic, seed: list = []):
                self.processes: list = processes
                self.heuristic = heuristic
                self.seed: list = seed

        class Solution:
            def __init__(self, actions: list, heuristic, seed: list = []):
                self.actions: list = actions
                self.heuristic = heuristic
                self.seed: list = seed

        def formulate(problem: Problem) -> Formula:
            if problem is None:
                return None

            processes = []
            for n in range(1, random.randint(3, 4)):
                processes += [Process(10, 3, [random.randint(0 + 3, 100 - 3)])]

            formula = Formula(processes, problem.heuristic, problem.seed)
            return formula

        def apply(formula: Formula) -> Solution:
            if formula is None:
                return None
            
            interval_expressions = [Simulation.domain()] * len(Submarine.location)
            for batch in formula.seed:
                if batch.timestamp < self.timestamp:
                    batch.update()

                for measurement in batch.measurements:
                    for index, interval_expression in enumerate(interval_expressions):
                        interval_expressions[index] = interval_expression.intersection(measurement.value[index])

            Simulation.update(self, [[4, interval_expressions]])
            
            actions = []
            if len(formula.seed) > 0 and self.balance >= RedAlert().cost:
                actions += [functools.partial(self.try_alert, RedAlert(), interval_expressions)]

            actions += [functools.partial(self.get_fresh_measurements, formula.processes)]

            solution = Solution(actions, formula.heuristic)

            return solution

        def execute(solution: Solution) -> Problem:
            if solution is None:
                time.sleep(1 / Simulation.frame_per_second)
                return None
            
            self.timestamp += 1
            seed = solution.seed
            for action in solution.actions:
                result = action()
                if result is not None:
                    seed += [result]
            time.sleep(1 / Simulation.frame_per_second)

            problem = Problem(solution.heuristic, seed)
            return problem

        # Problem Solving Search Algorithm
        problem = Problem()
        while Simulation.win_condition_is_not_satisfied and Simulation.lose_condition_is_not_satisfied:
            search_formula = formulate(problem)
            #print('problem: ' + str(problem.seed))
            solution = apply(search_formula)
            #print('formula: ' + str(search_formula.seed))
            problem = execute(solution)
            #print('solutio: ' + str(solution.heuristic))

    def __init__(self, location, balance):
        self.balance = balance
        self.value = []
        for value in location:
            self.value.append(Simulation.domain())
        self.alerts = []
        self.probes = []
        csv_content = []
        csv_content.append('ship')
        csv_content.append(location)
        csv_content.append(self.balance)
        csv_content.append(self.value)

        # Create log
        Simulation.put(csv_content)

        Movable.__init__(self, 'ship', 'ship', location, self.no_movement)
        #awareable.__init__(self, self.awareness)
        Decidable.__init__(self, self.strategy)

    def __hash__(self):
        return Movable.__hash__(self)

    def __hash__(self):
        return super().__hash__()

class Submarine(Movable, Decidable):
    location = None

    def move_to_submarine(self):
        velocity = list(map(lambda value: -value, Submarine.location))
        norm = math.sqrt(sum(value**2 for value in velocity))
        if norm == 0:
            Simulation.lose_condition_is_not_satisfied = False
            return
        normalized_vector = list(map(lambda value: value / norm, velocity))
        Submarine.location = list(map(lambda value: value[0] + value[1], zip(Submarine.location, normalized_vector)))

        #request = str(self.location).encode('ascii')
        #for client in Simulation.probes:
        #    client.client_socket.send(request)

        Simulation.update(self, [[2, Submarine.location]])

    #def awareness(self, message):
    #    pass

    def hack_random_probe(self):
        time.sleep(5)

        #random_probe_socket = random.choice(list(Simulation.probes)).client_socket
        
        #random_probe_socket.send(self.type_id.encode('ascii'))

    def __init__(self, location):
        Submarine.location = location
        csv_content = []
        csv_content.append('submarine')
        csv_content.append(location)

        # Create log
        Simulation.put(csv_content)

        Movable.__init__(self, 'submarine', 'submarine', location, self.move_to_submarine)
        #awareable.__init__(self, self.awareness)
        Decidable.__init__(self, self.hack_random_probe)

    def __hash__(self):
        return super().__hash__()

#intervals.test()
Simulation.start()
while(True):
    Simulation.agents.append(Ship([0], 5000))
    Simulation.agents.append(Submarine([random.randint(0, 100)]))

    for machine in Simulation.agents:
        machine.deploy()

    while Simulation.win_condition_is_not_satisfied and Simulation.lose_condition_is_not_satisfied:
        time.sleep(1 / Simulation.frame_per_second)
    Simulation.restart()