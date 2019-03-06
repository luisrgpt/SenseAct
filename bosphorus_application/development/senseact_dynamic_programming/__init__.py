from .store import store

from senseact_math import Interval, intersects
from math import inf
import time as timer
import csv
from senseact_genetic_algorithm import search

############################################################


############################################################
def extrapolate(
    incident_intervals: tuple,
    excluded: list,
    partitions: list
):
  (a_left, a_right) = incident_intervals
  ((a_lower, _), (a_upper, _)) = incident_intervals
  i_incident_intervals = Interval([incident_intervals])

  alert_cost = inf
  useless_range = []
  for ((x_lower, _), (x_upper, _)), cost in partitions:
    x = ((x_lower, True), (x_upper, False))
    if cost < alert_cost and intersects(incident_intervals, x):
      alert_cost = cost
      useless_range = [x]
    elif cost == alert_cost:
      useless_range += [x]
  useless_range = Interval(useless_range)
  # print(str((a_lower, a_upper)) + ' -> ' + str(useless_range))

  incident_intervals = []
  if len(useless_range) is 0:
    incident_intervals += [incident_intervals]

  else:
    i_incident_intervals &= ~useless_range
    i_incident_intervals = i_incident_intervals[0]
    ((i_a_lower, i_a_open), (i_a_upper, i_a_closed)) = i_incident_intervals

    if i_a_upper == a_upper:
      s_left = (i_a_lower - 1, True)
      while a_left <= s_left:
        s_incident_intervals = (s_left, a_right)
        if s_incident_intervals not in excluded:
          incident_intervals += [s_incident_intervals]
        (s_lower, s_open) = s_left
        s_left = (s_lower - (not s_open), not s_open)

    elif a_lower == i_a_lower:
      s_right = (i_a_upper + 1, False)
      while s_right <= a_right:
        s_incident_intervals = (a_left, s_right)
        if s_incident_intervals not in excluded:
          incident_intervals += [s_incident_intervals]
        (s_upper, s_closed) = s_right
        s_right = (s_upper + s_closed, not s_closed)

    else:
      s_right = (i_a_upper + 1, False)
      while s_right <= a_right:
        s_left = (i_a_lower - 1, True)
        while a_left <= s_left:
          s_incident_intervals = (s_left, s_right)
          if s_incident_intervals not in excluded:
            incident_intervals += [s_incident_intervals]
          (s_lower, s_open) = s_left
          s_left = (s_lower - (not s_open), not s_open)
        (s_upper, s_closed) = s_right
        s_right = (s_upper + s_closed, not s_closed)

  return incident_intervals

############################################################


############################################################
def multi_search(
    k_incident_intervals: list,
    l_incident_intervals: dict,
    time: int,
    cost_table: dict,
    population_size: int,
    population_elite_size: int,
    population_saved_size: int,
    boundaries: tuple,
    alert_settings: list,
    target_settings: float,
    mutate_probability_of_flipping_bit: float,
    stopping_condition: float,
    nucleus_settings: list,
    sensor_settings: dict,

    select_base_logarithm: float,
    crossover_probability: float,
    mutate_probability_of_mutate: float,

    sensor_success_rate_area: dict,
    byzantine_fault_tolerance: int
):
  population_elite = []

  for x in k_incident_intervals:
    # print(str(x) + ' -> ' + str(l_incident_intervals[x][0]))
    t_incident_intervals = (x, l_incident_intervals[x])
    search(
      time=time,
      t_incident_intervals=t_incident_intervals,
      cost_table=cost_table,
      population_size=population_size,
      population_elite_size=population_elite_size,
      population_saved_size=population_saved_size,
      boundaries=boundaries,
      alert_settings=alert_settings,
      target_settings=target_settings,
      stopping_condition=stopping_condition,
      mutate_probability_of_flipping_bit=mutate_probability_of_flipping_bit,
      nucleus_settings=nucleus_settings,
      sensor_settings=sensor_settings,

      select_base_logarithm=select_base_logarithm,
      crossover_probability=crossover_probability,
      mutate_probability_of_mutate=mutate_probability_of_mutate,
      population_elite=population_elite,

      sensor_success_rate_area=sensor_success_rate_area,
      byzantine_fault_tolerance=byzantine_fault_tolerance
    )
    store(alert_settings, boundaries, cost_table, population_elite,
          sensor_settings,
          t_incident_intervals, time, target_settings)

############################################################


