from random import randint, choice

from senseact.math import float_range

class EmergentAndUncertainEnvironment:

  @staticmethod
  def trajectory(location, settings):
    while True:
      yield location

      location += choice(tuple(float_range(minimum=-settings['target']['speed'], maximum=settings['target']['speed'], scale=settings['scale'])))
      location = max(location, settings['boundaries'][0])
      location = min(location, settings['boundaries'][1])

  def __init__(
      self,
      settings
  ):
    # Log
    self.name = 'Environment'

    self.settings = settings

    # State
    self.position = round(
      randint(
        self.settings['boundaries'][0],
        self.settings['boundaries'][1] - self.settings['scale'],
      ) + self.settings['scale'] / 2,
      12
    )
    self.trajectory = self.trajectory(self.position, self.settings)
    self.arriving_batch = {}
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
      self.settings['boundaries'],
      self.position
    )

  ############################################################



  ############################################################
  def wait(
      self,
      unit_time
  ):

    # As time passes, the environment changes.
    for _ in range(unit_time):
      self.position = next(self.trajectory)

    return self

  ############################################################

  ############################################################
  def import_batch(
      self,
      source
  ):

    source.probe_cost += sum(x for x, _, _ in source.departing_batch)
    self.arriving_batch[source.name] = source.departing_batch
    source.departed_batch = " ".join(str(x) for _, _, x in source.departing_batch)
    source.departing_batch = ()

    # Probes land and take their measurements instantaneously.
    # TODO: We may improve this by considering non-instantaneous measurements, where the delay is caused by distance, obstacle or any other unexpected event
    landed_batch = self.arriving_batch
    self.measurements = {
      name: [
        (float(location), float(imprecision), cost,
        abs(location - self.position) <= imprecision, False)
        for cost, imprecision, location in batch
      ]
      for name, batch in landed_batch.items()
    }
    self.arriving_batch = {}

    return self
