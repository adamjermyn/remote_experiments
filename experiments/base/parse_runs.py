from glob import glob
from collections import defaultdict
from experiments.base.grids import make_grid
from pandas import DataFrame
from copy import deepcopy
import subprocess

def parse(repo_dir, output_dir, parser):
	'''
	Extracts configurations from all files in the output_dir.

	Parsing is done by the provided parser function.
	The parser function returns a dictionary of {parameter_name:value} pairs
	when given a valid input file and None otherwise.

	If parsing requires reading auxiliary files that is the responsibility of
	the parser function. For instance, it might be that there are
	actually four configuration files per simulation.

	In that case the parser should return None on three of them and
	use the name of the fourth to identify the other three, combining
	their configurations into one dictionary.
	
	A good practice in this instance is to name the parameters by which file they appear in
	(e.g. 'config_file_1/param').

	repo_dir is the directory of the git repository that generated these runs.
	This is used to extract information on the parent commit that the runs were
	derived from (assuming runs are done on temporary patch branches).

	The output is a Pandas DataFrame with columns corresponding to configuration options and rows corresponding to files.

	'''

	files = list(glob(output_dir + '/*', recursive=False))

	# parser emits a dict of the form {parameter:value}.
	parsed = {fi:parser(fi) for fi in files}
	files = list(fi for fi in files if parsed[fi] is not None)
	parsed = dict({key:val for key,val in parsed.items() if val is not None})

	# We now append two special parameters:
	# 'self_short_sha', which is the short-sha of the commit that was run
	# 'parent_sha', which is the sha of the commit that the run was based on (assuming the run was done on a temporary patch branch).
	for fi in files:
		s = fi.split('sha')[1]
		s = s.split('_')
		short_sha = s[1]
		output = subprocess.run('cd ' + repo_dir + '; git log --pretty=%P -n 1 ' + short_sha, shell=True, capture_output=True)
		parent_sha = output.stdout.decode("utf-8").strip('\n')
		parsed[fi]['self_short_sha'] = short_sha
		parsed[fi]['parent_sha'] = parent_sha

	parsed = DataFrame.from_dict(parsed, orient='index')
	return parsed

def extract_runs(parsed, configs):
	'''
	Picks out all runs from the parsed set whose configurations match the specified ones.
	'''
	filtered = deepcopy(parsed)
	for param,value in configs.items():
		filtered = filtered[filtered[param] == value]
	return filtered

def group_by_parent(parsed):
	'''
	Groups configurations by parent commit hash.
	Returns a dictionary of the form
	{parent_hash:DataFrame}
	'''
	parents = parsed['parent_sha'].unique()
	ret = dict({parent:parsed[parsed['parent_sha'] == parent]})
	return ret