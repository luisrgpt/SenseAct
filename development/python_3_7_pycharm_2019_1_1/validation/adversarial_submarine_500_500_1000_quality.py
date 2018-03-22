from ast import \
  literal_eval
from re import match
import csv
import time
from itertools import repeat
from os.path import basename
from os import listdir
from socket import getfqdn

from senseact.agents import \
  SenseActAgent, \
  GreedyAgent, \
  LazyAgent, \
  OptimalAgent
from senseact.environments import \
  EmergentAndUncertainEnvironment

machine = getfqdn()

settings = {
  'genetic_algorithm': {
    'generate': {
      'chromosome': {
        'types': {
          5: 1,
        }
      },
      'population': {
        'size_ratio': 0.5,
        'elite_size': 5,
        'saved_size': 2,
      }
    },
    'select': {
      'base_logarithm': 2,
    },
    'crossover': {
      'probability': 0.1,
    },
    'mutate': {
      'probability': 0.1,
      'flip_probability': 0.1,
    },
    'stopping_condition': 4,
  },
  'scenario': {
    'alert': {
      'types': [
        (
          (40.0, 45.0),
          1000,
        ),
        (
          (45.0, 45.0),
          500,
        ),
        (
          (45.0, 70.0),
          500,
        ),
        (
          (40.0, 40.0),
          0,
        ),
        (
          (70.0, 70.0),
          0,
        ),
        (
          (0.0, 40.0),
          0,
        ),
        (
          (45.0, 45.0),
          0,
        ),
        (
          (70.0, 100),
          0,
        ),
      ]
    },
    'boundaries': (0.0, 100.0),
    'byzantine_fault_tolerance': 1,
    'scale': 1,
    'probe': {
      'types': {
        5: 500,
      },
    },
    'target': {
      'speed': 1,
    },
    'time': 100,
  },
}

for path_prefix in (
  x
  for x in listdir("./")
  if match(basename(__file__).replace('_quality.py', '') + ".*_cost_table\.csv", x)
):

  cost_table = {}
  for n in range(0, 101):
    cost_table[n] = {}

  print('Loading cost table from ' + path_prefix + "...")

  with open(path_prefix, 'r') as file:
    reader = csv.reader(
      file,
      escapechar='\\',
      lineterminator='\n',
      delimiter=';',
      quoting=csv.QUOTE_NONE
    )

    current_time = None
    for time, minimum, maximum, batches in reader:
      if time != current_time:
        print(time)
        current_time = time
      time = int(time)
      minimum = float(minimum)
      maximum = float(maximum)
      batches = literal_eval(batches)

      cost_table[time][minimum, maximum] = {}
      for batch, cost in batches.items():
        if len(batch) > 0:
          batch = tuple(n in batch for n in range(0, 101))
        cost_table[time][minimum, maximum][batch] = cost

  print('Executing decision component... ', end='')

  global_performance_table = []
  global_quality_table = []

  for x in range(0, 100):
    print(x)
    world = EmergentAndUncertainEnvironment(
      settings=settings['scenario'],
    )

    senseact_agent = SenseActAgent(
      settings=settings['scenario'],
    )
    greedy_agent = GreedyAgent(
      settings=settings['scenario'],
    )
    lazy_agent = LazyAgent(
      settings=settings['scenario'],
    )
    optimal_agent = OptimalAgent(
      settings=settings['scenario'],
    )

    performance_table = []
    quality_table = []

    for _ in range(0, settings['scenario']['time']):
      # SenseAct
      performance_table += [senseact_agent.invoke_senseact_algorithm(
        cost_table=cost_table,
      )]
      world.import_batch(
        source=senseact_agent
      )
      senseact_agent.import_measurements(
        source=world
      ).invoke_inference_algorithm()

      # Strawman 1
      performance_table += [greedy_agent.invoke_greedy_algorithm()]
      world.import_batch(
        source=greedy_agent
      )
      greedy_agent.import_measurements(
        source=world
      ).invoke_inference_algorithm()

      # Strawman 2
      performance_table += [lazy_agent.invoke_lazy_algorithm()]
      world.import_batch(
        source=lazy_agent
      )
      lazy_agent.import_measurements(
        source=world
      ).invoke_inference_algorithm()

      # Strawman 3 - Baseline
      performance_table += [optimal_agent.invoke_optimal_algorithm(
        oracle=world
      )]
      world.import_batch(
        source=optimal_agent
      )
      optimal_agent.import_measurements(
        source=world
      ).invoke_inference_algorithm()

      # Go to next unit time.
      world.wait(
        unit_time=1
      )
      quality_table += [
        senseact_agent.wait(
          unit_time=1
        ),
        greedy_agent.wait(
          unit_time=1
        ),
        lazy_agent.wait(
          unit_time=1
        ),
        optimal_agent.wait(
          unit_time=1
        ),
      ]

    global_performance_table += [
      performance_table,
    ]
    global_quality_table += [
      quality_table,
    ]

  print('OK!')

  print('Storing decision component results... ', end='')

  path_prefix = path_prefix.replace("_cost_table.csv", "")

  with open(path_prefix + '_decision_element_performance.csv', 'w') as file:
    writer = csv.writer(
      file,
      lineterminator='\n',
    )
    for instance, performance_table in enumerate(global_performance_table):
      for agent, time, duration in performance_table:
        writer.writerow((machine, instance, agent, time, duration))

  with open(path_prefix + '_decision_element_quality.csv', 'w') as file:
    writer = csv.writer(
      file,
      escapechar='\\',
      lineterminator='\n',
      quoting=csv.QUOTE_NONE
    )
    for instance, quality_table in enumerate(global_quality_table):
      for agent, time, interval, alert_cost, probe_cost, batch in quality_table:
        writer.writerow((machine, instance, agent, time, interval, alert_cost, probe_cost, batch))

  print('OK!')
