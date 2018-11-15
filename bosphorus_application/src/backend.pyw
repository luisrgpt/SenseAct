# coding=utf-8
############################################################










############################################################
from algorithm import evaluate
from ast import literal_eval
import csv
from graphs import Graph, Node, Hyperedge
from intervals import Interval
from time import strftime, time
from datetime import datetime
from logging import basicConfig, INFO, debug, info
from random import random, randint, choice
basicConfig(
    filename='example.yaml',
    filemode='w',
    format='info: %(message)s',
    level=INFO
)
enter_info_format = """  {0}
module: '{1}'
class:  '{2}'
method: '{3}'
phase:  'enter'
input:  {4}
state:  {5}
---"""
exit_info_format = """  {0}
module: '{1}'
class:  '{2}'
method: '{3}'
phase:  'exit'
state:  {4}
output: {5}
---"""
############################################################










############################################################
class UncertainEnvironment:
############################################################










############################################################
    def __init__(
        self,
        name,

        boundaries,
        trajectory,
        initial_position
    ):
        # Log
        self.name = name

        # State
        self.boundaries = boundaries
        self.trajectory = trajectory(initial_position)
        self.position   = initial_position

        self.arriving_probes = {}
        self.measurements = {}
############################################################










############################################################
    def __repr__(
            self
    ):
        return """
    name:       '{0}'
    boundaries: '{1}'
    position:   {2}""".format(
            self.name,
            self.boundaries,
            self.position
        )
############################################################










############################################################
    def wait(
            self,
            unit_time
    ):
        ####################################################
        # Debug
        debug('Entering backend.UncertainEnvironment.wait')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'wait',
                '',
                self
            )
        )
        ####################################################

        # As time passes...
        self.position = next(self.trajectory)

        # ...probes land and take their measurements.
        landed_probes = self.arriving_probes
        self.measurements = {
            name: [
                (float(location), float(imprecision), cost, abs(location - self.position) <= imprecision, False)
                for cost, imprecision, location in probes
            ]
            for name, probes in landed_probes.items()
        }
        self.arriving_probes = {}

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'wait',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.UncertainEnvironment.wait')
        ####################################################

        return self
############################################################










############################################################
    def import_probes(
            self,
            source
    ):
        ####################################################
        # Debug
        debug('Entering backend.UncertainEnvironment.import_probes')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'import_probes',
                source,
                self
            )
        )
        ####################################################

        source.probe_cost += sum(x for x, _, _ in source.departing_probes)
        self.arriving_probes[source.name] = source.departing_probes

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'import_probes',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.UncertainEnvironment.import_probes')
        ####################################################

        return self
############################################################










############################################################
class DecisionSupportSystem:
############################################################










############################################################

    # FIXME: Implement a better way of importing the cost table only once, without an initialization method
    # Ugly way to import the cost table once
    cost_table: dict = {}
    with open('../share/cost_table.csv', newline='') as file:
        reader = csv.reader(
            file,
            escapechar='\\',
            lineterminator='\n',
            delimiter=';',
            quoting=csv.QUOTE_NONE
        )
        for row in reader:
            cost_table[literal_eval(row[0])] = literal_eval(row[1])

############################################################










############################################################
    def __init__(
            self,

            # Log
            name,

            # State
            alert_cost,
            probe_cost,
            answer_intervals,
            action_history,
            turn,

            # Parameters
            boundaries,
            alert_catalog,
            probe_success_rate_area,
            trajectory_speed,
            cost_table_quality,
            byzantine_fault_tolerance,

            probe_catalog
    ):
        # Log
        self.name = name

        # State
        self.alert_cost = alert_cost
        self.probe_cost = probe_cost
        self.answer_intervals = answer_intervals
        self.action_history = action_history
        self.turn = turn

        # Parameters
        self.boundaries = boundaries
        self.alert_catalog = alert_catalog
        self.probe_success_rate_area = probe_success_rate_area
        self.trajectory_speed = trajectory_speed
        self.cost_table_quality = cost_table_quality
        self.byzantine_fault_tolerance = byzantine_fault_tolerance


        self.graph: Graph = Graph(
                node=Node(
                    label=str(answer_intervals)
                )
            )
        if self.name == "dynamic_programming":
            self.graph.export_png(
                directory='./log',
                filename= self.name + '_' + str(self.turn) + '_00_start_' + self.name
            )
        self.departing_probes = []
        n_boundaries = boundaries[1][0] - boundaries[0][0]
        self.boundaries_distribution = [1 / n_boundaries] * n_boundaries
        self.probe_catalog = probe_catalog
        self.measurements = []
        self.current_alert = (None, 0)
