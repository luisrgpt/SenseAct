from senseact.evaluation.get_answers_non_uniform import \
  get_answers_non_uniform
from senseact.evaluation.get_certainty_cost import \
  get_certainty_cost
from senseact.evaluation.get_claims import \
  get_claims
from senseact.evaluation.get_measurement_cost import \
  get_measurement_cost
from senseact.evaluation.get_uncertainty_cost import \
  get_uncertainty_cost

def evaluate_non_uniform(
    population,
    boundaries,
    extended_boundaries,
    amount: int,
    cost_table,
    settings,
    probability_mass_function,
):

  fitness = {}
  for chromosome in population:

    claims = get_claims(
      chromosome=chromosome,
      boundaries=boundaries,
      extended_boundaries=extended_boundaries,
      amount=amount,
      settings=settings,
    )
    certainty, uncertainty = get_answers_non_uniform(
      claims=claims,
      boundaries=boundaries,
      probability_mass_function=probability_mass_function,
      settings=settings
    )
    measurement_cost = get_measurement_cost(
      chromosome=chromosome,
      amount=amount,
      settings=settings,
    )
    certainty_cost = get_certainty_cost(
      certainty=certainty,
      cost_table=cost_table,
      settings=settings,
    ) if certainty else 0
    uncertainty_cost = get_uncertainty_cost(
      uncertainty=uncertainty,
      cost_table=cost_table,
      settings=settings,
    ) if uncertainty else 0
    fitness[chromosome] = measurement_cost + certainty_cost + uncertainty_cost

  return fitness
