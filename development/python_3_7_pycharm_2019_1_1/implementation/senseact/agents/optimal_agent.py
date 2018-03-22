from math import floor, ceil
from time import time

from senseact.agents import Agent

class OptimalAgent(Agent):

  def __init__(self, settings):
    super().__init__('OptimalAgent', settings)

  def invoke_optimal_algorithm(
      self,

      oracle
  ):

    cheapest_probe = min(self.settings['probe']['types'].keys(), key=self.settings['probe']['types'].get)

    start = time()

    if self.turn is 0 or any(
      self.settings['boundaries'][0] <= minimum < self.current_alert[0][0]
      or self.current_alert[0][1] < maximum <= self.settings['boundaries'][1]
      for (minimum, _), (maximum, _) in self.incident_intervals
    ):
      # Step 1: Minimize uncertainty when the uncertainty may reach multiple sensitive zones
      minimum = floor(oracle.position)
      maximum = ceil(oracle.position)
      if minimum == self.settings['boundaries'][0]:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe + self.settings['target']['speed']),
        )
      elif maximum == self.settings['boundaries'][1]:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe - self.settings['target']['speed']),
        )
      elif minimum - cheapest_probe - 1 < self.settings['boundaries'][0]:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe + self.settings['target']['speed']),
        )
      else:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe - self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe),
        )

    end = time()

    return self.name, self.turn, end - start