############################################################










############################################################
    def __repr__(
            self
    ):
        return """
    name:                      '{0}'
    alert_cost:                {1}
    probe_cost:                {2}
    answer_intervals:          '{3}'
    action_history:
    turn:          {4}
    boundaries:                '{5}'
    alert_catalog:
    probe_success_rate_area:
    trajectory_speed:
    cost_table_quality:
    byzantine_fault_tolerance: {6}
    graph:
    departing_probes:
    boundaries_distribution:
    probe_catalog:""".format(
            self.name,
            self.alert_cost,
            self.probe_cost,
            self.answer_intervals,
            self.turn,
            self.boundaries,
            self.byzantine_fault_tolerance
        )
############################################################










############################################################
    def export_csv_content(
            self
    ):
        # Info 1: System
        csv_content = [strftime('%Y_%m_%d_%H_%M_%S')]
        csv_content += [0]
        csv_content += [self.turn]
        csv_content += [self.alert_cost + self.probe_cost]
        csv_content += [self.answer_intervals]

        # Info 2: Environment
        csv_content += [1234]
        csv_content += [self.turn]

        # Info 3: Graph
        csv_content += [self.graph.export_png(
            directory='../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX',
            filename=str(time.strftime('%Y_%m_%d_%H_%M_%S'))
        )]
        # Info 4: Measurements
        counter = 0
        for timestamp, batch in enumerate(self.action_history, start=1):
            decay = self.turn - timestamp
            if not batch:
                continue
            counter += 1
            for label, probe in enumerate(batch):
                if not probe:
                    continue
                location, imprecision, cost, does_detect, does_lie = probe
                csv_content += [counter]
                csv_content += [label]
                csv_content += [timestamp]
                csv_content += [location]
                csv_content += [imprecision]
                csv_content += [decay]
                csv_content += [cost]
                csv_content += [does_detect]
                csv_content += [
                    Interval([
                        ((location - imprecision - decay, True), (location + imprecision + decay, False))
                    ])
                    if does_detect
                    else
                    Interval([
                        (0, (location - imprecision + decay, True)),
                        ((location + imprecision - decay, False), 100)
                    ])
                ]

        # Final step: Convert info into csv parameters
        csv_content = [str(x) for x in csv_content]
        stream = csv.StringIO()
        writer = csv.writer(stream)
        writer.writerow(csv_content)

        return stream.getvalue()
############################################################










############################################################
    def wait(
            self,
            unit_time
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.wait')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'wait',
                '',
                self
            )
        )
        ####################################################

        # As time passes...
        self.turn += 1

        # ... unmeasured intervals may involve costly alerts,...
        alert_cost = 0
        for answer_intervals_yes in self.answer_intervals:
            for x, cost in self.alert_catalog:
                if alert_cost < cost and (answer_intervals_yes if x[1] <= answer_intervals_yes[1] else x)[0] < (answer_intervals_yes if answer_intervals_yes[0] <= x[0] else x)[1]:
                    alert_cost = cost
                    self.current_alert = (x, cost)
        self.alert_cost += alert_cost

        # ... while every measurement gets less accurate...
        snapshot = Interval(self.answer_intervals[:])
        self.answer_intervals += (0, self.trajectory_speed)
        self.answer_intervals &= Interval([self.boundaries])
        self.graph += [
            Hyperedge(
                sources=[Interval([source]) for source in snapshot if Interval([source]) in Interval([target])],
                targets=[Interval([target])],
                weight=0,
                label='Wait'
            ) for target in self.answer_intervals
        ]
        if self.name == "dynamic_programming":
            self.graph.export_png(
                directory='./log',
                filename=str(self.turn) + '_01_wait_' + self.name
            )

        # ... or even useless, some minutes after being obtained.
        for timestamp, batch in enumerate(self.action_history):
            if not batch:
                continue
            decay = (self.turn - timestamp) * self.trajectory_speed
            for index, probe in enumerate(batch):
                if not probe:
                    continue
                location, imprecision, _, does_detect, _ = probe
                upper_margin = self.boundaries[1][0] - imprecision - decay
                lower_margin = self.boundaries[0][0] + imprecision + decay
                useless_yes = does_detect and upper_margin < location < lower_margin
                useless_no = not does_detect and decay >= imprecision
                if useless_yes or useless_no:
                    batch[index] = None
                    continue

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'wait',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.wait')
        ####################################################

        return self
