import subprocess
from datetime import datetime

class Remote:

	def __init__(self, origin, origin_dir, run_dir):
		self.origin = origin
		self.origin_dir = origin_dir
		self.run_dir = run_dir

	def get_branch_on_remote(self, bname):
		command = "ssh " + self.origin + " 'cd " + self.origin_dir + "; git fetch; git reset --hard origin/" + bname + "'"
		subprocess.run(command, shell=True)

	def prepare_branch_on_remote(self, bname, sha):
		now = datetime.now()
		time = now.strftime('%Y_%m_%d_%H_%M_%S')
		dir_name = bname + '_time_' + time +  '_sha_' + sha
		command = "ssh " + self.origin + " 'rsync -av --exclude=\".*\" " + self.origin_dir + "/ " + self.run_dir + "/" + dir_name + " '"
		subprocess.run(command, shell=True)
		return self.run_dir + "/" + dir_name

	def run_branch_on_remote(self, run_path):
		command = "ssh " + self.origin + " \"bash -lc 'cd " + run_path + "; pwd; sbatch run.sbatch'\""
		subprocess.run(command, shell=True)

	def get_disBatch_file(self, disBatch_run_dir, run_dir):
		command = "ssh " + self.origin + " \"bash -lc 'cp " + run_path + "/run.disBatch " + disBatch_run_dir + "/'\""
		subprocess.run(command, shell=True)

	def run_disBatch_on_remote(self, run_path):
		command = "ssh " + self.origin + " \"bash -lc 'cd " + run_path + "; pwd; sbatch run.disBatch'\""
		subprocess.run(command, shell=True)