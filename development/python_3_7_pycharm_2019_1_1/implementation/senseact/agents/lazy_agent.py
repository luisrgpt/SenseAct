from time import time

from senseact.agents import Agent
from senseact.math import float_range

class LazyAgent(Agent):

  def __init__(self, settings):
    super().__init__('LazyAgent', settings)

  def invoke_lazy_algorithm(
      self
  ):

    cheapest_probe = min(self.settings['probe']['types'].keys(), key=self.settings['probe']['types'].get)
    (minimum, _), (maximum, _) = self.incident_intervals[0]

    start = time()

    if self.turn is 0:
      # Step 1: Send as many batch as possible
      self.departing_batch = tuple(
        (self.settings['probe']['types'][cheapest_probe], cheapest_probe, x)
        for x in float_range(
          minimum=self.settings['boundaries'][0],
          maximum=self.settings['boundaries'][1],
          scale=self.settings['scale']
        )
      )

    elif any(
      self.settings['boundaries'][0] <= minimum < self.current_alert[0][0]
      or self.current_alert[0][1] < maximum <= self.settings['boundaries'][1]
      for (minimum, _), (maximum, _) in self.incident_intervals
    ):
      # Step 2: Send as many batch as possible after a certain period of time
      self.departing_batch = tuple(
        (self.settings['probe']['types'][cheapest_probe], cheapest_probe, x)
        for x in float_range(
          minimum=minimum - cheapest_probe * self.settings['scale'],
          maximum=maximum + cheapest_probe * self.settings['scale'],
          scale=self.settings['scale']
        )
      )

    end = time()

    return self.name, self.turn, end - start
