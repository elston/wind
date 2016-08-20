import numpy as np
import numpy.ma as ma


def reduce_scenarios(scenarios, probabilities, new_n_scenarios):
    if isinstance(scenarios, list):
        scenarios = np.array(scenarios)
    n_scenarios, time_span = scenarios.shape

    cost_matrix = ma.array(get_cost_matrix(scenarios))
    cost_matrix_i = cost_matrix.copy()

    reduced_set = []
    distances = np.dot(cost_matrix, probabilities)
    included_sc_idx = np.argmin(distances)
    reduced_set.append(included_sc_idx)

    for n in xrange(1, new_n_scenarios):
        col_for_minimum = cost_matrix_i[:, included_sc_idx].copy()

        for idx in reduced_set:
            cost_matrix_i[idx, :] = ma.masked
            cost_matrix_i[:, idx] = ma.masked

        cost_matrix_i = np.minimum(cost_matrix_i, col_for_minimum.reshape(n_scenarios, 1))

        distances = np.dot(cost_matrix_i.T, probabilities)
        for idx in reduced_set:
            distances[idx] = ma.masked

        included_sc_idx = np.argmin(distances)
        reduced_set.append(included_sc_idx)

    new_scenarios = scenarios[reduced_set, :]
    new_probabilities = probabilities[reduced_set]

    for i in xrange(n_scenarios):
        if i in reduced_set:
            continue
        distances_to_reduced = cost_matrix[i, reduced_set]
        scenario_to_add = np.argmin(distances_to_reduced)
        new_probabilities[scenario_to_add] += probabilities[i]

    return new_scenarios, new_probabilities


def scenarios_distance(s1, s2):
    return np.linalg.norm(s1 - s2)


def get_cost_matrix(scenarios):
    n_scenarios = scenarios.shape[0]
    cost_martix = np.empty((n_scenarios, n_scenarios))
    for i in xrange(n_scenarios):
        cost_martix[i][i] = 0.0
        for j in xrange(i + 1, n_scenarios):
            cost_martix[i][j] = cost_martix[j][i] = scenarios_distance(scenarios[i], scenarios[j])
    return cost_martix
