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
        self.log_content = []

        self.dictionary = {}
        self.csv_content = []

        self.log_file_name = simulation_handler.csv_prefix + str(time.strftime("%Y_%m_%d_%H_%M_%S")) + simulation_handler.log_suffix

        files = [ file for file in os.listdir(simulation_handler.csv_prefix) if file.endswith(simulation_handler.csv_suffix) ]
        for file in files:
            os.remove(os.path.join(simulation_handler.csv_prefix, file))

        time.sleep(1 / simulation_handler.frame_per_second)

        self.submarines = []
        self.probes = []
        self.lock.release()

    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.restart()

        self.awareness_handlers = {}

    def reset_condition(self):
        if len(self.submarines) < 2:
            return True

        reset_condition = any(value[0] != value[1] for value in zip(self.submarines[0].location, self.submarines[1].location))

        return reset_condition

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
        self.log_content = self.stack.copy()
        self.stack = []

        self.csv_content = self.dictionary.copy()
        self.lock.release()

    def run(self):
        while(True):
            self.take_all()

            with open(self.log_file_name, "a+", newline="") as log_file:
                log_writer = csv.writer(log_file)
                for log_row in self.log_content:
                    log_writer.writerow(log_row)

            for csv_id, csv_row in self.csv_content.items():
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
        while(simulation.reset_condition()):
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

class socket_handler(threading.Thread):
    def __init__(self, state, socket):
        super().__init__()
        self.state = state
        self.socket = socket

    def restart(self, new_state):
        self.state = new_state

    def run(self):
        while(True):
            # Receive message
            message = self.socket.recv(10)
            # Process message
            self.state.awareness(message.decode("ascii"))

class awareness_handler(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.socket_handlers = []

    def restart(self, new_state):
        new_state.socket = self.state.socket
        new_state.client_socket = self.state.client_socket
        self.state = new_state
        for socket_handler in self.socket_handlers:
            socket_handler.restart(self.state)

    def run(self):
        while(True):
            # Establish connection
            client_socket, _ = self.state.socket.accept()
            # Receive message
            self.socket_handlers.append(socket_handler(self.state, client_socket))
            self.socket_handlers[-1].start()

class awareable:
    def no_awareness(message):
        pass

    def __init__(self, awareness = no_awareness):
        self.memory = []
        self.awareness = awareness

        # Get port
        if self.type_id == "ship":
            self.port = 10040
        elif self.type_id == "submarine":
            self.port = 10050
        elif self.type_id == "probe":
            self.port = 20000 + int(self.id)

        if self.port in simulation.awareness_handlers:
            simulation.awareness_handlers[self.port].restart(self)
        else:
            # Create a TCP server socket object
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Get local machine name
            self.hostname = socket.gethostname()
            # TCP bind to hostname on the port.
            self.socket.bind((self.hostname, self.port))
            # Queue up to 10 requests
            self.socket.listen(10)

            # Create a TCP client socket object
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Establish connection
            self.client_socket.connect((self.hostname, self.port))

            simulation.awareness_handlers[self.port] = awareness_handler(self)
            simulation.awareness_handlers[self.port].start()


    def __hash__(self):
        return hash(self.id)

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

class probe(movable, awareable):
    def movement(self):
        pass

    def awareness(self, message):
        if message == "submarine":
            simulation.update(self, [["HACKED!!!"]])
        elif message == "probe":
            # Send message
            message = self.value.encode("ascii")
            self.owner.client_socket.send(message)
        else:
            # Parse message
            submarine_location = ast.literal_eval(message)
            # Calculate measurements
            distance = math.sqrt(functools.reduce(lambda acc, value: acc + (value[0] - value[1])**2, zip(self.location, submarine_location), 0))
            if distance <= self.precision:
                self.value = "yes"
                # Update log
                simulation.update(self, [[4, self.value]])
            elif self.value == "yes":
                self.value = "no"
                # Update log
                simulation.update(self, [[4, self.value]])

    def __init__(self, id, location, owner, cost, precision):
        self.cost : int = cost
        self.precision : int = precision
        self.value : int = "no"
        self.owner = owner
        csv_content = []
        csv_content.append("probe")
        csv_content.append(id)
        csv_content.append(list(map(lambda value: intervals.interval(value - precision, value + precision, intervals.limit.open, intervals.limit.open), location)))
        csv_content.append(self.value)

        # Create log
        simulation.put(csv_content)

        movable.__init__(self, "probe", id, location, self.movement)
        awareable.__init__(self, self.awareness)
        #decidable.__init__(self, self.strategy)

    def __hash__(self):
        return movable.__hash__(self)

class low_probe(probe) :
    def __init__(self, id, location, owner):
        super().__init__(id, location, owner, 1, 5)

    def __hash__(self):
        return super().__hash__()

class high_probe(probe) :
    def __init__(self, id, location, owner):
        super().__init__(id, location, owner, 10, 3)

    def __hash__(self):
        return super().__hash__()

class perfect_probe(probe) :
    def __init__(self, id, location, owner):
        super().__init__(id, location, owner, 0, 0)

    def __hash__(self):
        return super().__hash__()

###############################################################################
# Alert

class alert:
    def __init__(self, range, cost):
        self.interval = range
        self.cost = cost

class red_alert(alert):
    def __init__(self):
        super().__init__(intervals.interval(40, 45, intervals.limit.closed, intervals.limit.closed), 10)

class yellow_alert(alert):
    def __init__(self):
        super().__init__(intervals.interval(45, 70, intervals.limit.open, intervals.limit.closed), 5)

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

class ship(movable, awareable, decidable):
    def no_movement(self):
        pass

    def create_probe(self, probe):
        self.balance -= probe.cost
        simulation.probes.append(probe)
        simulation.update(self, [[3, self.balance], [probe.id]])
        return self

    def create_perfect_probe(self, location):
        return self.create_probe(perfect_probe(len(simulation.probes), location, self))

    def create_high_probe(self, location):
        return self.create_probe(high_probe(len(simulation.probes), location, self))

    def create_low_probe(self, location):
        return self.create_probe(low_probe(len(simulation.probes), location, self))

    def try_red_alert(self, value):
        if (red_alert().interval.contains(value)):
            simulation.update(self, [["RED ALERT!!!"]])

    def try_yellow_alert(self, value):
        if (yellow_alert().interval.contains(value)):
            simulation.update(self, [["Yellow alert!"]])

    def awareness(self, message):
        if len(simulation.probes) >= 3:
            #self.value = self.formula_3(simulation.probes[0], simulation.probes[1], simulation.probes[2])
            simulation.update(self, [[4, self.value]])

    def strategy(self):
        if len(simulation.probes) == 0:
            for n in range(1, random.randint(2, 20)):
                self.create_high_probe([random.randint(20, 90)])

            for n in range(1, random.randint(2, 20)):
                self.create_low_probe([random.randint(20, 90)])

    def __init__(self, location, balance):
        self.balance = balance
        self.value = -1
        csv_content = []
        csv_content.append("ship")
        csv_content.append(location)
        csv_content.append(self.balance)
        csv_content.append(self.value)

        # Create log
        simulation.put(csv_content)

        movable.__init__(self, "ship", "ship", location, self.no_movement)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.strategy)

    def __hash__(self):
        return movable.__hash__(self)

    def __hash__(self):
        return super().__hash__()

