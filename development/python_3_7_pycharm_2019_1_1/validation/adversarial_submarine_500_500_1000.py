import csv
import time
from itertools import repeat
from os.path import realpath
from socket import getfqdn

from senseact.dynamic_programming import \
  build
from senseact.agents import \
  SenseActAgent, \
  GreedyAgent, \
  LazyAgent, \
  OptimalAgent
from senseact.environments import \
  EmergentAndUncertainEnvironment

machine = getfqdn()

path_prefix = realpath(__file__).replace('.py', '') + str(time.time())

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
          (45.0, 70.0),
          500,
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

print('Executing learning component:')

cost_table, global_performance_table = build(
  settings=settings,
)

print('Executing learning component... OK!')

print('Storing learning component results... ', end='')

with open(path_prefix + '_learning_element_performance.csv', 'w') as file:
  writer = csv.writer(
    file,
    lineterminator='\n',
  )
  for time, duration in global_performance_table:
    writer.writerow((machine, time, duration))

with open(path_prefix + '_cost_table.csv', 'w') as file:
  writer = csv.writer(
    file,
    escapechar='\\',
    lineterminator='\n',
    delimiter=';',
    quoting=csv.QUOTE_NONE
  )
  for time, row_group in sorted(cost_table.items(), key=lambda x: x[0]):
    for (minimum, maximum), row_value in sorted(row_group.items(), key=lambda x: x[0]):
      writer.writerow((
        time,
        minimum,
        maximum,
        {
          tuple(position for position, condition in enumerate(batch) if condition): cost
          for batch, cost in row_value.items()
        },
      ))

with open(path_prefix + '_cost_table_human_readable.csv', 'w') as file:
  writer = csv.writer(
    file,
    escapechar='\\',
    lineterminator='\n',
    delimiter=';',
    quoting=csv.QUOTE_NONE
  )
  for time, row_group in sorted(cost_table.items(), key=lambda x: x[0]):
    for (minimum, maximum), row_value in sorted(row_group.items(), key=lambda x: x[0]):
      chromosome_types = [
        y
        for x in (5,)
        for y in repeat(x, 101)
      ]

      if len(row_value) > 1:
        writer.writerow((
          (time, minimum, maximum),
          [
            (
              [
                (radius, (position - 1) % 100)
                for position, (condition, radius) in enumerate(zip(batch, chromosome_types)) if condition
              ],
              cost,
            )
            for batch, cost in sorted(row_value.items(), key=lambda x: x[1])
          ]
        ))

print('OK!')

print('Executing decision component... ', end='')

global_performance_table = []
global_quality_table = []

for _ in range(0, 100):

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
    for agent, time, interval, alert_cost, probe_cost in quality_table:
      writer.writerow((machine, instance, agent, time, interval, alert_cost, probe_cost))

print('OK!')
