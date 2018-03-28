#!/usr/bin/python3

import asyncio
import csv
import functools
import math
import os
import queue
import random
import time
import threading

###############################################################################
# World
#
# Properties:
# - list of locations
#

csv_prefix = "../user_interface_1_wpf/bin/x86/Debug/AppX/"
csv_suffix = "_current.csv"

log_file_name = csv_prefix + str(time.strftime("%Y_%m_%d_%H_%M_%S")) + "_log.csv"

files = [ file for file in os.listdir(csv_prefix) if file.endswith(csv_suffix) ]
for file in files:
    os.remove(os.path.join(csv_prefix, file))

class world:
    locations = {}
    network = []
    darknet = []
    lock = threading.Lock()

###############################################################################
# Logging
#

#class logging_scheduler(threading.Thread):
#    loop = asyncio.get_event_loop()

#    def run(self):
#        self.loop.run_forever()

class logging_handler(threading.Thread):
    stack = []
    log_content = []

    dictionary = {}
    csv_content = []

    lock = threading.Lock()

    def put(csv_content):
        logging_handler.lock.acquire()
        logging_handler.stack.append(csv_content.copy())
        logging_handler.dictionary[csv_content[1] + "_" + csv_content[2]] = csv_content.copy()
        logging_handler.lock.release()

    def update(submarine_or_probe, csv_changes = []):
        csv_changes.append((0, time.strftime("%Y_%m_%d_%H_%M_%S")))

        logging_handler.lock.acquire()
        csv_content = logging_handler.dictionary[submarine_or_probe.type_id + "_" + submarine_or_probe.id]
        
        for csv_change in csv_changes:
            if len(csv_change) == 1:
                csv_content.append(csv_change[0])
            elif len(csv_change) == 2:
                csv_content[csv_change[0]] = csv_change[1]
        logging_handler.lock.release()

        logging_handler.put(csv_content)

    def take_all(self):
        logging_handler.lock.acquire()
        logging_handler.log_content = logging_handler.stack.copy()
        logging_handler.stack = []

        logging_handler.csv_content = logging_handler.dictionary.copy()
        logging_handler.lock.release()

    def run(self):
        # logging_scheduler.loop.call_soon_threadsafe(self.take_all)
        self.take_all()

        with open(log_file_name, "a+", newline="") as log_file:
            log_writer = csv.writer(log_file)
            for log_row in logging_handler.log_content:
                log_writer.writerow(log_row)

        for csv_id, csv_row in logging_handler.csv_content.items():
            with open(csv_prefix + csv_id + csv_suffix, "w+", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(csv_row)

        threading.Timer(1, self.run).start()

# logging_scheduler().start()
logging_handler().start()

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
        self.state.movement()

class movable:
    def no_movement():
        pass

    def __init__(self, type_id, id, location, movement = no_movement):
        self.type_id = type_id
        self.id = str(id)
        world.locations[hash(self.id)] = location
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

class awareness_handler(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        self.state.awareness()

class awareable:
    def no_awareness():
        pass

    def __init__(self, awareness = no_awareness):
        self.memory = []
        self.awareness = awareness
        awareness_handler(self).start()

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

class probe(movable, awareable, decidable):
    def awareness(self):
        if(int(self.id) in world.darknet):
            self.owner_id = "red"
            logging_handler.update(self, [(3, self.owner_id)])
        threading.Timer(1, self.awareness).start()

    def strategy(self):
        # Get locations
        location = world.locations[hash(self.id)]
        red_location = world.locations[hash("red")]
        # Calculate measurements
        measurement = math.sqrt(functools.reduce(lambda acc, value: acc + (location[value] - red_location[value])**2, [0, 1, 2], 0))
        measurement_with_error = measurement + random.uniform(-self.precision, self.precision)
        
        self.value = measurement_with_error if measurement_with_error > 0 else 0
        # Send measurement
        world.lock.acquire()
        world.network.append((self.id, self.value))
        world.lock.release()

        # Update log
        # logging_scheduler.loop.call_soon_threadsafe(logging_handler.update, [(1, self.type_id), (2, self.id), (0, time.strftime("%Y_%m_%d_%H_%M_%S")), (7, str(self.value))])
        logging_handler.update(self, [(7, str(self.value))])

        # Repeat strategy
        threading.Timer(1, self.strategy).start()

    def __init__(self, id, location, owner, cost, precision):
        self.owner_id = str(owner.id)
        self.cost : int = cost
        self.precision : int = precision
        self.value : int = -1
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        csv_content = []
        csv_content.append(timestamp)
        csv_content.append("probe")
        csv_content.append(str(id))
        csv_content.append(self.owner_id)
        csv_content.append(location)
        csv_content.append(str(self.cost))
        csv_content.append(str(self.precision))
        csv_content.append(str(self.value))

        # Create log
        # logging_scheduler.loop.call_soon_threadsafe(logging_handler.put, csv_content)
        logging_handler.put(csv_content)

        movable.__init__(self, "probe", id, location)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.strategy)

    def __hash__(self):
        return movable.__hash__(self)

class low_probe(probe) :
    def __init__(self, id, location, owner):
        super().__init__(id, location, owner, 1, 5)

    def __hash__(self):
        return super().__hash__()

class high_probe(probe) :
    def __init__(self, id, location, owner):
        super().__init__(id, location, owner, 10, 2)

    def __hash__(self):
        return super().__hash__()

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

class submarine(movable, awareable, decidable):
    def awareness(self):
        world.lock.acquire()
        messages = world.network.copy()
        world.network = []
        world.lock.release()

        self.memory += messages
        threading.Timer(1, self.awareness).start()

    def __init__(self, id, location, movement, strategy, balance):
        self.balance = balance
        self.probes = []
        csv_content = []
        csv_content.append(time.strftime("%Y_%m_%d_%H_%M_%S"))
        csv_content.append("submarine")
        csv_content.append(str(id))
        csv_content.append(str(id))
        csv_content.append(location)
        csv_content.append(str(self.balance))

        # Create log
        # logging_scheduler.loop.call_soon_threadsafe(logging_handler.put, csv_content)
        logging_handler.put(csv_content)

        movable.__init__(self, "submarine", id, location, movement)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, strategy)

    def __hash__(self):
        return movable.__hash__(self)

