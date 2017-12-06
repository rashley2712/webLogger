import json, os, astropy

class fitsDatabase:
	def __init__(self):
		self.dbFilename = "db.json"
		self.objectList = []
		self.debug = True

	def addObject(self, filename):
		newObject = { "filename" : filename }
		self.objectList.append(newObject)

	def save(self):
		outputfile = open(self.dbFilename, 'wt')
		json.dump(self.objectList, outputfile, indent = 4)
		outputfile.close()

	def load(self):
		try:
			inputfile = open(self.dbFilename, 'rt')
			self.objectList = json.load(inputfile)
			inputfile.close()
		except FileNotFoundError:
			if self.debug: print("Could not load the database file %s."%self.dbFilename)

	def addFITSData(self, filename):
		targetObject = None
		for index, o in enumerate(self.objectList):
			if o['filename'] == filename: targetObject = o
		targetObject['data'] = 'FITSfile'


	def clean(self):
		try:
			os.remove(self.dbFilename)
		except FileNotFoundError:
			if self.debug: print("No file to clean.")

	def getFilenames(self):
		return sorted([ o['filename'] for o in self.objectList])
