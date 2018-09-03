# coding=utf-8

from algorithm import build
from submarine import Parameters
#from forest_fires import Parameters

build(
    name=Parameters.name,

    bounds=Parameters.bounds,

    alert_costs=Parameters.alert_costs,
    decay_unit=Parameters.decay_unit,

    computation_rate=Parameters.computation_rate,
    m_stagnation=Parameters.m_stagnation,
    m_flips=Parameters.m_flips,

    n_pool=Parameters.n_pool,
    m_tops=Parameters.m_tops,
    n_sel=Parameters.n_sel,
    n_precisions=Parameters.n_precisions,
    n_costs=Parameters.n_costs,

    k_mat=Parameters.k_mat,
    k_mut=Parameters.k_mut,

    probability_distributions=Parameters.probability_distributions,
    byzantine_fault_tolerance=Parameters.byzantine_fault_tolerance
)