############################################################










############################################################
    def import_measurements(
            self,
            source
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.import_measurements')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'import_measurements',
                source,
                self
            )
        )
        ####################################################

        if self.name in source.measurements and len(source.measurements[self.name]) > 0:
            self.measurements = source.measurements[self.name]

        else:
            self.measurements = []

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'import_measurements',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.import_measurements')
        ####################################################

        return self
############################################################










############################################################
    def invoke_inference_algorithm(
            self
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.invoke_inference_algorithm')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_inference_algorithm',
                '',
                self
            )
        )
        ####################################################

        if len(self.measurements) > 0:
            # Solution 1: Generate result
            snapshot = Interval(self.answer_intervals[:])

            current_answer_interval = Interval([])
            lower_boundaries, upper_boundaries = self.boundaries
            for location, imprecision, _, does_detect, _ in self.measurements:
                if does_detect:
                    current_answer_interval.intervals = [
                        ((location - imprecision, True), (location + imprecision, False))
                    ]
                else:
                    current_answer_interval.intervals = [
                        (lower_boundaries, (location - imprecision, True)),
                        ((location + imprecision, False), upper_boundaries)
                    ]
            self.answer_intervals &= current_answer_interval

            # Solution 2: Update state
            self.graph += [
                Hyperedge(
                    sources=[Interval([source])],
                    targets=[Interval([target]) for target in self.answer_intervals if Interval([target]) in Interval([self.measurements])],
                    weight=self.alert_cost + self.probe_cost,
                    label=str([(location, imprecision, does_detect) for location, imprecision, _, does_detect, _ in self.measurements])
                ) for source in snapshot
            ]
            if self.name == "dynamic_programming":
                self.graph.export_png(
                    directory='./log',
                    filename=str(self.turn) + '_02_probe_' + self.name
                )
            self.action_history += [self.measurements]
        else:
            self.action_history += [None]

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_inference_algorithm',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.invoke_inference_algorithm')
        ####################################################

        return self
############################################################










