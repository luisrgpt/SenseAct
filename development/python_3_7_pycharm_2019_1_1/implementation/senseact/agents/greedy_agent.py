from time import time

from senseact.agents import Agent
from senseact.math import float_range

class GreedyAgent(Agent):

  def __init__(self, settings):
    super().__init__('GreedyAgent', settings)

  def invoke_greedy_algorithm(
      self
  ):

    cheapest_probe = min(self.settings['probe']['types'].keys(), key=self.settings['probe']['types'].get)
    (minimum, _), (maximum, _) = self.incident_intervals[0]

    start = time()

    if self.turn == 0:
      # Step 1: Send as many probes as possible in a single batch
      self.departing_batch = tuple(
        (self.settings['probe']['types'][cheapest_probe], cheapest_probe, x)
        for x in float_range(self.settings['boundaries'][0], self.settings['boundaries'][1], scale=self.settings['scale'])
      )

    else:
      # Step 2: Keep the knowledge space size
      if minimum == self.settings['boundaries'][0]:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe + self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe + 2 * self.settings['target']['speed']),
        )
      elif maximum == self.settings['boundaries'][1]:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe - 2 * self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe - self.settings['target']['speed']),
        )
      elif minimum - cheapest_probe - 1 < self.settings['boundaries'][0]:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe - self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe + self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, minimum + cheapest_probe + 2 * self.settings['target']['speed']),
        )
      else:
        self.departing_batch = (
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe - 2 * self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe - self.settings['target']['speed']),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe),
          (self.settings['probe']['types'][cheapest_probe], cheapest_probe, maximum - cheapest_probe + self.settings['target']['speed']),
        )

    end = time()

    return self.name, self.turn, end - start
