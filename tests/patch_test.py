from remote import Remote
from repo import Repo
from submit import submit
from patcher import make_patch


repo = Repo('/Users/ajermyn/Dropbox/Software/Stokes_Experiments')
remote = Remote('rusty', '/mnt/home/ajermyn/Projects/Stokes_Experiments', '/mnt/home/ajermyn/ceph/Stokes_Experiments/')



config = {
	'x_ctrl(6)': 4.0, # Heat multiplier
	'x_logical_ctrl(1)': '.false.', # True for simple norm, false for complicated
	'x_ctrl(2)': 1.0 # nf spacing in log space
	'x_ctrl(3)': 1.0 # nl spacing in log space
	'x_ctrl(5)': 1e-4 # Heat smoothing in Msun
	'x_ctrl(7)': 1.0 # N^2 smoothing in distance 1/(this*kr)
	'time_delta_coeff': 0.2 # Time resolution
}

bname = 'master'
config = {}
config['x_ctrl(2)'] = 1.0
patch = make_patch(config)

submit(repo,remote,bname,patch)