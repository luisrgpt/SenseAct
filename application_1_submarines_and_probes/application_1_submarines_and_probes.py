#!/usr/bin/python3

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

class simulation_handler(threading.Thread):
    csv_prefix = "../user_interface_1_wpf/bin/x86/Debug/AppX/"
    csv_suffix = "_current.csv"
    log_suffix = "_log.csv"
    frame_per_second = 1

    def restart(self):
        self.lock.acquire()
        self.stack = []

        self.dictionary = {}

        self.log_file_name = simulation_handler.csv_prefix + str(time.strftime("%Y_%m_%d_%H_%M_%S")) + simulation_handler.log_suffix

        files = [ file for file in os.listdir(simulation_handler.csv_prefix) if file.endswith(simulation_handler.csv_suffix) ]
        for file in files:
            os.remove(os.path.join(simulation_handler.csv_prefix, file))

        time.sleep(1 / simulation_handler.frame_per_second)

        self.agents = []
        self.probes = []

        self.lose_condition_is_not_satisfied = True
        self.win_condition_is_not_satisfied = True
        self.lock.release()

    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.restart()

        self.awareness_handlers = {}

    def put(self, csv_content):
        csv_content = list(map(lambda value:  str(value), csv_content))

        csv_content.insert(0, time.strftime("%Y_%m_%d_%H_%M_%S"))
        if csv_content[1] == "probe":
            index = csv_content[1] + "_" + csv_content[2]
        else:
            index = csv_content[1]

        self.lock.acquire()
        self.stack.append(csv_content.copy())
        self.dictionary[index] = csv_content.copy()
        self.lock.release()

    def update(self, submarine_or_probe, csv_changes = []):
        csv_content = list(map(lambda value:  (value[0], str(value[1])) if len(value) == 2 else str(value[0]), csv_changes))

        csv_changes.append((0, time.strftime("%Y_%m_%d_%H_%M_%S")))

        if submarine_or_probe.type_id == "probe":
            index = submarine_or_probe.type_id + "_" + str(submarine_or_probe.id)
        else:
            index = submarine_or_probe.type_id

        if not index in self.dictionary:
            return

        self.lock.acquire()
        csv_content = self.dictionary[index]
        
        for csv_change in csv_changes:
            if len(csv_change) == 1:
                csv_content.append(csv_change[0])
            elif len(csv_change) == 2:
                csv_content[csv_change[0]] = csv_change[1]

        self.stack.append(csv_content.copy())
        self.dictionary[index] = csv_content.copy()
        self.lock.release()

    def take_all(self):
        self.lock.acquire()
        log_content = self.stack.copy()
        self.stack = []

        csv_content = self.dictionary.copy()
        self.lock.release()

        return csv_content, log_content

    def run(self):
        while(True):
            csv_content, log_content = self.take_all()

            with open(self.log_file_name, "a+", newline="") as log_file:
                log_writer = csv.writer(log_file)
                for log_row in log_content:
                    log_writer.writerow(log_row)

            for csv_id, csv_row in csv_content.items():
                with open(simulation_handler.csv_prefix + csv_id + simulation_handler.csv_suffix, "w+", newline="") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(csv_row)

            time.sleep(1 / simulation_handler.frame_per_second)

simulation = simulation_handler()

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

