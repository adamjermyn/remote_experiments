# RemoteExperiments

This Python package enables running and analyzing **reproducible** numerical experiments on a remote cluster using [Slurm](https://www.schedmd.com).

## Installation

Download/clone this repository locally, then add the containing directory (`remote_experiments`) to your Python path.

## Usage

To ensure reproducibility, in RemoteExperiments every numerical experiment corresponds uniquely to a single commit in a git repository. The control flow is then of the form:

1. User specifies a commit to base an experiment on.
2. User specifies configuration settings as patches to apply to that commit.
3. RemoteExperiments creates a new commit on a temporary branch with the patches applied and pushes to `origin`.
4. RemoteExperiments uses `ssh` to log into the remote cluster, pull that temporary branch, and submit that experiment to the Slurm queue using `sbatch run.sbatch`, where `run.sbatch` is a hard-coded name for the Slurm job script.
5. The output folder contains a copy of the relevant commit and is labelled by the time, date, and short-sha of the commit. The temporary branch is deleted locally, on the cluster, and on `origin`.

In order for this to work, the code and configuration files that are needed to run your experiment must live in a git repo with a configured `origin` (i.e. Github). That repo has to be cloned both locally and on the remote cluster where you want to run experiments.

### Single experiment

Assuming that's done, we first tell RemoteExperiments where the local repository lives:

```python
from experiments.base.repo import Repo
repo = Repo('path/to/repo')
```

Next we configure cluster access:

```python
remote = Remote('user@remote_machine', 'path/to/repo/on/cluster', 'path/to/store/output')
```

At this stage we can submit an experiment to the queue using

```python
from experiments.base.submit import submit
submit(repo, remote, 'branch name', patcher, 'patch name')
```

where here `patcher` is a Python function, specific to your experiments, which applies a patch to your repo. For instance a patch could change some configuration settings, or modify the code in some way. RemoteExperiments first checks out the specified branch, then calls `patcher("path-to-repository")`, commits the changes to a new (temporary) branch, and then pulls that branch on the remote and runs it.

The output from this process looks as follows:

```
Change local branch to main with short sha ae9a
-------------
Create new branch with name main_rho_test
-------------
Applying patch locally.
-------------
Committing patch to patch branch.
...
 1 file changed, 3 insertions(+), 2 deletions(-)
-------------
Push branch main_rho_time_test to origin.
...
Branch 'main_rho_time_test' set up to track remote branch 'main_rho_test' from 'origin'.
-------------
Getting branch main_rho_time_test on remote.
...
HEAD is now at 694c7af Patch.
-------------
Running branch main_rho_test with short sha 694c on remote.
/.../main_rho_test_time_2021_01_12_10_21_25_sha_694c
Submitted batch job 898024
```

Note that the Slurm job directory contains a copy of `HEAD` and is named as `temp_branch_name_time_YYYY_MM_DD_HH_MM_SS_sha_shortSHA`.

### 1-Parameter Sweep Experiments

RemoteExperiment comes with helper functions for running parameter sweeps. For instance the following example sets up a series of experiments which share a single base configuration but differ in one parameter.

```python
from experiments.base.remote import Remote
from experiments.base.repo import Repo
from experiments.base.submit import batch_submit
from experiments.extensions.mesa_patcher import make_patch
from experiments.base.grids import make_grid
from pickle import dump

batch_dir = '...'
repo = Repo('...')
remote = Remote(...)

#-------------
base_config = {
	'param1': 1,
	'param2': 2,
	'param3': 3
}
dimensions = {
					('param4',):[(0.1,), (0.2,), (0.3,)],
				}
sweep = {}
sweep['base_config'] = base_config
sweep['name'] = 'example'
sweep['branch'] = 'main'
sweep['dimensions'] = dimensions
batch_submit(sweep, repo, remote, make_patch, batch_dir)

```

Here `batch_dir` specifies where to save a copy of the sweep configuration, which is useful for later analysis. This configuration is saved along with a list of the short-Sha's of the experiment commits in a pickled dictionary named as `"sweep['name']_YYYY_MM_DD_HH_MM_SS.pkl`.

### N-Parameter Sweeps

The `batch_submit` function knows how to handle much more general sweeps. You can specify any number of parameters to vary together:

```python
dimensions = {
					('param4','param5'):[(0.1,'A'), (0.2,'B'), (0.3,'C')],
				}
```

This will run one experiment with `param4=0.1,param5='A'`, one with `(0.2,'B')`, and so on. 

As the name suggests, `dimensions` can also be used to run multi-dimensional grids:

```python
dimensions = {
					('param4','param5'):[(0.1,'A'), (0.2,'B'), (0.3,'C')],
					('param6',):[(2,), (3,), (4,)],
				}
```

More generally, `dimensions` is a dictionary where the keys are tuples of parameters and the values are tuples of parameter settings with the same in-tuple ordering. Each `(key,value)` pair gets swept independently, so an N-dimensional grid of experiments is specified by giving N `(key,value)` pairs to `dimensions`.

## Analysis

### Retrieving Output

RemoteExperiment uses the [Fabric](http://www.fabfile.org) library combined with `ssh` and `rsync` to retrieve the results of experiments. For example:

```python
from fabric import Connection
from experiments.base.getter import get_file

c = Connection('user@cluster')
local_dir = '...'
remote_dir = 'path/containing/output/on/cluster'

get_file(c, 'inlist_project', remote_dir, local_dir)
get_file(c, 'history.data', remote_dir, local_dir)
```

This will download all files with the given name (e.g. `history.data` or `inlist_project`) from all experiments in the `remote_dir`. Each file downloaded is placed in `local_dir` and given the name `"experiment directory name"_"original filename"`. So for instance an experiment in directory  `main_rho_test_time_2021_01_12_10_21_25_sha_694c` would result in a file named `main_rho_test_time_2021_01_12_10_21_25_sha_694c_inlist_project`.

### Linking Output

For single experiments it may be enough to just retrieve the output. For large grids of models though it's useful to apply a little more structure. For this reason RemoteExperiments comes with a *linker*. The linker can read the configuration of a grid of experiments and then search through a set of downloaded experiments for the output of that grid. It then creates a new folder with helpfully-named symlinks to the experiment output for just that grid.

Here's an example:

```python
from experiments.extensions.mesa_parser import mesa_parser
from experiments.base.parse_runs import parse
from experiments.base.linker import sweep_make_symlinks, batch_make_symlinks
from pickle import load, dump
from subprocess import run

repo_dir = '...'
output_dir = 'local/path/to/retrieved/output'
parsed = parse(repo_dir, output_dir, mesa_parser)

symlink_parent_dir = 'place/to/put/symlinks/'
dname = 'place/to/load/batche/configs'
target_file_names = ['mov.mp4','history.data','slurm.out'] # File endings to symlink
config_file_name = 'inlist_project' # Configuration files to check against the sweep config

# Load the batch
sname = 'experiment_2021_01_11_11_40_07.pkl'
sweep = load(open(dname + '/' + sname, 'rb'))

# Make the link directory
symlink_dir = symlink_parent_dir + '/' + 'experiment_1'
run('mkdir ' + symlink_dir, shell=True)
dump(config, open(symlink_dir + '/' + 'base_config.pkl','wb'))

# Gives the link a meaningful name based on configuration
namer = lambda config: str(config['param1']) + '_' + str(config['param2']) 

# Generate symlinks
sweep_make_symlinks(parsed, sweep, namer, config_file_name, target_file_names, symlink_dir)
```

# MESA

I'm primarily developing this tool to enable my own experiments with [MESA](http://mesa.sourceforge.net). For that reason, I've included helper functions in the `extensions` folder. The important ones for use with MESA are `mesa_patcher.make_patch` and `mesa_parser.mesa_parser`.

The `make_patch`  function takes as input a dictionary keyed by parameter names, with parameter settings as values. It returns a function which takes as input a directory and modifies the file `inlist_project` in that directory to contain those parameter settings. As of now it is only able to **modify** existing settings (i.e. the settings must appear somewhere already in the `inlist_project` file).

The `mesa_parser` function takes as input a file path. If the path contains `inlist_project` the parser extracts all settings from it and stores them in a dictionary. It also parses the time and date and short-sha from the path, assuming the path ends in `_time_YYYY_MM_DD_HH_MM_SS_sha_shortSHA_inlist_project`. If the path does not contain `inlist_project` then the parser returns `None`.