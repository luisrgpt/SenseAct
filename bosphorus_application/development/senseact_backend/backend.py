from senseact_evaluation import evaluate
from ast import literal_eval
import csv
from senseact_math import Interval
from time import strftime, time
from math import log2
from datetime import datetime
from logging import basicConfig, INFO, debug, info

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
    self.position = initial_position

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
        (float(location), float(imprecision), cost,
         abs(location - self.position) <= imprecision, False)
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

    source.sensor_cost += sum(x for x, _, _ in source.departing_probes)
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
      sensor_cost,
      incident_intervals,
      action_history,
      turn,

      # Parameters
      boundaries,
      alert_settings,
      sensor_success_rate_area,
      target_settings,
      cost_table_quality,
      byzantine_fault_tolerance,

      sensor_settings
  ):
    # Log
    self.name = name

    # State
    self.alert_cost = alert_cost
    self.sensor_cost = sensor_cost
    self.incident_intervals = incident_intervals
    self.action_history = action_history
    self.turn = turn

    # Parameters
    self.boundaries = boundaries
    self.alert_settings = alert_settings
    self.sensor_success_rate_area = sensor_success_rate_area
    self.target_settings = target_settings
    self.cost_table_quality = cost_table_quality
    self.byzantine_fault_tolerance = byzantine_fault_tolerance

    # self.graph: Graph = Graph(
    #         node=Node(
    #             label=str(incident_intervals)
    #         )
    #     )
    # if self.name == "dynamic_programming":
    #     self.graph.export_png(
    #         directory='./log',
    #         filename=str(self.turn) + '_00_start_' + self.name
    #     )
    self.departing_probes = []
    n_boundaries = boundaries[1][0] - boundaries[0][0]
    self.boundaries_distribution = [1 / n_boundaries] * n_boundaries
    self.sensor_settings = sensor_settings
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
    sensor_cost:                {2}
    incident_intervals:          '{3}'
    action_history:
    turn:          {4}
    boundaries:                '{5}'
    alert_settings:
    sensor_success_rate_area:
    target_settings:
    cost_table_quality:
    byzantine_fault_tolerance: {6}
    graph:
    departing_probes:
    boundaries_distribution:
    sensor_settings:""".format(
      self.name,
      self.alert_cost,
      self.sensor_cost,
      self.incident_intervals,
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
    csv_content += [self.alert_cost + self.sensor_cost]
    csv_content += [self.incident_intervals]

    # Info 2: Environment
    csv_content += [1234]
    csv_content += [self.turn]

    # Info 3: Graph
    # csv_content += [self.graph.export_png(
    #     directory='../../borphorus_interface/user_interface_1_wpf/bin/x64/Debug/AppX',
    #     filename=str(time.strftime('%Y_%m_%d_%H_%M_%S'))
    # )]
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
            ((location - imprecision - decay, True),
             (location + imprecision + decay, False))
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
    for incident_intervals_yes in self.incident_intervals:
      for x, cost in self.alert_settings:
        if alert_cost < cost and \
            (
            incident_intervals_yes if x[1] <= incident_intervals_yes[1] else x)[
              0] < \
            (
            incident_intervals_yes if incident_intervals_yes[0] <= x[0] else x)[
              1]:
          alert_cost = cost
          self.current_alert = (x, cost)
    self.alert_cost += alert_cost

    # ... while every measurement gets less accurate...
    snapshot = Interval(self.incident_intervals[:])
    self.incident_intervals += (0, self.target_settings)
    self.incident_intervals &= Interval([self.boundaries])
    # self.graph += [
    #     Hyperedge(
    #         sources=[Interval([source]) for source in snapshot if Interval([source]) in Interval([target])],
    #         targets=[Interval([target])],
    #         weight=0,
    #         label='Wait'
    #     ) for target in self.incident_intervals
    # ]
    # if self.name == "dynamic_programming":
    #     self.graph.export_png(
    #         directory='./log',
    #         filename=str(self.turn) + '_01_wait_' + self.name
    #     )

    # ... or even useless, some minutes after being obtained.
    for timestamp, batch in enumerate(self.action_history):
      if not batch:
        continue
      decay = (self.turn - timestamp) * self.target_settings
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

    if self.name in source.measurements and len(
        source.measurements[self.name]) > 0:
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
      snapshot = Interval(self.incident_intervals[:])

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
      self.incident_intervals &= current_answer_interval

      # Solution 2: Update state
      # self.graph += [
      #     Hyperedge(
      #         sources=[Interval([source])],
      #         targets=[Interval([target]) for target in self.incident_intervals if Interval([target]) in Interval([self.measurements])],
      #         weight=self.alert_cost + self.sensor_cost,
      #         label=str([(location, imprecision, does_detect) for location, imprecision, _, does_detect, _ in self.measurements])
      #     ) for source in snapshot
      # ]
      # if self.name == "dynamic_programming":
      #     self.graph.export_png(
      #         directory='./log',
      #         filename=str(self.turn) + '_02_sensor_' + self.name
      #     )
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
    debug(
      'Entering backend.DecisionSupportSystem.invoke_dynamic_programming_algorithm')
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
    new_boundaries_distribution = [0.0] * n_dist
    an_half = self.boundaries_distribution[0] / 2.0
    new_boundaries_distribution[0] += self.boundaries_distribution[0] - an_half
    new_boundaries_distribution[1] += an_half
    for x in range(1, n_dist - 1):
      a_third = self.boundaries_distribution[x] / 3.0
      new_boundaries_distribution[x - 1] += a_third
      new_boundaries_distribution[x] += self.boundaries_distribution[
                                          x] - a_third - a_third
      new_boundaries_distribution[x + 1] += a_third
    an_half = self.boundaries_distribution[-1] / 2.0
    new_boundaries_distribution[-2] += an_half
    new_boundaries_distribution[-1] += self.boundaries_distribution[
                                         -1] - an_half
    self.boundaries_distribution = new_boundaries_distribution

    # Step 2: Crop probabilistic distribution
    total_pb = 0.0
    total = 0
    for x in range(n_dist):
      if Interval([((x, True), (x + 1, False))]) in self.incident_intervals:
        total_pb += self.boundaries_distribution[x]
        total += 1
      else:
        self.boundaries_distribution[x] = 0
    current_total = total_pb
    # Step 2.a: First adjustment
    total_pb = 0.0
    for x in range(n_dist):
      if Interval([((x, True), (x + 1, False))]) in self.incident_intervals:
        self.boundaries_distribution[x] /= current_total
        total_pb += self.boundaries_distribution[x]
    current_total = total_pb
    # Step 2.b: Second adjustment
    if current_total != 1.0:
      for x in range(n_dist):
        if Interval([((x, True), (x + 1, False))]) in self.incident_intervals:
          self.boundaries_distribution[x] += 1 - current_total
          current_total += 1 - current_total
          break

    # Step 3: Pick the best set of probes for each disjunction
    best_comb = []
    for incident_intervals in self.incident_intervals:
      best_comb += [min(
        self.cost_table[self.cost_table_quality, incident_intervals],
        key=lambda x:
        evaluate(
          time=self.cost_table_quality,
          cost_table=self.cost_table,
          boundaries=self.boundaries,
          alert_settings=self.alert_settings,
          target_settings=self.target_settings,
          nucleus=x[0],
          sensor_settings=self.sensor_settings,

          sensor_success_rate_area=self.sensor_success_rate_area,
          byzantine_fault_tolerance=self.byzantine_fault_tolerance,

          boundaries_distributions=[self.boundaries_distribution],

          incident_intervals=[incident_intervals],

          convert=False
        )[0]
      )[0]]

    # Step 4: Prepare probe information
    self.departing_probes = [
      (self.sensor_settings[u], u, pos)
      for x in best_comb
      for u, comb in x
      for pos in comb
    ]

    end = time()
    if self.turn is 0 or log2(self.turn) % 1 == 0:
      with open('../share/' + self.name + '_' + str(self.turn) + '.csv',
                'a') as file:
        csv \
          .writer(
          file,
          escapechar='\\',
          lineterminator='\n',
          quoting=csv.QUOTE_NONE
        ) \
          .writerow(
          [
            repr(self.incident_intervals),
            self.alert_cost,
            self.sensor_cost,
            end - start
          ]
        )

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
    debug(
      'Exiting backend.DecisionSupportSystem.invoke_dynamic_programming_algorithm')
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

    cheapest_probe = min(self.sensor_settings.keys(),
                         key=self.sensor_settings.get)
    ((a_left_point, _), (a_right_point, _)) = self.incident_intervals[0]
    ((b_left_point, _), (b_right_point, _)) = self.boundaries

    start = time()

    if self.turn == 0:
      # Step 1: Send as many probes as possible
      self.departing_probes = [
        (self.sensor_settings[cheapest_probe], cheapest_probe, x)
        for x in range(0, 101)
      ]

    else:
      # Step 2: Keep the knowledge space size
      if b_left_point <= a_left_point - cheapest_probe:
        left_sensor_location = a_left_point - cheapest_probe
      elif a_left_point + cheapest_probe <= b_right_point:
        left_sensor_location = a_left_point + cheapest_probe

      if b_left_point <= a_right_point - cheapest_probe:
        right_sensor_location = a_right_point - cheapest_probe
      elif a_right_point + cheapest_probe <= b_right_point:
        right_sensor_location = a_right_point + cheapest_probe

      self.departing_probes = [
        (self.sensor_settings[cheapest_probe], cheapest_probe,
         left_sensor_location),
        (self.sensor_settings[cheapest_probe], cheapest_probe,
         right_sensor_location)
      ]

    end = time()
    if self.turn is 0 or log2(self.turn) % 1 == 0:
      with open('../share/' + self.name + '_' + str(self.turn) + '.csv',
                'a') as file:
        csv \
          .writer(
          file,
          escapechar='\\',
          lineterminator='\n',
          quoting=csv.QUOTE_NONE
        ) \
          .writerow(
          [
            repr(self.incident_intervals),
            self.alert_cost,
            self.sensor_cost,
            end - start
          ]
        )

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

    cheapest_probe = min(self.sensor_settings.keys(),
                         key=self.sensor_settings.get)
    outside_alert = (
      ~Interval([self.current_alert[0]])
      if self.current_alert[0] is not None
      else Interval([x for x, _ in self.alert_settings])
    )
    ((a_left_point, _), (a_right_point, _)) = self.incident_intervals[0]

    start = time()

    if self.turn == 0:
      # Step 1: Send as many probes as possible
      self.departing_probes = [
        (self.sensor_settings[cheapest_probe], cheapest_probe, x)
        for x in range(0, 101)
      ]

    elif len((self.incident_intervals + (
        0, self.target_settings)) & outside_alert) > 0:
      # Step 2: Send as many probes as possible after a certain period of time
      self.departing_probes = [
        (self.sensor_settings[cheapest_probe], cheapest_probe, x)
        for x in range(int(a_left_point), int(a_right_point) + 1)
      ]

    end = time()
    if self.turn is 0 or log2(self.turn) % 1 == 0:
      with open('../share/' + self.name + '_' + str(self.turn) + '.csv',
                'a') as file:
        csv \
          .writer(
          file,
          escapechar='\\',
          lineterminator='\n',
          quoting=csv.QUOTE_NONE
        ) \
          .writerow(
          [
            repr(self.incident_intervals),
            self.alert_cost,
            self.sensor_cost,
            end - start
          ]
        )

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

  # ############################################################
  #     def invoke_lazy_with_randomness_algorithm(
  #             self
  #     ):
  #         ####################################################
  #         # Debug
  #         debug('Entering backend.DecisionSupportSystem.invoke_lazy_with_randomness_algorithm')
  #         ####################################################
  #         # Verbose
  #         info(
  #             msg=enter_info_format.format(
  #                 datetime.now().isoformat(),
  #                 'backend',
  #                 self.__class__.__name__,
  #                 'invoke_lazy_with_randomness_algorithm',
  #                 '',
  #                 self
  #             )
  #         )
  #         ####################################################
  #
  #         cheapest_probe = min(self.sensor_settings.keys(), key=self.sensor_settings.get)
  #         ((b_left_point, _), (b_right_point, _)) = self.boundaries
  #
  #         start = time()
  #
  #         if self.turn == 0:
  #             # Send as many probes as possible
  #             self.departing_probes = [
  #                 (self.sensor_settings[cheapest_probe], cheapest_probe, x)
  #                 for x in range(0, 101)
  #             ]
  #
  #         else:
  #
  #             self.departing_probes = [
  #                 (self.sensor_settings[u], u, randint(b_left_point, b_right_point))
  #                 for u in [choice(list(self.sensor_settings.keys()))]
  #                 for _ in range(0, randint(0, b_right_point - b_left_point + 1))
  #             ]
  #
  #         end = time()
  #         if self.turn is 0 or log2(self.turn) % 1 == 0:
  #             with open('../share/' + self.name + '_' + str(self.turn) + '.csv', 'a') as file:
  #                 csv\
  #                     .writer(
  #                         file,
  #                         escapechar='\\',
  #                         lineterminator='\n',
  #                         quoting=csv.QUOTE_NONE
  #                     )\
  #                     .writerow(
  #                         [
  #                             repr(self.incident_intervals),
  #                             self.alert_cost,
  #                             self.sensor_cost,
  #                             end - start
  #                         ]
  #                     )
  #
  #         ####################################################
  #         # Verbose
  #         info(
  #             msg=exit_info_format.format(
  #                 datetime.now().isoformat(),
  #                 'backend',
  #                 self.__class__.__name__,
  #                 'invoke_lazy_with_randomness_algorithm',
  #                 self,
  #                 ''
  #             )
  #         )
  #         ####################################################
  #         # Debug
  #         debug('Exiting backend.DecisionSupportSystem.invoke_lazy_with_randomness_algorithm')
  #         ####################################################
  #
  #         return self
  # ############################################################

  ############################################################
  def invoke_optimal_algorithm(
      self,

      oracle
  ):
    cheapest_probe = min(self.sensor_settings.keys(),
                         key=self.sensor_settings.get)
    ((b_left_point, _), (b_right_point, _)) = oracle.boundaries

    start = time()

    if b_left_point <= oracle.position - cheapest_probe:
      left_sensor_location = oracle.position - cheapest_probe
    elif oracle.position + cheapest_probe <= b_right_point:
      left_sensor_location = oracle.position + cheapest_probe

    if b_left_point <= oracle.position - cheapest_probe:
      right_sensor_location = oracle.position - cheapest_probe
    elif oracle.position + cheapest_probe <= b_right_point:
      right_sensor_location = oracle.position + cheapest_probe

    self.departing_probes = [
      (self.sensor_settings[cheapest_probe], cheapest_probe,
       left_sensor_location),
      (self.sensor_settings[cheapest_probe], cheapest_probe,
       right_sensor_location)
    ]

    end = time()
    if self.turn is 0 or log2(self.turn) % 1 == 0:
      with open('../share/' + self.name + '_' + str(self.turn) + '.csv',
                'a') as file:
        csv \
          .writer(
          file,
          escapechar='\\',
          lineterminator='\n',
          quoting=csv.QUOTE_NONE
        ) \
          .writerow(
          [
            repr(self.incident_intervals),
            self.alert_cost,
            self.sensor_cost,
            end - start
          ]
        )

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
    sensor_cost=0,
    incident_intervals=Interval([((0, False), (100, True))]),
    action_history=[],
    turn=0,

    # Parameters
    boundaries=parameters.boundaries,
    alert_settings=parameters.alert_settings,
    sensor_success_rate_area=parameters.sensor_success_rate_area,
    target_settings=parameters.target_settings,
    cost_table_quality=parameters.cost_table_quality,
    byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

    sensor_settings=parameters.sensor_settings
  )
  greedy_system = DecisionSupportSystem(
    # Log
    name='greedy',

    # State
    alert_cost=0,
    sensor_cost=0,
    incident_intervals=Interval([((0, False), (100, True))]),
    action_history=[],
    turn=0,

    # Parameters
    boundaries=parameters.boundaries,
    alert_settings=parameters.alert_settings,
    sensor_success_rate_area=parameters.sensor_success_rate_area,
    target_settings=parameters.target_settings,
    cost_table_quality=parameters.cost_table_quality,
    byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

    sensor_settings=parameters.sensor_settings
  )
  lazy_system = DecisionSupportSystem(
    # Log
    name='lazy',

    # State
    alert_cost=0,
    sensor_cost=0,
    incident_intervals=Interval([((0, False), (100, True))]),
    action_history=[],
    turn=0,

    # Parameters
    boundaries=parameters.boundaries,
    alert_settings=parameters.alert_settings,
    sensor_success_rate_area=parameters.sensor_success_rate_area,
    target_settings=parameters.target_settings,
    cost_table_quality=parameters.cost_table_quality,
    byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

    sensor_settings=parameters.sensor_settings
  )
  # lazy_with_randomness_system = DecisionSupportSystem(
  #     # Log
  #     name='lazy_with_randomness',
  #
  #     # State
  #     alert_cost=0,
  #     sensor_cost=0,
  #     incident_intervals=Interval([((0, False), (100, True))]),
  #     action_history=[],
  #     turn=0,
  #
  #     # Parameters
  #     boundaries=parameters.boundaries,
  #     alert_settings=parameters.alert_settings,
  #     sensor_success_rate_area=parameters.sensor_success_rate_area,
  #     target_settings=parameters.target_settings,
  #     cost_table_quality=parameters.cost_table_quality,
  #     byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,
  #
  #     sensor_settings=parameters.sensor_settings
  # )
  optimal_system = DecisionSupportSystem(
    # Log
    name='optimal',

    # State
    alert_cost=0,
    sensor_cost=0,
    incident_intervals=Interval([((0, False), (100, True))]),
    action_history=[],
    turn=0,

    # Parameters
    boundaries=parameters.boundaries,
    alert_settings=parameters.alert_settings,
    sensor_success_rate_area=parameters.sensor_success_rate_area,
    target_settings=parameters.target_settings,
    cost_table_quality=parameters.cost_table_quality,
    byzantine_fault_tolerance=parameters.byzantine_fault_tolerance,

    sensor_settings=parameters.sensor_settings
  )

  for _ in range(0, parameters.time_limit):
    # yield dynamic_programming_system.export_csv_content()

    # Full-fledged solution
    dynamic_programming_system \
      .import_measurements(
      source=world
    ) \
      .invoke_inference_algorithm() \
      .invoke_dynamic_programming_algorithm()
    world \
      .import_probes(
      source=dynamic_programming_system
    )

    # Strawman 1
    greedy_system \
      .import_measurements(
      source=world
    ) \
      .invoke_inference_algorithm() \
      .invoke_greedy_algorithm()
    world \
      .import_probes(
      source=greedy_system
    )

    # Strawman 2
    lazy_system \
      .import_measurements(
      source=world
    ) \
      .invoke_inference_algorithm() \
      .invoke_lazy_algorithm()
    world \
      .import_probes(
      source=lazy_system
    )

    # # Strawman 3
    # lazy_with_randomness_system\
    #     .import_measurements(
    #         source=world
    #     )\
    #     .invoke_inference_algorithm()\
    #     .invoke_lazy_with_randomness_algorithm()
    # world\
    #     .import_probes(
    #         source=lazy_with_randomness_system
    #     )

    # Strawman 4 - Baseline
    optimal_system \
      .import_measurements(
      source=world
    ) \
      .invoke_inference_algorithm() \
      .invoke_optimal_algorithm(
      oracle=world
    )
    world \
      .import_probes(
      source=lazy_system
    )

    # yield dynamic_programming_system.export_csv_content()

    # Go to next unit time.
    world \
      .wait(
      unit_time=1
    )
    dynamic_programming_system \
      .wait(
      unit_time=1
    )
    greedy_system \
      .wait(
      unit_time=1
    )
    lazy_system \
      .wait(
      unit_time=1
    )
    # lazy_with_randomness_system\
    #     .wait(
    #         unit_time=1
    #     )
    optimal_system \
      .wait(
      unit_time=1
    )