class defensive_submarine(submarine):
    def no_movement(self):
        pass

    def create_probe(self, probe):
        self.balance -= probe.cost
        self.probes.append(probe)
        logging_handler.update(self, [(4, str(self.balance)), (probe.id)])
        return self

    def create_high_probe(self, location):
        return self.create_probe(high_probe(len(self.probes), location, self))

    def create_low_probe(self, location):
        return self.create_probe(low_probe(len(self.probes), location, self))

    def strategy(self):
        if(len(world.locations) == 2):
            self.create_high_probe((5,0,0))
        if(len(world.locations) == 3):
            self.create_low_probe((1,2,1))
            self.create_high_probe((4,2,1))
        if(len(world.locations) == 5):
            self.create_low_probe((1,2,3))
        if(len(world.locations) == 6):
            self.create_low_probe((1,5,3))
            self.create_low_probe((-1,2,3))
        threading.Timer(1, self.strategy).start()

    def __init__(self, location, balance):
        super().__init__("blu", location, self.no_movement, self.strategy, balance)

    def __hash__(self):
        return super().__hash__()

class offensive_submarine(submarine):
    def move_to_submarine(self):
        current_location = world.locations[hash(self.id)]
        next_location = current_location
        world.locations[hash(self.id)] = next_location
        #logging_handler.update([(1, self.state.type_id), (2, self.state.id)])
        threading.Timer(1, self.move_to_submarine).start()

    def hack_random_probe(self):
        time.sleep(9)
        world.darknet.append(random.randint(0, 5))
        threading.Timer(1, self.hack_random_probe).start()

    def __init__(self, location, balance):
        super().__init__("red", location, self.move_to_submarine, self.hack_random_probe, 100)

    def __hash__(self):
        return super().__hash__()

blu_submarine = defensive_submarine((0,0,0), 100)
red_submarine = offensive_submarine((10,0,0), 100)

