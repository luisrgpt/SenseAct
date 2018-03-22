#!/usr/bin/python3

import csv
import queue
import threading

###############################################################################
# World
#
# Properties:
# - list of locations
#

log_path = "../user_interface_1_wpf/bin/x86/Debug/AppX/"

class world:
    locations = {}
    network = queue.Queue()
    lock = threading.Lock()

class log_handler(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        world.lock.acquire()
        csv_content = ""
        with open(log_path + self.state.id + ".csv", "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            for csv_line in csv_reader:
                csv_content = csv_line
                break
        with open(log_path + self.state.id + ".csv", "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_content)
        world.lock.release()

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

class movement_handler(log_handler):
    def __init__(self, state):
        super().__init__(state)

    def run(self):
        super().run()
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

class awareness_handler(log_handler):
    def __init__(self, state):
        super().__init__(state)

    def run(self):
        super().run()
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

class strategy_handler(log_handler):
    def __init__(self, state):
        super().__init__(state)

    def run(self):
        super().run()
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

    def __init__(self, id, location, cost, precision):
        movable.__init__(self, id, location)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, self.strategy)
        self.cost = cost
        self.precision = precision
        with open(log_path + self.id + ".csv", "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_content = []
            csv_content.append("blue")
            csv_content.append("blue")
            csv_content.append("left")
            csv_content.append("250")
            csv_content.append("40")
            csv_content.append("00")
            csv_content.append("00")
            csv_content.append("140")
            csv_content.append("Probe: " + self.id + ",Cost: " + f"{self.cost:04}" + ", Value: ")
            csv_writer.writerow(csv_content)

    def __hash__(self):
        return movable.__hash__(self)

#f"{self.super().id:03}" + "," + f"{self.cost:02}" + "," + f"{self.precision:02}"

class low_probe(probe) :
    def __init__(self, id, location):
        super().__init__(id, location, 1, 5)

    def __hash__(self):
        return super().__hash__()

class high_probe(probe) :
    def __init__(self, id, location):
        super().__init__(id, location, 10, 2)

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
        movable.__init__(self, id, location, movement)
        awareable.__init__(self, self.awareness)
        decidable.__init__(self, strategy)
        self.balance = balance
        self.probes = []

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
        return self.create_probe(high_probe(len(self.probes), location))

    def create_low_probe(self, location):
        return self.create_probe(low_probe(len(self.probes), location))

    def strategy(self):
        return self.create_high_probe((1,1,1))

    def __init__(self, balance):
        super().__init__("blue", (0,0,0), self.no_movement, self.strategy, balance)
        with open(log_path + self.id + ".csv", "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_content = []
            csv_content.append("blue")
            csv_content.append("blue")
            csv_content.append("left")
            csv_content.append("40")
            csv_content.append("40")
            csv_content.append("00")
            csv_content.append("40")
            csv_content.append("200")
            csv_content.append("Submarine: blue,Balance: " + f"{self.balance:04}")
            csv_writer.writerow(csv_content)

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
        with open(log_path + self.id + ".csv", "w+", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_content = []
            csv_content.append("red")
            csv_content.append("red")
            csv_content.append("right")
            csv_content.append("00")
            csv_content.append("40")
            csv_content.append("40")
            csv_content.append("40")
            csv_content.append("200")
            csv_content.append("Submarine: red,Balance: 100")
            csv_writer.writerow(csv_content)

    def __hash__(self):
        return super().__hash__()

blu_submarine = defensive_submarine(100)
red_submarine = offensive_submarine((10,10,10))

#write("red",  "red_submarine,red,right,00,40,40,40,200,Submarine:  Red,Balance:    100")

# ",- " + ",- ".join(map(self.print_probe, self.probes))
