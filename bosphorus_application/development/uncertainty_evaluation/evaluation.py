from .get_claims import get_claims
from .get_answers import get_answers
from .get_measurement_cost import get_measurement_cost
from .get_certainty_cost import get_certainty_cost
from .get_uncertainty_cost import get_uncertainty_cost

def evaluation(
    next_unit_time: int,
    cost_table: dict,
    alert_catalog: list,
    trajectory_speed: float,
    nucleus: list,
    sensor_catalog: dict,
    problem: tuple,
):
  claims = get_claims(
    nucleus=nucleus
  )

  certainty, uncertainty = get_answers(
    claims=claims,
    problem=problem
  )

  measurement_cost = get_measurement_cost(
    nucleus=nucleus,
    sensor_catalog=sensor_catalog
  )

  certainty_cost = get_certainty_cost(
    certainty=certainty,
    alert_catalog=alert_catalog,
    cost_table=cost_table,
    next_unit_time=next_unit_time,
    trajectory_speed=trajectory_speed
  )

  uncertainty_cost = get_uncertainty_cost(
    uncertainty=uncertainty,
    alert_catalog=alert_catalog,
    cost_table=cost_table,
    next_unit_time=next_unit_time,
    trajectory_speed=trajectory_speed
  )

  return measurement_cost + certainty_cost + uncertainty_cost