############################################################
    def invoke_dynamic_programming_algorithm(
            self,
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.invoke_dynamic_programming_algorithm')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_dynamic_programming_algorithm',
                '',
                self
            )
        )
        ####################################################

        start = time()

        # Step 1: Redistribute probabilistic distribution
        n_dist = len(self.boundaries_distribution)
        new_boundaries_distribution = [0] * n_dist
        new_boundaries_distribution[0] += self.boundaries_distribution[0] * 1 / 2
        new_boundaries_distribution[1] += self.boundaries_distribution[0] * 1 / 2
        for x in range(1, n_dist - 1):
            a_third = self.boundaries_distribution[x] * 1 / 3
            new_boundaries_distribution[x - 1] += a_third
            new_boundaries_distribution[x] += a_third
            new_boundaries_distribution[x + 1] += a_third
        new_boundaries_distribution[-2] += self.boundaries_distribution[-1] * 1 / 2
        new_boundaries_distribution[-1] += self.boundaries_distribution[-1] * 1 / 2
        self.boundaries_distribution = new_boundaries_distribution

        # Step 2: Crop probabilistic distribution
        total_pb = 0
        for x in range(n_dist):
            if Interval([((x, True), (x + 1, False))]) in self.answer_intervals:
                total_pb += self.boundaries_distribution[x]
            else:
                self.boundaries_distribution[x] = 0
        for x in range(n_dist):
            if Interval([((x, True), (x + 1, False))]) in self.answer_intervals:
                self.boundaries_distribution[x] /= total_pb

        # Step 3: Pick the best set of probes for each disjunction
        best_comb = []
        for answer_intervals in self.answer_intervals:
            best_comb += [min(
                self.cost_table[(self.cost_table_quality, answer_intervals)],
                key=lambda x:
                    evaluate(
                        time=self.cost_table_quality,
                        cost_table=self.cost_table,
                        boundaries=self.boundaries,
                        alert_catalog=self.alert_catalog,
                        trajectory_speed=self.trajectory_speed,
                        nucleus=x[0],
                        probe_catalog=self.probe_catalog,

                        probe_success_rate_area=self.probe_success_rate_area,
                        byzantine_fault_tolerance=self.byzantine_fault_tolerance,

                        boundaries_distributions=[self.boundaries_distribution],

                        answer_intervals=[answer_intervals],

                        convert=False
                    )[0]
            )[0]]

        # Step 4: Prepare probe information
        self.departing_probes = [
            (self.probe_catalog[u], u, pos)
            for x in best_comb
            for u, comb in x
            for pos in comb
        ]

        end = time()
        #print('[' + self.name + '] ' + str(self.alert_cost) + ', ' + str(self.probe_cost) + ', ' + str(end - start))

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_dynamic_programming_algorithm',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.invoke_dynamic_programming_algorithm')
        ####################################################

        return self
############################################################










############################################################
    def invoke_greedy_algorithm(
            self
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.invoke_greedy_algorithm')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_greedy_algorithm',
                '',
                self
            )
        )
        ####################################################

        cheapest_probe = min(self.probe_catalog.keys(), key=self.probe_catalog.get)
        ((a_left_point, _), (a_right_point, _)) = self.answer_intervals[0]
        ((b_left_point, _), (b_right_point, _)) = self.boundaries

        start = time()

        if self.turn == 0:
            # Send as many probes as possible
            self.departing_probes = [
                (self.probe_catalog[cheapest_probe], cheapest_probe, x)
                for x in range(0, 101)
            ]

        else:
            if b_left_point <= a_left_point - cheapest_probe:
                left_probe_location = a_left_point - cheapest_probe
            elif a_left_point + cheapest_probe <= b_right_point:
                left_probe_location = a_left_point + cheapest_probe

            if b_left_point <= a_right_point - cheapest_probe:
                right_probe_location = a_right_point - cheapest_probe
            elif a_right_point + cheapest_probe <= b_right_point:
                right_probe_location = a_right_point + cheapest_probe

            self.departing_probes = [
                (self.probe_catalog[cheapest_probe], cheapest_probe, left_probe_location),
                (self.probe_catalog[cheapest_probe], cheapest_probe, right_probe_location)
            ]

        end = time()
        #print('[' + self.name + '] ' + str(self.alert_cost) + ', ' + str(self.probe_cost) + ', ' + str(end - start))

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_greedy_algorithm',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.invoke_greedy_algorithm')
        ####################################################

        return self
############################################################










############################################################
    def invoke_lazy_algorithm(
            self
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.invoke_lazy_algorithm')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_lazy_algorithm',
                '',
                self
            )
        )
        ####################################################

        cheapest_probe = min(self.probe_catalog.keys(), key=self.probe_catalog.get)
        outside_alert = (
            ~Interval([self.current_alert[0]])
            if self.current_alert[0] is not None
            else Interval([x for x, _ in self.alert_catalog])
        )
        ((b_left_point, _), (b_right_point, _)) = self.boundaries

        start = time()

        if self.turn == 0:
            # Send as many probes as possible
            self.departing_probes = [
                (self.probe_catalog[cheapest_probe], cheapest_probe, x)
                for x in range(0, 101)
            ]

        elif len((self.answer_intervals + (0, self.trajectory_speed)) & outside_alert) > 0:
            # Send as many probes as possible
            self.departing_probes = [
                (self.probe_catalog[cheapest_probe], cheapest_probe, x)
                for x in range(b_left_point, b_right_point + 1)
            ]

        end = time()
        #print('[' + self.name + '] ' + str(self.alert_cost) + ', ' + str(self.probe_cost) + ', ' + str(end - start))

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_lazy_algorithm',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.invoke_lazy_algorithm')
        ####################################################

        return self
