#!/usr/bin/python3

import csv
import queue
import time
import threading

###############################################################################
# World
#
# Properties:
# - list of locations
#

current_csv_prefix = "../user_interface_1_wpf/bin/x86/Debug/AppX/"
log_csv_prefix = current_csv_prefix + str(time.strftime("%Y_%m_%d_%H_%M_%S_"))

current_csv_suffix = "_current.csv"
log_csv_suffix = "_log.csv"

class world:
    locations = {}
    network = queue.Queue()
    lock = threading.Lock()

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
        csv_content = ""
        world.lock.acquire()
        with open(current_csv_prefix + self.state.id + current_csv_suffix, "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            for csv_line in csv_reader:
                csv_content = csv_line
                break
        with open(current_csv_prefix + self.state.id + current_csv_suffix, "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        world.lock.release()
        self.state.movement()

class movable:
    def no_movement():
        pass

    def __init__(self, id, location, movement = no_movement):
        self.id = str(id)
        world.locations[self] = location
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
        csv_content = ""
        world.lock.acquire()
        with open(current_csv_prefix + self.state.id + current_csv_suffix, "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            for csv_line in csv_reader:
                csv_content = csv_line
                break
        with open(current_csv_prefix + self.state.id + current_csv_suffix, "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        world.lock.release()
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
        csv_content = ""
        world.lock.acquire()
        with open(current_csv_prefix + self.state.id + current_csv_suffix, "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            for csv_line in csv_reader:
                csv_content = csv_line
                break
        with open(current_csv_prefix + self.state.id + current_csv_suffix, "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        world.lock.release()
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
        # Nothing
        pass

    def strategy(self):
        # Get measurement
        distance = world.locations[self]
        # Send measurement
        world.network.put(distance)
        # Repeat strategy
        threading.Timer(1, self.strategy).start()

    def __init__(self, id, location, owner_id, cost, precision):
        self.owner_id = str(owner_id)
        self.cost = cost
        self.precision = precision
        csv_content = []
        csv_content.append(time.strftime("%Y_%m_%d_%H_%M_%S"))
        csv_content.append("probe")
        csv_content.append(str(id))
        csv_content.append(str(owner_id))
        csv_content.append(location)
        csv_content.append(f"{self.cost:03}")
        csv_content.append(f"{self.precision:03}")
        csv_content.append("-")
        world.lock.acquire()
        with open(current_csv_prefix + str(id) + current_csv_suffix, "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        with open(log_csv_prefix + str(id) + log_csv_suffix, "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        world.lock.release()
        movable.__init__(self, id, location)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.strategy)

    def __hash__(self):
        return movable.__hash__(self)

#f"{self.super().id:03}" + "," + f"{self.cost:02}" + "," + f"{self.precision:02}"

class low_probe(probe) :
    def __init__(self, id, location, owner_id):
        super().__init__(id, location, owner_id, 1, 5)

    def __hash__(self):
        return super().__hash__()

class high_probe(probe) :
    def __init__(self, id, location, owner_id):
        super().__init__(id, location, owner_id, 10, 2)

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
        message = world.network.get()
        self.memory.append(message)
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
        csv_content.append(f"{self.balance:04}")
        world.lock.acquire()
        with open(current_csv_prefix + str(id) + current_csv_suffix, "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        world.lock.release()
        movable.__init__(self, id, location, movement)
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
        return self

    def create_high_probe(self, location):
        return self.create_probe(high_probe(len(self.probes), location, self.id))

    def create_low_probe(self, location):
        return self.create_probe(low_probe(len(self.probes), location, self.id))

    def strategy(self):
        if(len(world.locations) == 2):
            self.create_high_probe((1,1,1))
        if(len(world.locations) == 3):
            self.create_low_probe((1,2,1))
            self.create_high_probe((4,2,1))
        if(len(world.locations) == 5):
            self.create_low_probe((1,2,3))
        if(len(world.locations) == 6):
            self.create_low_probe((1,5,3))
            self.create_low_probe((-1,2,3))
        threading.Timer(1, self.strategy).start()

    def __init__(self, balance):
        super().__init__("blu", (0,0,0), self.no_movement, self.strategy, balance)

    def __hash__(self):
        return super().__hash__()

class offensive_submarine(submarine):
    def move_to_submarine(self):
        current_location = world.locations[self]
        next_location = current_location
        world.locations[self] = next_location
        threading.Timer(1, self.move_to_submarine).start()

    def hack_random_probe(self):
        print("sls")

    def __init__(self, location):
        super().__init__("red", (0,0,0), self.move_to_submarine, self.hack_random_probe, 100)

    def __hash__(self):
        return super().__hash__()

blu_submarine = defensive_submarine(100)
red_submarine = offensive_submarine((10,10,10))

#write("red",  "red_submarine,red,right,00,40,40,40,200,Submarine:  Red,Balance:    100")

# ",- " + ",- ".join(map(self.print_probe, self.probes))
