

def make_patch(config):
	def patcher(dname):
		fi = open(dname + '/inlist_project', 'r')
		lines = list(l for l in fi)
		fi.close()

		new_lines = []

		for line in lines:
			to_append = line
			for c in config.keys():
				s = line.replace(' ','')
				if c + '=' in s:
					k = line.split('!') # Pull out the comments					
					if len(k) > 1:
						comment = k[-1]
						s = '    ' + c + ' = ' + str(config[c]) + ' !' + comment + '\n'
					else:
						s = '    ' + c + ' = ' + str(config[c]) + '\n'
					to_append = s
			new_lines.append(to_append)

		fi = open(dname + '/inlist_project', 'w')
		fi.write(''.join(new_lines))

	return patcher