############################################################
def build(
    name: str,

    boundaries: tuple,

    alert_settings: list,
    target_settings: float,

    cost_table_quality: int,
    stopping_condition: float,
    mutate_probability_of_flipping_bit: float,
    population_size: int,
    population_elite_size: int,
    population_saved_size: int,
    nucleus_settings: list,
    sensor_settings: dict,

    select_base_logarithm: float,
    crossover_probability: float,
    mutate_probability_of_mutate: float,

    sensor_success_rate_area: dict,
    byzantine_fault_tolerance: int
):
  start = timer.time()

  cost_table = {
    (0, x): [('', 0)]
    for x in Interval([boundaries]).range()
  }

  i_boundaries = Interval([boundaries])
  (b_left, b_right) = boundaries
  not_alert = [(x, 0) for x in ~Interval([x for x, _ in alert_settings])]
  alert_partitions = alert_settings + not_alert
  useless_partitions = alert_partitions[:]
  useful_partitions = alert_settings[:]
  for time in range(1, cost_table_quality + 1):
    time_minus_1 = time - 1
    excluded = []

    # Get well known costs
    for x in i_boundaries.range():
      ((x_lower, x_open), (x_upper, x_closed)) = x
      if x_upper - x_lower <= 1:
        for y, c in alert_partitions:
          if not intersects(x, y):
            continue
          _, wait_cost = cost_table[(
            time_minus_1,
            (
              max((x_lower - target_settings, x_open), b_left),
              min((x_upper + target_settings, x_closed), b_right)
            )
          )][0]
          cost_table[(time, x)] = [([], wait_cost + c)]
          excluded += [x]
          # print(str((x_lower, x_upper)) + ' & ' + str((i_lower, i_upper)) + ' -> ' + str(
          #     cost_table[(time, x_lower, x_upper)]))
          break
      else:
        for (y_left, y_right), c in useless_partitions:
          if not (
              y_left <= (x_lower, x_open) and (x_upper, x_closed) <= y_right):
            continue
          _, wait_cost = cost_table[(
            time_minus_1,
            (
              max((x_lower - target_settings, x_open), b_left),
              min((x_upper + target_settings, x_closed), b_right)
            )
          )][0]
          cost_table[(time, x)] = [([], wait_cost + c)]
          excluded += [x]
          # print(str((x_lower, x_upper)) + ' & ' + str((i_lower, i_upper)) + ' -> ' + str(
          #     cost_table[(time, x_lower, x_upper)]))
          break

    # Group intervals by extrapolation
    l_incident_intervals = {}
    for x in reversed(sorted(
        Interval([boundaries]).range(),
        key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(
          x[1][1])
    )):
      if x not in excluded:
        incident_intervals = extrapolate(
          incident_intervals=x,
          excluded=excluded,
          partitions=useless_partitions
        )
        l_incident_intervals[x] = incident_intervals
        excluded += incident_intervals

    # Group intervals by proximity
    d_incident_intervals = {}
    for x in l_incident_intervals:
      (x_left, x_right) = x
      lower_key = (x_left, False)
      if lower_key not in d_incident_intervals:
        d_incident_intervals[lower_key] = [x]
      else:
        d_incident_intervals[lower_key] += [x]

      upper_key = (x_right, True)
      if upper_key not in d_incident_intervals:
        d_incident_intervals[upper_key] = [x]
      else:
        d_incident_intervals[upper_key] += [x]
    k_incident_intervals = sorted(d_incident_intervals.values(),
                                key=lambda x: len(x), reverse=True)

    # Remove repeated intervals
    excluded = []
    x_deleted = 0
    for x in range(len(k_incident_intervals)):
      x -= x_deleted
      x_incident_intervals = k_incident_intervals[x]
      y_deleted = 0
      for y in range(len(x_incident_intervals)):
        y -= y_deleted
        y_incident_intervals = x_incident_intervals[y]
        if y_incident_intervals in excluded:
          del x_incident_intervals[y]
          y_deleted += 1
          if len(x_incident_intervals) is 0:
            del k_incident_intervals[x]
            x_deleted += 1
        else:
          excluded += [y_incident_intervals]

    for x, _ in enumerate(k_incident_intervals):
      k_incident_intervals[x].sort(
        key=lambda x: x[1][0] - x[0][0] + 0.25 * int(not x[0][1]) + 0.25 * int(
          x[1][1]))

    end = timer.time()
    print('Dynamic Performance: ' + str(end - start))

    with open('../share/' + name + '_bla' + str(time) + '.csv', 'w') as file:
      writer = csv.writer(
        file,
        escapechar='\\',
        lineterminator='\n',
        quoting=csv.QUOTE_NONE
      )
      for ((x_lower, x_open), (x_upper, x_closed)), x in sorted(
          l_incident_intervals.items(), key=lambda x: x[0]):
        a = (
          ('{' + str(x_lower) + '}')
          if not x_open and x_closed and x_lower == x_upper
          else
          ('(' if x_open else '[') +
          str(float(x_lower)) + '..' + str(float(x_upper)) +
          (']' if x_closed else ')')
        )
        # print(a + ' -> ' + str(x))
        x = [
          (
            ('{' + str(x_lower) + '}')
            if not x_open and x_closed and x_lower == x_upper
            else
            ('(' if x_open else '[') +
            str(float(x_lower)) + '..' + str(float(x_upper)) +
            (']' if x_closed else ')')
          )
          for ((x_lower, x_open), (x_upper, x_closed)) in x
        ]
        writer.writerow([a] + x)

    with open('../share/' + name + '_ble' + str(time) + '.csv', 'w') as file:
      writer = csv.writer(
        file,
        escapechar='\\',
        lineterminator='\n',
        quoting=csv.QUOTE_NONE
      )
      for x in k_incident_intervals:
        x = [
          (
            ('{' + str(x_lower) + '}')
            if not x_open and x_closed and x_lower == x_upper
            else
            ('(' if x_open else '[') +
            str(float(x_lower)) + '..' + str(float(x_upper)) +
            (']' if x_closed else ')')
          )
          for ((x_lower, x_open), (x_upper, x_closed)) in x
        ]
        writer.writerow(x)

    start = timer.time()

    # context = partial(
    #     multi_search,
    #
    #     l_incident_intervals=l_incident_intervals,
    #
    #     time=time,
    #     cost_table=cost_table,
    #     population_size=population_size,
    #     population_elite_size=population_elite_size,
    #     population_saved_size=population_saved_size,
    #     boundaries=boundaries,
    #     alert_settings=alert_settings,
    #     target_settings=target_settings,
    #     stopping_condition=stopping_condition,
    #     m_flips=m_flips,
    #     nucleus_settings=nucleus_settings,
    #     sensor_settings=sensor_settings,
    #
    #     crossover_probability=crossover_probability,
    #     mutate_probability_of_mutate=mutate_probability_of_mutate,
    #
    #     sensor_success_rate_area=sensor_success_rate_area,
    #     byzantine_fault_tolerance=byzantine_fault_tolerance
    # )
    # with Pool(processes=cpu_count()) as population:
    #     population.map(context, k_incident_intervals)
    for x in k_incident_intervals:
      multi_search(
        k_incident_intervals=x,
        l_incident_intervals=l_incident_intervals,

        time=time,
        cost_table=cost_table,
        population_size=population_size,
        population_elite_size=population_elite_size,
        population_saved_size=population_saved_size,
        boundaries=boundaries,
        alert_settings=alert_settings,
        target_settings=target_settings,
        stopping_condition=stopping_condition,
        mutate_probability_of_flipping_bit=mutate_probability_of_flipping_bit,
        nucleus_settings=nucleus_settings,
        sensor_settings=sensor_settings,

        select_base_logarithm=select_base_logarithm,
        crossover_probability=crossover_probability,
        mutate_probability_of_mutate=mutate_probability_of_mutate,

        sensor_success_rate_area=sensor_success_rate_area,
        byzantine_fault_tolerance=byzantine_fault_tolerance
      )

    end = timer.time()
    print('Genetic Performance: ' + str(end - start))
    start = timer.time()

    with open('../share/' + name + '_readable_cost_table_t_minus_' + str(
        time) + '_minutes.csv', 'w') as file:
      writer = csv.writer(
        file,
        escapechar='\\',
        lineterminator='\n',
        quoting=csv.QUOTE_NONE
      )
      writer.writerow(
        ['time till done', 'interval', 'probes', 'cost', 'probes', 'cost',
         'probes', 'cost',
         'probes',
         'cost', 'probes', 'cost'])
      for x, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
        t, ((x_lower, x_open), (x_upper, x_closed)) = x
        i = (
          ('{' + str(x_lower) + '}')
          if not x_open and x_closed and x_lower == x_upper
          else
          (
              ('(' if x_open else '[') +
              str(float(x_lower)) + '..' + str(float(x_upper)) +
              (']' if x_closed else ')')
          )
        )
        writer.writerow([t] + [i] + [
          x
          for probes, cost in row_value
          for x in [' '.join([
            str(u) + '(' + ' '.join([str(pos) for pos in comb]) + ')'
            for u, comb in probes
          ]), cost]
        ])

    for x, _ in enumerate(useful_partitions):
      ((x_lower, x_open), (x_upper, x_closed)), x_cost = useful_partitions[x]
      x_range = (max((x_lower - target_settings, x_open), b_left),
                 min((x_upper + target_settings, x_closed), b_right))
      useful_partitions[x] = (x_range, x_cost)

      (x_left, x_right) = x_range
      deleted = 0
      for y in range(len(useless_partitions)):
        y -= deleted
        y_range, y_cost = useless_partitions[y]
        if y_cost < x_cost:
          (y_left, y_right) = y_range
          if x_right <= y_right and intersects(x_range, y_range):
            y_left = x_right
            useless_partitions[y] = ((y_left, y_right), y_cost)
          if y_left <= x_left and intersects(x_range, y_range):
            y_right = x_left
            useless_partitions[y] = ((y_left, y_right), y_cost)
          if x_left <= y_left and y_right <= x_right:
            del useless_partitions[y]
            deleted += 1

  with open('../share/cost_table_' + name + '.csv', 'w') as file:
    writer = csv.writer(
      file,
      escapechar='\\',
      lineterminator='\n',
      delimiter=';',
      quoting=csv.QUOTE_NONE
    )
    for c, row_value in sorted(cost_table.items(), key=lambda x: x[0]):
      writer.writerow([c, row_value])

  # time += cost_table_quality

  return cost_table
