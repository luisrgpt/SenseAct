from typing import \
  List
from senseact_evaluation import \
  get_claims, \
  get_answers, \
  get_measurement_cost, \
  get_certainty_cost, \
  get_uncertainty_cost

def evaluate(
    population,
    minimum: float,
    maximum: float,
    amount: int,
    cost_table,
    settings,
    probability_mass_function: List[float] = None
):
  fitness = []
  for nucleus in population:
    claims = get_claims(
      nucleus=nucleus,
      minimum=minimum,
      maximum=maximum,
      amount=amount
    )
    certainty, uncertainty = get_answers(
      claims=claims,
      minimum=minimum,
      maximum=maximum,
      probability_mass_function=probability_mass_function
    )
    measurement_cost = get_measurement_cost(
      nucleus=nucleus,
      settings=settings.sensor
    )
    certainty_cost = get_certainty_cost(
      certainty=certainty,
      cost_table=cost_table,
      settings=settings
    )
    uncertainty_cost = get_uncertainty_cost(
      uncertainty=uncertainty,
      cost_table=cost_table,
      settings=settings
    )
    fitness += [measurement_cost + certainty_cost + uncertainty_cost]
  return fitness
