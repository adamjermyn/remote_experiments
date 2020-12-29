from experiments.extensions.mesa_parser import mesa_parser
from experiments.base.parse_runs import parse

repo_dir = '/Users/ajermyn/Dropbox/Software/Stokes/Stokes_Experiments'
output_dir = '/Users/ajermyn/Dropbox/prototype/runs/runs'

parsed = parse(repo_dir, output_dir, mesa_parser)

print(parsed)