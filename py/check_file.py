def checker(fname):
	with open(fname, 'rb') as fh: 
		first = next(fh).decode()
		fh.seek(-1024,2)
		last = fh.readlines()[-1].decode()
		print last 
		if last == "</Event>\n" or last == "</Event>": 
			return True
		else:
			print "file invalid"
			return False 