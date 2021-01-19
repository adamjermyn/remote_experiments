from experiments.base.grids import make_grid
from datetime import datetime
from pickle import dump



def disBatch_submit(sweep, repo, remote, make_patch, batch_dir, disBatch_dir):
	bname = sweep['branch']
	name = sweep['name']
	base_config = sweep['base_config']
	dimensions = sweep['dimensions']
	grid = make_grid(base_config, dimensions)

	run_paths = []
	sweep['run_shas'] = []
	for config in grid:
		patch = make_patch(config)
		run_path, parent_sha, child_sha = prepare_remote(repo, remote, bname, patch, name)
		run_paths.append(run_path)
		sweep['parent_sha'] = parent_sha
		sweep['run_shas'].append(child_sha)

	now = datetime.now()
	time = now.strftime('%Y_%m_%d_%H_%M_%S')
	disBatch_run_dir = disBatch_dir + '/time_' + time

	repo.get_disBatch_file(disBatch_run_dir, run_dir)
	repo.run_disBatch_on_remote(disBatch_run_dir)

	save_batch(sweep, batch_dir)
	return sweep