############################################################










############################################################
    def invoke_lazy_with_randomness_algorithm(
            self
    ):
        ####################################################
        # Debug
        debug('Entering backend.DecisionSupportSystem.invoke_lazy_with_randomness_algorithm')
        ####################################################
        # Verbose
        info(
            msg=enter_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_lazy_with_randomness_algorithm',
                '',
                self
            )
        )
        ####################################################

        cheapest_probe = min(self.probe_catalog.keys(), key=self.probe_catalog.get)
        ((b_left_point, _), (b_right_point, _)) = self.boundaries

        start = time()

        if self.turn == 0:
            # Send as many probes as possible
            self.departing_probes = [
                (self.probe_catalog[cheapest_probe], cheapest_probe, x)
                for x in range(0, 101)
            ]

        else:

            self.departing_probes = [
                (self.probe_catalog[u], u, randint(b_left_point, b_right_point))
                for u in [choice(list(self.probe_catalog.keys()))]
                for _ in range(0, randint(0, b_right_point - b_left_point + 1))
            ]

        end = time()
        #print('[' + self.name + '] ' + str(self.alert_cost) + ', ' + str(self.probe_cost) + ', ' + str(end - start))

        ####################################################
        # Verbose
        info(
            msg=exit_info_format.format(
                datetime.now().isoformat(),
                'backend',
                self.__class__.__name__,
                'invoke_lazy_with_randomness_algorithm',
                self,
                ''
            )
        )
        ####################################################
        # Debug
        debug('Exiting backend.DecisionSupportSystem.invoke_lazy_with_randomness_algorithm')
        ####################################################

        return self
############################################################










############################################################
    def invoke_optimal_algorithm(
            self,

            world
    ):
        cheapest_probe = min(self.probe_catalog.keys(), key=self.probe_catalog.get)
        ((b_left_point, _), (b_right_point, _)) = world.boundaries

        start = time()

        if b_left_point <= world.position - cheapest_probe:
            left_probe_location = world.position - cheapest_probe
        elif world.position + cheapest_probe <= b_right_point:
            left_probe_location = world.position + cheapest_probe

        if b_left_point <= world.position - cheapest_probe:
            right_probe_location = world.position - cheapest_probe
        elif world.position + cheapest_probe <= b_right_point:
            right_probe_location = world.position + cheapest_probe

        self.departing_probes = [
            (self.probe_catalog[cheapest_probe], cheapest_probe, left_probe_location),
            (self.probe_catalog[cheapest_probe], cheapest_probe, right_probe_location)
        ]

        end = time()
        #print('[' + self.name + '] ' + str(self.alert_cost) + ', ' + str(self.probe_cost) + ', ' + str(end - start))
        return self
############################################################