class submarine(movable, awareable, decidable):
    def move_to_submarine(self):
        velocity = list(map(lambda value: -value, self.location))
        norm = math.sqrt(functools.reduce(lambda acc, value: acc + value**2, velocity, 0))
        if norm == 0:
            return
        normalized_vector = list(map(lambda value: value / norm, velocity))
        self.location = list(map(lambda value: value[0] + value[1], zip(self.location, normalized_vector)))

        for _, handler in simulation.awareness_handlers.items():
            if handler.state.type_id == "probe" and len(simulation.probes) >= handler.state.id:
                handler.state.client_socket.send(str(self.location).encode('ascii'))
        simulation.update(self, [[2, self.location]])

    def awareness(self, message):
        pass

    def hack_random_probe(self):
        time.sleep(5)

        hack_probe = random.choice(list(simulation.awareness_handlers.values()))
        while hack_probe.state.type_id != "probe" and len(simulation.probes) >= hack_probe.state.id:
            hack_probe = random.choice(list(simulation.awareness_handlers.values()))
        
        hack_probe.state.client_socket.send("submarine".encode('ascii'))

        pass

    def __init__(self, location):
        csv_content = []
        csv_content.append("submarine")
        csv_content.append(location)

        # Create log
        simulation.put(csv_content)

        movable.__init__(self, "submarine", "submarine", location, self.move_to_submarine)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.hack_random_probe)

    def __hash__(self):
        return super().__hash__()

#intervals.test()

simulation.start()
while(True):
    simulation.submarines.append(ship([0], 500))
    simulation.submarines.append(submarine([100]))

    while(simulation.reset_condition()):
        time.sleep(1 / simulation_handler.frame_per_second)
    simulation.restart()