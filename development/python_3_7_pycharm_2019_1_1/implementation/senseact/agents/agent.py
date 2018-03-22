import csv
from time import strftime

from senseact.math import Interval

class Agent:

  def __init__(
      self,
      name,
      settings
  ):
    # Log
    self.name = name

    # State
    self.alert_cost = 0
    self.probe_cost = 0
    self.incident_intervals = Interval([((0, False), (100, True))])
    self.measurements = {}
    self.turn = 0

    # Parameters
    self.settings = settings

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
    self.departing_batch = ()
    self.departed_batch = ()
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
    incident_intervals:          '{3}'
    measurements:
    turn:          {4}
    boundaries:                '{5}'
    alert_settings:
    probe_success_rate_area:
    target_settings:
    cost_table_quality:
    byzantine_fault_tolerance: {6}
    graph:
    departing_batch:
    boundaries_distribution:
    probe_settings:""".format(
      self.name,
      self.alert_cost,
      self.probe_cost,
      self.incident_intervals,
      self.turn,
      self.settings['boundaries'],
      self.settings['byzantine_fault_tolerance']
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
    for timestamp, batch in enumerate(self.measurements, start=1):
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

    # As time passes...
    self.turn += 1

    # ... treatments are being applied based on knowledge represented as intervals,...
    self.current_alert = next(
      ((alert_minimum, alert_maximum), alert_cost)
      for (alert_minimum, alert_maximum), alert_cost in self.settings['alert']['types']
      for ((minimum, _), (maximum, _)) in self.incident_intervals
      if (minimum == maximum and minimum <= alert_maximum and alert_minimum <= maximum)
      or (minimum < alert_maximum and alert_minimum < maximum)
    )
    self.alert_cost += self.current_alert[1]

    # ... while every measurement gets less accurate...
    snapshot = Interval(self.incident_intervals[:])
    self.incident_intervals += (0, self.settings['target']['speed'])
    self.incident_intervals &= Interval([((self.settings['boundaries'][0], False), (self.settings['boundaries'][1], True))])
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

    # ... and eventually useless.
    for timestamp, batch in self.measurements.items():
      if not batch:
        continue
      decay = (self.turn - timestamp) * self.settings['target']['speed']
      for index, probe in enumerate(batch):
        if not probe:
          continue
        location, imprecision, _, does_detect, _ = probe
        upper_margin = self.settings['boundaries'][1] - imprecision - decay
        lower_margin = self.settings['boundaries'][0] + imprecision + decay
        useless_yes = does_detect and upper_margin < location < lower_margin
        useless_no = not does_detect and decay >= imprecision
        if useless_yes or useless_no:
          batch[index] = None
          continue

    return self.name, self.turn, repr(snapshot), self.alert_cost, self.probe_cost, self.departed_batch

  ############################################################

  ############################################################
  def import_measurements(
      self,
      source
  ):

    self.measurements.setdefault(self.turn, [])
    if self.name in source.measurements and len(source.measurements[self.name]) > 0:
      self.measurements[self.turn] += source.measurements[self.name]
      del source.measurements[self.name]

    return self

  ############################################################

  ############################################################
  def invoke_inference_algorithm(
      self
  ):

    if self.measurements[self.turn]:
      # Solution 1: Generate result
      snapshot = Interval(self.incident_intervals[:])

      lower_boundaries, upper_boundaries = self.settings['boundaries']
      for location, imprecision, _, does_detect, _ in self.measurements[self.turn]:

        current_answer_interval = Interval([])
        if does_detect:
          current_answer_interval.intervals += [
            ((max(lower_boundaries, location - imprecision), False), (min(location + imprecision, upper_boundaries), True)),
          ]

        else:
          if lower_boundaries < location - imprecision :
            current_answer_interval.intervals += [
              ((lower_boundaries, False), (location - imprecision, False)),
            ]

          if location + imprecision < upper_boundaries:
            current_answer_interval.intervals += [
              ((location + imprecision, True), (upper_boundaries, True)),
            ]

        self.incident_intervals &= current_answer_interval

      # Solution 2: Update state
      # self.graph += [
      #     Hyperedge(
      #         sources=[Interval([source])],
      #         targets=[Interval([target]) for target in self.incident_intervals if Interval([target]) in Interval([self.measurements])],
      #         weight=self.alert_cost + self.probe_cost,
      #         label=str([(location, imprecision, does_detect) for location, imprecision, _, does_detect, _ in self.measurements])
      #     ) for source in snapshot
      # ]
      # if self.name == "dynamic_programming":
      #     self.graph.export_png(
      #         directory='./log',
      #         filename=str(self.turn) + '_02_probe_' + self.name
      #     )

    return self
