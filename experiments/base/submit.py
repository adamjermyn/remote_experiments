from experiments.base.grids import make_grid
from datetime import datetime
from pickle import dump

def submit(repo, remote, bname, patch, patch_name):
	# Setup
	print('Change local branch to ' + bname)
	repo.change_branch(bname)
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

	# Run
	sha = repo.get_short_sha()
	print('Running branch ' + pname + ' with short sha ' + sha + ' on remote.')
	remote.run_branch_on_remote(pname, sha)
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

def batch_submit(sweep, repo, remote, make_patch):
	bname = sweep['branch']
	name = sweep['name']
	base_config = sweep['base_config']
	dimensions = sweep['dimensions']
	grid = make_grid(base_config, dimensions)

	for config in grid:
		patch = make_patch(config)
		submit(repo, remote, bname, patch, name)

def save_batch(sweep, dname):
	now = datetime.now()
	time = now.strftime('%Y_%m_%d_%H_%M_%S')
	dump(sweep, open(dname + '/' + sweep['name'] + '_' + time + '.pkl', 'wb'))