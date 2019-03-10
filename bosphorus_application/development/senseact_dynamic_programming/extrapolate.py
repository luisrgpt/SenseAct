from senseact_math import Interval, intersects
from math import inf

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
