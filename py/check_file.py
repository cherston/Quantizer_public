def checker(fname):
	with open(fname, 'rb') as fh: 
		first = next(fh).decode()
		try: 
			fh.seek(-1024,2)
		except: 
			print "file invalid"
			return False 
		last = fh.readlines()[-1].decode()
		print last 
		if last == "</Event>\n" or last == "</Event>" and fname.endswith('.xml'): 
			return True
		else:
			print "file invalid"
			return False 