import json, os, sys, numpy
import astropy
from astropy.io import fits

class fitsObject:
	def __init__(self, properties):
		self.properties = properties
		self.debug = True
		self.images = []

	def lookForImageData(self):
		try:
			filename = self.properties['originalFilename']
			hdulist = fits.open(filename)
		except Exception as e:
			print("Unexpected error:", sys.exc_info()[0])
			print(e)
			print("Error opening the FITS file.")
		if self.debug: print("Info: ", hdulist.info())
		for index, h in enumerate(hdulist):
			if type(h.data) is numpy.ndarray:
				imageObject = {}
				imageObject['data'] = h.data
				imageObject['size'] = numpy.shape(h.data)
				self.images.append(imageObject)
				if len(imageObject['size'])<2:
					if self.debug: print("Data is one-dimensional. Not valid.")
					continue;
				if self.debug: print("%d: Found image data of dimensions (%d, %d)"%(index, imageObject['size'][0], imageObject['size'][1]))
			else:
				if self.debug: print("%d: This card has no image data"%index)
				continue
		if len(images)==0:
			if self.debug: print "Could not find any valid FITS data for %s"%filename
			return False
		if len(images)>1:
			self.combineImages(images)
		else:
			self.fullImage = images[0]
			self.size = numpy.shape(self.fullImage['data'])

		return True


class fitsDatabase:
	def __init__(self, filename=None, debug=False):
		if filename is None: self.dbFilename = "db.json"
		else: self.dbFilename = filename
		self.dataPath = '.'
		self.objectList = []
		self.debug = debug

	def addObject(self, filename):
		newObject = { "filename" : filename }
		newObject['unixtime'] = os.path.getmtime(os.path.join(self.dataPath, filename))
		newObject['originalFilename'] = os.path.join(self.dataPath, filename)
		self.objectList.append(newObject)

	def save(self):
		if self.debug: print("Writing dbfile to %s"%self.dbFilename)
		directory = os.path.dirname(self.dbFilename)
		if not os.path.exists(directory):
			os.makedirs(directory)
		outputfile = open(self.dbFilename, 'wt')
		json.dump(self.objectList, outputfile, indent = 4)
		outputfile.close()

	def hasImageData(self, index):
		fitsObject = self.objectList[index]
		if 'imagedata' not in fitsObject.keys(): return False
		return True


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
			print("Removed %s"%self.dbFilename)
		except FileNotFoundError:
			if self.debug: print("No file to clean.")

	def getFilenames(self):
		return sorted([ o['filename'] for o in self.objectList])
