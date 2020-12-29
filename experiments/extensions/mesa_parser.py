
def mesa_parser(fname):
	if 'inlist_project' in fname:	
		parsed = {}
		fi = open(fname, 'r')
		for line in fi:
			if '!' in line:
				line = line[:line.index('!')]
			if '=' in line:
				s = line.split('=')
				s = list(li.strip() for li in s)
				param = s[0]
				value = s[1]
				parsed[param] = value
		return parsed
	else:
		return None
