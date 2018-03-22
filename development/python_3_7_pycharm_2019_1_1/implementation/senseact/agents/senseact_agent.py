from itertools import repeat
from time import time

from senseact.agents import \
  Agent
from senseact.evaluation import \
  evaluate_non_uniform
from senseact.math import \
  crop_probability_mass_function, \
  float_range, \
  redistribute_probability_mass_function

class SenseActAgent(Agent):

  def __init__(
    self,
    settings
  ):
    super().__init__('SenseActAgent', settings)
    amount = int((self.settings['boundaries'][1] - self.settings['boundaries'][0]) / self.settings['scale'])
    self.probability_mass_function = {}
    decrementer = 1.0
    a_fraction = 1 / amount
    for position in float_range(minimum=self.settings['boundaries'][0], maximum=self.settings['boundaries'][1] - self.settings['scale'], scale=self.settings['scale']):
      self.probability_mass_function[position] = a_fraction
      decrementer -= a_fraction
    self.probability_mass_function[self.settings['boundaries'][1] - self.settings['scale']] = decrementer

  def wait(
    self,
    unit_time
  ):
    output = super().wait(unit_time)
    self.probability_mass_function = redistribute_probability_mass_function(
      probability_mass_function=self.probability_mass_function,
      incident_intervals=self.incident_intervals,
      settings=self.settings,
    )

    return output

  def invoke_inference_algorithm(
      self
  ):
    super().invoke_inference_algorithm()
    self.probability_mass_function = crop_probability_mass_function(
      probability_mass_function=self.probability_mass_function,
      interval=self.incident_intervals,
      settings=self.settings,
    )

  def invoke_senseact_algorithm(
      self,
      cost_table,
  ):

    start = time()

    # Step 1: Pick the best set of batch for each disjunction
    batch = tuple(
      min(
        evaluate_non_uniform(
          population=tuple(x for x in cost_table[self.settings['time'] - self.turn][minimum, maximum] if x is not None),
          boundaries=(minimum, maximum),
          extended_boundaries=self.settings['boundaries'],
          amount=int(self.settings['boundaries'][1] - self.settings['boundaries'][0]) + 1,
          cost_table=cost_table[self.settings['time'] - self.turn - 1],
          settings=self.settings,
          probability_mass_function=self.probability_mass_function,
        ).items(),
        key=lambda x: x[1],
      )[0]
      for ((minimum, _), (maximum, _)) in self.incident_intervals
    )

    # Step 2: Prepare probe information
    probe_types = [
      (position, y)
      for x in self.settings['probe']['types'].items()
      for position, y in enumerate(repeat(x, int(self.settings['boundaries'][1] - self.settings['boundaries'][0]) + 1))
    ]
    self.departing_batch = tuple(
      (probe_cost, probe_type, position)
      for local_batch in batch
      for condition, (position, (probe_type, probe_cost)) in zip(local_batch, probe_types) if condition
    )

    end = time()

    return self.name, self.turn, end - start