############################################################
def search(
        parameters
):
    world = UncertainEnvironment(
        # Log
        name=parameters.name,

        # State
        boundaries=parameters.boundaries,
        trajectory=parameters.trajectory,
        initial_position=parameters.initial_position
    )

    dynamic_programming_system = DecisionSupportSystem(
        # Log
        name='dynamic_programming',

        # State
        alert_cost=0,
        probe_cost=0,
        answer_intervals=Interval([((0, False), (100, True))]),
        action_history=[],
        turn=0,

        # Parameters
        boundaries=parameters.boundaries,
        alert_catalog=parameters.alert_catalog,
        probe_success_rate_area=parameters.probe_success_rate_area,
        trajectory_speed=parameters.trajectory_speed,
        cost_table_quality=parameters.cost_table_quality,
        byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

        probe_catalog=parameters.probe_catalog
    )
    greedy_system = DecisionSupportSystem(
        # Log
        name='greedy',

        # State
        alert_cost=0,
        probe_cost=0,
        answer_intervals=Interval([((0, False), (100, True))]),
        action_history=[],
        turn=0,

        # Parameters
        boundaries=parameters.boundaries,
        alert_catalog=parameters.alert_catalog,
        probe_success_rate_area=parameters.probe_success_rate_area,
        trajectory_speed=parameters.trajectory_speed,
        cost_table_quality=parameters.cost_table_quality,
        byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

        probe_catalog=parameters.probe_catalog
    )
    lazy_system = DecisionSupportSystem(
        # Log
        name='lazy',

        # State
        alert_cost=0,
        probe_cost=0,
        answer_intervals=Interval([((0, False), (100, True))]),
        action_history=[],
        turn=0,

        # Parameters
        boundaries=parameters.boundaries,
        alert_catalog=parameters.alert_catalog,
        probe_success_rate_area=parameters.probe_success_rate_area,
        trajectory_speed=parameters.trajectory_speed,
        cost_table_quality=parameters.cost_table_quality,
        byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

        probe_catalog=parameters.probe_catalog
    )
    lazy_with_randomness_system = DecisionSupportSystem(
        # Log
        name='lazy_with_randomness',

        # State
        alert_cost=0,
        probe_cost=0,
        answer_intervals=Interval([((0, False), (100, True))]),
        action_history=[],
        turn=0,

        # Parameters
        boundaries=parameters.boundaries,
        alert_catalog=parameters.alert_catalog,
        probe_success_rate_area=parameters.probe_success_rate_area,
        trajectory_speed=parameters.trajectory_speed,
        cost_table_quality=parameters.cost_table_quality,
        byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

        probe_catalog=parameters.probe_catalog
    )
    optimal_system = DecisionSupportSystem(
        # Log
        name='optimal',

        # State
        alert_cost=0,
        probe_cost=0,
        answer_intervals=Interval([((0, False), (100, True))]),
        action_history=[],
        turn=0,

        # Parameters
        boundaries=parameters.boundaries,
        alert_catalog=parameters.alert_catalog,
        probe_success_rate_area=parameters.probe_success_rate_area,
        trajectory_speed=parameters.trajectory_speed,
        cost_table_quality=parameters.cost_table_quality,
        byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

        probe_catalog=parameters.probe_catalog
    )


    while True:
        # yield dynamic_programming_system.export_csv_content()

        # Full-fledged solution
        dynamic_programming_system\
            .import_measurements(
                source=dynamic_programming_system
            )\
            .invoke_inference_algorithm()\
            .invoke_dynamic_programming_algorithm()
        world\
            .import_probes(
                source=dynamic_programming_system
            )

        # Strawman 1
        greedy_system\
            .import_measurements(
                source=dynamic_programming_system
            )\
            .invoke_inference_algorithm()\
            .invoke_greedy_algorithm()
        world\
            .import_probes(
                source=greedy_system
            )

        # Strawman 2
        lazy_system\
            .import_measurements(
                source=dynamic_programming_system
            )\
            .invoke_inference_algorithm()\
            .invoke_lazy_algorithm()
        world\
            .import_probes(
                source=lazy_system
            )

        # Strawman 3
        lazy_with_randomness_system\
            .import_measurements(
                source=dynamic_programming_system
            )\
            .invoke_inference_algorithm()\
            .invoke_lazy_with_randomness_algorithm()
        world\
            .import_probes(
                source=lazy_with_randomness_system
            )

        # Strawman 4 - Baseline
        optimal_system\
            .import_measurements(
                source=dynamic_programming_system
            )\
            .invoke_inference_algorithm()\
            .invoke_optimal_algorithm(
                world)
        world\
            .import_probes(
                source=lazy_system
            )

        # yield dynamic_programming_system.export_csv_content()

        # Go to next unit time.
        world\
            .wait(
                unit_time=1
            )
        dynamic_programming_system\
            .wait(
                unit_time=1
            )
        greedy_system\
            .wait(
                unit_time=1
            )
        lazy_system\
            .wait(
                unit_time=1
            )
        lazy_with_randomness_system\
            .wait(
                unit_time=1
            )
        optimal_system\
            .wait(
                unit_time=1
            )