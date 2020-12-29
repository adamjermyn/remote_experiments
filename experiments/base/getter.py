import os.path
from os import path
import subprocess as sp

def get_file(connection, fname, remote_dir, local_dir, local_name=None):
	'''
	Loop over all subfolders of the remote_dir.
	In each, find the named file.
	Then check the checksum against the local copy (if one exists).
	If not, download it and rename it to (containing folder name + _ + file name).
	'''
	with connection.cd(remote_dir):

		result = connection.run('find . ' + ' -name ' + fname + ' ! -path \'*experiments*\'')

		files = result.stdout.split('\n')
		files = list(f for f in files if len(f) > 0)

		for f in files:
			remote_name = f.split('/')[1]
			if local_name is None:
				local_fname = local_dir + remote_name + '_' + fname
			else:
				local_fname = local_dir + remote_name + '_' + local_name
			if path.isfile(local_fname):
				local_sha = str(sp.run('openssl sha1 ' + local_fname, shell=True, capture_output=True).stdout).split('=')[1].strip('\\n\'').strip()
				remote_sha =  connection.run('openssl sha1 ' + f).stdout.split('=')[1].strip()
				if local_sha != remote_sha:
					sp.run('rsync -zarv rusty:' + remote_dir + f + ' ' + local_fname, shell=True)
			else:
				sp.run('rsync -zarv rusty:' + remote_dir + f + ' ' + local_fname, shell=True)
