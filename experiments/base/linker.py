import subprocess
from experiments.base.grids import make_grid
from experiments.base.parse_runs import extract_runs, group_by_parent

def make_symlinks(parsed, namer, config_file_name, target_file_name, symlink_dir):
	'''
	Generates symlinks to run output files.
	
	symlink_dir specifies the directory in which to put symlinks. This is created if it does not exist.
	
	target_file_name is the base file name of the output file (e.g. mov.mp4, before we add the run details).
	config_file_name is the base file name of the configuration file (e.g. config.yaml).
	We obtain the file names of the output files by taking each parsed configuration file, stripping off
	the base config_file_name, and appending the target_file_name.

	namer is a function that takes the configuration as input and produces a name for the symlink as output.
	A common pattern is to name the symlink by one or more of the parameters involved in the run.
	'''

	subprocess.run('mkdir ' + symlink_dir, shell=True)

	for fi,config in parsed.iterrows():
		link_name = symlink_dir + '/' + namer(config) + '_' + target_file_name
		link_target = fi[:-len(config_file_name)] + target_file_name
		subprocess.run('rm ' + link_name, shell=True)
		subprocess.run('ln -s ' + link_target + ' ' + link_name, shell=True)

def batch_make_symlinks(parsed, sweep, namer, config_file_name, target_file_names, symlink_dir):
	grid = make_grid(sweep['base_config'], sweep['dimensions'])
	parents = group_by_parent(extract_runs(parsed, grid))
	for parent,runs in parents.items():
		for target_file_name in target_file_names:
			make_symlinks(runs, namer, config_file_name, target_file_name, symlink_dir)
