import subprocess
import git

class Repo:

	def __init__(self, dname):
		self.dname = dname
		self.repo = git.Repo(dname)

	def get_short_sha(self):
		sha = self.repo.head.object.hexsha
		short_sha = self.repo.git.rev_parse(sha, short=1)
		return short_sha

	def change_branch(self, bname):
		self.repo.git.checkout(bname)

	def new_branch(self, base, bname):
		# Check out base, make new branch, check out new branch.
		self.repo.git.checkout(base)
		self.repo.git.branch(bname)
		self.repo.git.checkout(bname)

	def commit_all(self, message):
		subprocess.run('cd ' + self.dname + '; git add *; git commit -m "' + message + '"', shell=True)

	def push_branch(self, bname):
		subprocess.run('cd ' + self.dname + '; git push --force --set-upstream origin ' + bname, shell=True)

	def delete_branch(self, bname):
		subprocess.run('cd ' + self.dname + '; git branch -d ' + bname, shell=True)
		subprocess.run('cd ' + self.dname + '; git push -d origin ' + bname, shell=True)
