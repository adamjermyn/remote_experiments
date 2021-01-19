from experiments.base.grids import make_grid
from datetime import datetime
from pickle import dump

def prepare_remote(repo, remote, bname, patch, name):
	
	# Setup
	repo.change_branch(bname)
	parent_sha = repo.get_short_sha()
	print('Change local branch to ' + bname + ' with short sha ' + parent_sha)
	print('-------------')

	pname = bname + '_' + patch_name
	print('Create new branch with name ' + pname)
	repo.new_branch(bname, pname)
	print('-------------')

	print('Applying patch locally.')
	patch(repo.dname)
	print('-------------')

	print('Committing patch to patch branch.')
	repo.commit_all('Patch.')
	print('-------------')

	print('Push branch ' + pname + ' to origin.')
	repo.push_branch(pname)
	print('-------------')

	print('Getting branch ' + pname + ' on remote.')
	remote.get_branch_on_remote(pname)
	print('-------------')

	# Prepare
	sha = repo.get_short_sha()
	print('Preparing branch ' + pname + ' with short sha ' + sha + ' on remote.')
	run_path = remote.prepare_branch_on_remote(pname, sha)
	print('-------------')

	# Cleanup
	print('Getting branch ' + bname + ' on remote.')
	remote.get_branch_on_remote(bname)
	print('-------------')

	print('Change local branch to ' + bname)
	repo.change_branch(bname)
	print('-------------')

	print('Removing branch locally and on origin.')
	repo.delete_branch(pname)
	print('-------------')
	return run_path, parent_sha, sha

def submit(run_path):
	# Run
	sha = repo.get_short_sha()
	print('Running branch on remote.')
	remote.run_branch_on_remote(run_path)
	print('-------------')

def batch_submit(sweep, repo, remote, make_patch, batch_dir):
	bname = sweep['branch']
	name = sweep['name']
	base_config = sweep['base_config']
	dimensions = sweep['dimensions']
	grid = make_grid(base_config, dimensions)

	sweep['run_shas'] = []
	for config in grid:
		patch = make_patch(config)
		run_path, parent_sha, child_sha = prepare_remote(repo, remote, bname, patch, name)
		sweep['parent_sha'] = parent_sha
		sweep['run_shas'].append(child_sha)
		submit(run_path)

	save_batch(sweep, batch_dir)
	return sweep

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

def save_batch(sweep, dname):
	now = datetime.now()
	time = now.strftime('%Y_%m_%d_%H_%M_%S')
	dump(sweep, open(dname + '/' + sweep['name'] + '_' + time + '.pkl', 'wb'))