class movement_handler(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        while simulation.win_condition_is_not_satisfied and simulation.lose_condition_is_not_satisfied:
            self.state.movement()
            time.sleep(1 / simulation_handler.frame_per_second)

class movable:
    def __init__(self, type_id, id, location, movement):
        self.type_id = type_id
        self.id = id
        self.location = location
        self.movement = movement
        movement_handler(self).start()

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
#            self.state.awareness(message.decode("ascii"))

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

#            if self.state.type_id != "ship":
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
#        if self.type_id == "ship":
#            self.port = 10040
#        elif self.type_id == "submarine":
#            self.port = 10050
#        elif self.type_id == "probe":
#            self.port = 20000 + int(self.id)

#        if self.port in simulation.awareness_handlers:
#            simulation.awareness_handlers[self.port].restart(self)
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

#            simulation.awareness_handlers[self.port] = awareness_handler(self)
#            simulation.awareness_handlers[self.port].start()


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

class strategy_handler(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        self.state.strategy()

class decidable:
    def no_strategy():
        pass

    def __init__(self, strategy = no_strategy):
        self.strategy = strategy

    def deploy(self):
        strategy_handler(self).start()

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
#        if request == "submarine":
#            simulation.update(self, [["HACKED!!!"]])
#        elif request == "ship":
#            # Send message
#            reply = self.value.encode("ascii")
#            self.owner.client_socket.send(reply)
#        else:
#            # Parse message
#            submarine_location = ast.literal_eval(request)
#            # Calculate measurements
#            distance = math.sqrt(sum((value[0] - value[1])**2 for value in zip(self.location, submarine_location)))
#            if distance <= self.precision:
#                self.value = "yes"
#                # Update log
#                simulation.update(self, [[4, self.value]])
#            elif self.value == "yes":
#                self.value = "no"
#                # Update log
#                simulation.update(self, [[4, self.value]])

#    def __init__(self, id, location, owner, cost, precision):
#        self.cost : int = cost
#        self.precision : int = precision
#        self.value : int = "no"
#        self.owner = owner
#        self.interval = []
#        for value in location:
#            interval_left  = intervals.left_endpoint(value - precision, True, False)
#            interval_right = intervals.right_endpoint(value + precision, True, False)
#            interval_expression = intervals.interval_expression([intervals.interval(interval_left, interval_right)])
#            self.interval.append(interval_expression)
#        csv_content = []
#        csv_content.append("probe")
#        csv_content.append(id)
#        csv_content.append(self.interval)
#        csv_content.append(self.value)

#        # Create log
#        simulation.put(csv_content)

#        movable.__init__(self, "probe", id, location, self.movement)
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

class process:
    def __init__(self, cost: int, precision: int, id: int, location: list):
        self.cost : int = cost
        self.precision : int = precision
        self.id : int = id
        self.location = location
        self.interval = []
        for value in location:
            interval_left  = intervals.left_endpoint(value - precision, True, False)
            interval_right = intervals.right_endpoint(value + precision, True, False)
            interval_expression = intervals.interval_expression([intervals.interval(interval_left, interval_right)])
            self.interval += [interval_expression]

    def synchronous_read(self):
        # Calculate measurements
        distance = math.sqrt(sum((value[0] - value[1])**2 for value in zip(self.location, submarine.location)))
        reply = str(distance <= self.precision)

        # Create log
        csv_content = []
        csv_content.append("probe")
        csv_content.append(self.id)
        csv_content.append(self.interval)
        csv_content.append(reply)
        simulation.put(csv_content)

        return reply

###############################################################################
# Alert

class alert:
    def __init__(self, range, cost, message):
        self.range = range
        self.cost = cost
        self.message = message

    def trigger(self):
        pass

class red_alert(alert):
    def __init__(self):
        interval_left  = intervals.left_endpoint(40, False, True)
        interval_right = intervals.right_endpoint(45, False, True)
        interval_expression = intervals.interval_expression([intervals.interval(interval_left, interval_right)])
        super().__init__([interval_expression], 10, "RED ALERT!!!")

    def trigger(self):
        simulation.win_condition_is_not_satisfied = False

class yellow_alert(alert):
    def __init__(self):
        interval_left  = intervals.left_endpoint(45, True, False)
        interval_right = intervals.right_endpoint(70, False, True)
        interval_expression = intervals.interval_expression([intervals.interval(interval_left, interval_right)])
        super().__init__([interval_expression], 5, "Yellow alert!")

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

class ship(movable, decidable):
    def no_movement(self):
        pass

    def create_alert(self, alert):
        self.alerts.append(alert)
        simulation.update(self, [[3, self.balance], [alert.range]])
        return self

    def create_probe(self, probe):
        self.balance -= probe.cost
        simulation.probes.append(probe)
        return self

    def create_perfect_probe(self, location):
        return self.create_probe(perfect_probe(len(simulation.probes), location, self))

    def create_high_probe(self, location):
        return self.create_probe(high_probe(len(simulation.probes), location, self))

    def create_low_probe(self, location):
        return self.create_probe(low_probe(len(simulation.probes), location, self))

    def wait(frames):
        time.sleep(frames / simulation_handler.frame_per_second)

    def try_alert(self, alert, value):
        if all(zip_value[0].contains(zip_value[1]) for zip_value in zip(alert.range, value)):
            if self.balance > alert.cost:
                self.balance -= alert.cost
                simulation.update(self, [[3, self.balance], [alert.message]])
                alert.trigger()
            else:
                simulation.update(self, [["low energy"]])

        return None

    def synchronous_reply_from_ephemeral_deployment(self, processes: list) -> list:
        raw_measurements = [[]] * len(submarine.location)

        for process in processes:
            reply = process.synchronous_read()
            if reply == "True":
                raw_measurements = list(map(lambda value: value[0] + [value[1]], zip(raw_measurements, process.interval)))
            else:
                raw_measurements = list(map(lambda value: value[0] + [value[1].negation()], zip(raw_measurements, process.interval)))

        return raw_measurements

    def interval_byzantine_verification(self, raw_measurements: list) -> list:
        return raw_measurements

    def get_fresh_measurements(self, processes):
        # Heuristic Ephemeral Interval Byzantine Register
        raw_measurements = self.synchronous_reply_from_ephemeral_deployment(processes)
        verified_measurements = self.interval_byzantine_verification(raw_measurements)

        return verified_measurements

    #def awareness(self, message):
    #    pass

    # Problem solving search algorithm
    def strategy(self):
        self.timestamp = 0

        class problem_data:
            def __init__(self, heuristic = None, seed: list = []):
                self.heuristic = heuristic
                self.seed: list = seed

        class formula_data:
            def __init__(self, processes: list, heuristic, seed: list = []):
                self.processes: list = processes
                self.heuristic = heuristic
                self.seed: list = seed

        class solution_data:
            def __init__(self, actions: list, heuristic):
                self.actions: list = actions
                self.heuristic = heuristic

        def formulate(problem: problem_data) -> formula_data:
            if problem is None:
                return None

            processes = []
            for n in range(1, random.randint(3, 4)):
                processes += [process(10, 3, self.timestamp, [random.randint(20, 90)])]
                self.timestamp += 1

            formula = formula_data(processes, problem.heuristic, problem.seed)
            return formula

        def apply(formula: formula_data) -> solution_data:
            if formula is None:
                return None
            
            infered_measurements = []
            for measurements in formula.seed:
                infered_measurements += [functools.reduce(lambda acc, value: acc.intersection(value), measurements)]
                simulation.update(self, [[4, infered_measurements]])
            
            actions = []
            if len(formula.seed) > 0:
                actions += [functools.partial(self.try_alert, red_alert(), infered_measurements)]

            actions += [functools.partial(self.get_fresh_measurements, formula.processes)]

            solution = solution_data(actions, formula.heuristic)

            return solution

        def execute(solution: solution_data) -> problem_data:
            if solution is None:
                time.sleep(1 / simulation_handler.frame_per_second)
                return None
            
            for action in solution.actions:
                result = action()
                if result is not None:
                    seed = result
            time.sleep(1 / simulation_handler.frame_per_second)

            problem = problem_data(solution.heuristic, seed)
            return problem

        # Problem Solving Search Algorithm
        problem = problem_data()
        while simulation.win_condition_is_not_satisfied and simulation.lose_condition_is_not_satisfied:
            search_formula = formulate(problem)
            solution = apply(search_formula)
            problem = execute(solution)

    def __init__(self, location, balance):
        self.balance = balance
        self.value = []
        for value in location:
            self.value.append(intervals.interval_expression.domain())
        self.alerts = []
        self.probes = []
        csv_content = []
        csv_content.append("ship")
        csv_content.append(location)
        csv_content.append(self.balance)
        csv_content.append(self.value)

        # Create log
        simulation.put(csv_content)

        movable.__init__(self, "ship", "ship", location, self.no_movement)
        #awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.strategy)

    def __hash__(self):
        return movable.__hash__(self)

    def __hash__(self):
        return super().__hash__()

class submarine(movable, decidable):
    location = None

    def move_to_submarine(self):
        velocity = list(map(lambda value: -value, submarine.location))
        norm = math.sqrt(sum(value**2 for value in velocity))
        if norm == 0:
            simulation.lose_condition_is_not_satisfied = False
            return
        normalized_vector = list(map(lambda value: value / norm, velocity))
        submarine.location = list(map(lambda value: value[0] + value[1], zip(submarine.location, normalized_vector)))

        #request = str(self.location).encode("ascii")
        #for client in simulation.probes:
        #    client.client_socket.send(request)

        simulation.update(self, [[2, submarine.location]])

    #def awareness(self, message):
    #    pass

    def hack_random_probe(self):
        time.sleep(5)

        #random_probe_socket = random.choice(list(simulation.probes)).client_socket
        
        #random_probe_socket.send(self.type_id.encode("ascii"))

    def __init__(self, location):
        submarine.location = location
        csv_content = []
        csv_content.append("submarine")
        csv_content.append(location)

        # Create log
        simulation.put(csv_content)

        movable.__init__(self, "submarine", "submarine", location, self.move_to_submarine)
        #awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.hack_random_probe)

    def __hash__(self):
        return super().__hash__()

#intervals.test()

simulation.start()
while(True):
    simulation.agents.append(ship([0], 5000))
    simulation.agents.append(submarine([100]))

    for machine in simulation.agents:
        machine.deploy()

    while simulation.win_condition_is_not_satisfied and simulation.lose_condition_is_not_satisfied:
        time.sleep(1 / simulation_handler.frame_per_second)
    simulation.restart()