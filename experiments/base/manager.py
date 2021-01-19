import argparse
import subprocess as sp
from datetime import datetime

# Parse arguments
parser = argparse.ArgumentParser(description='Manager script.')

parser.add_argument('--submit_single', dest='submit_single', action='store_const', const=True, default=False)
parser.add_argument('--start_of_batch', dest='end_of_batch', action='store_const', const=True, default=False)
parser.add_argument('--end_of_batch', dest='end_of_batch', action='store_const', const=True, default=False)
parser.add_argument('path', metavar='path', type=str, help='Path to slurm batch script')
parser.add_argument('disBatch_path', metavar='disBatch_path', type=str, help='Path to hold disBatch directories.')
parser.add_argument('--num_simultaneous_tasks', dest='num_simultaneous_tasks', type=int, default=-1)

args = parser.parse_args()

# If this is a single run, submit it and exit.
if args.submit_single:
	sp.run('cd ' + args.path + '; sbatch run.sbatch', shell=True)
	exit()

# If we get here, it's a batch.
# Set up for batch (if start)
dirName = args.disBatch_path
if args.start_of_batch:
	sp.run('mkdir ' + dirName + '; touch ' + dirName + '/tasks.disBatch', shell=True)

# Write the task down
fi = open(dirName + '/tasks.disBatch','a')
fi.write('cd ' + args.path + '; ./run.sbatch\n')
fi.close()

# If this is the last in a batch, generate the disBatch script and run it.
if args.end_of_batch:
	# Parse slurm config from last in batch
	fi = open(args.path + '/run.sbatch','r')
	lines = list(l for l in fi if '#SBATCH' in l or '#!/bin/bash' in l)
	fi.close()

	# Parse slurm config from last in batch
	fi = open(dirName + '/run.disBatch','w+')
	for l in lines:
		fi.write(l)
	fi.write('disBatch tasks.disBatch')
	fi.close()

	# Submit job
	# sp.run('cd ' + dirName + '; sbatch run.disBatch', shell=True)

