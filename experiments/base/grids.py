from itertools import product
from copy import deepcopy

def make_grid(base_config, dimensions):
	'''
	Makes an n-dimensional grid sweeping through parameter settings

	Each dimension of the grid is given by modifying a set of parameters along a given range.
	For instance, suppose the parameters are labelled p1, p2, ..., pN.
	One dimension in the grid might be formed by (p1, p3), which get swept through the values [(1,1), (2,1), (3,2), (5,0), (6,4), ...].
	A second dimension could be formed by (p4, p7, p9), sweeping through a list of three-tuples.
	More dimensions can be added similarly, so long as the dimensions form disjoint sets of variables.
	The grid is then the cartesian product of these dimensions.

	THIS METHOD DOES NOT CHECK IF SETS ARE DISJOINT.
	Non-disjoint dimension specifications produce undefined behavior.

	Arguments:
		base_config - Base configuration to modify. Dictionary of the form {param_name:param_value}
		dimensions - Dictionary. Each key is a tuple of parameters corresponding to one dimension.
					 Each value is a list of tuples giving the parameter values to sweep through.

	Returns:
		List of `config` objects implementing the points in the grid.
	'''

	shape = list(len(val) for key,val in dimensions.items())
	shape_ranges = list(list(range(n)) for n in shape)

	it = product(*shape_ranges)

	configs = []

	for ns in it:
		config = deepcopy(base_config)

		for n, (param_set, param_values) in zip(*(ns, dimensions.items())):
			for i,param in enumerate(param_set):
				config[param] = param_values[n][i]

		configs.append(config)

	return configs
