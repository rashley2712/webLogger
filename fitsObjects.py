import json, os, sys
import astropy
from astropy.io import fits

class fitsDatabase:
	def __init__(self, filename=None, debug=False):
		if filename is None: self.dbFilename = "db.json"
		else: self.dbFilename = filename
		self.dataPath = '.'
		self.objectList = []
		self.debug = debug

	def addObject(self, filename):
		newObject = { "filename" : filename }
		self.objectList.append(newObject)

	def save(self):
		if self.debug: print("Writing dbfile to %s"%self.dbFilename)
		directory = os.path.dirname(self.dbFilename)
		if not os.path.exists(directory):
			os.makedirs(directory)
		outputfile = open(self.dbFilename, 'wt')
		json.dump(self.objectList, outputfile, indent = 4)
		outputfile.close()

	def showDataTypes(self):
		for o in self.objectList:
			print(o)

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
		if targetObject is None: return False

		allHeaders = {}
		try:
			hdulist = fits.open(os.path.join(self.dataPath, targetObject['filename']))
			if self.debug: print("Info: ", hdulist.info())
			# Grab all of the FITS headers I can find
			for card in hdulist:
				for key in card.header.keys():
					allHeaders[key] = card.header[key]
					if type(card.header[key]) is astropy.io.fits.header._HeaderCommentaryCards:
						allHeaders[key] = str(card.header[key])

			hdulist.close(output_verify='ignore')
		except astropy.io.fits.verify.VerifyError as e:
			print("WARNING: Verification error", e)

		except Exception as e:
			print("Unexpected error:", sys.exc_info()[0])
			print(e)
			print("Could not find any valid FITS data for %s"%filename)
			return False



		for key in allHeaders.keys():
			targetObject[key] = allHeaders[key]


	def clean(self):
		try:
			os.remove(self.dbFilename)
		except FileNotFoundError:
			if self.debug: print("No file to clean.")

	def getFilenames(self):
		return sorted([ o['filename'] for o in self.objectList])
