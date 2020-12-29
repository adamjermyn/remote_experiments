from grids import make_grid

# Makes a 3D grid with one two-parameter dimension (nf,nl) and two one-parameter dimensions (mesh and frosh).
dimensions = {}
dimensions[('nf','nl')] = [(x,x) for x in (0.1,0.2,0.3,0.4,0.5)]
dimensions[('mesh',)] = [(0.1,),(0.2,)]
dimensions[('frosh',)] = [('.true.',), ('.false.',)]
make_grid({}, dimensions)