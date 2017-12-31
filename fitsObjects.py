import json, os, sys, numpy
import astropy
from astropy.io import fits
from PIL import Image,ImageDraw,ImageFont

def changeExtension(filename, newExtension):
	return os.path.splitext(filename)[0] + "." + newExtension


class fitsObject:
	def __init__(self, properties):
		self.properties = properties
		self.debug = True
		self.images = []
		self.hasImage = False

	def getImageMetadata(self):
		imageMetadataObject = {}
		imageMetadataObject['hasImage'] = self.hasImage
		if not self.hasImage: return imageMetadataObject
		imageMetadataObject['src'] = self.imageSrc
		imageMetadataObject['size'] = self.size
		imageMetadataObject['tb_src'] = self.thumbnailSrc
		return imageMetadataObject


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
		if len(self.images)==0:
			if self.debug: print("Could not find any valid FITS data for %s"%filename)
			return False
		if len(self.images)>1:
			self.combineImages(images)
		else:
			self.fullImage = self.images[0]
			self.size = numpy.shape(self.fullImage['data'])

		self.hasImage = True
		return True

	def getBoostedImage(self):
		""" Returns a normalised array where lo percent of the pixels are 0 and hi percent of the pixels are 255 """
		hi = 99
		lo = 20
		imageData = self.fullImage['data']
		data = numpy.copy(self.fullImage['data'])
		max = data.max()
		dataArray = data.flatten()
		pHi = numpy.percentile(dataArray, hi)
		pLo = numpy.percentile(dataArray, lo)
		range = pHi - pLo
		scale = range/255
		data = numpy.clip(data, pLo, pHi)
		data-= pLo
		data/=scale
		self.boostedImage = data
		self.boostedImageExists = True
		return data

	def writeAsPNG(self, boosted=False, filename = None):
		imageData = numpy.copy(self.fullImage['data'])
		if boosted==True:
			if not self.boostedImageExists: imageData = self.getBoostedImage()
			else: imageData = self.boostedImage
		imgData = numpy.rot90(imageData, 3)
		imgSize = numpy.shape(imgData)
		imgLength = imgSize[0] * imgSize[1]
		testData = numpy.reshape(imgData, imgLength, order="F")
		img = Image.new("L", imgSize)
		palette = []
		for i in range(256):
			palette.extend((i, i, i)) # grey scale
			img.putpalette(palette)
		img.putdata(testData)

		if filename==None:
			outputFilename = changeExtension(self.properties['filename'], "png")
		else:
			outputFilename = filename

		if self.debug: print ("Writing PNG file: " + outputFilename)
		self.imageSrc = os.path.basename(outputFilename)
		img.save(outputFilename, "PNG", clobber=True)

	def createThumbnail(self, filename = None, size=128):
		if not self.boostedImageExists: imageData = self.getBoostedImage()
		else: imageData = self.boostedImage

		imgData = numpy.rot90(imageData, 3)
		imgSize = numpy.shape(imgData)
		imgLength = imgSize[0] * imgSize[1]
		testData = numpy.reshape(imgData, imgLength, order="F")
		img = Image.new("L", imgSize)
		palette = []
		for i in range(256):
			palette.extend((i, i, i)) # grey scale
			img.putpalette(palette)
		img.putdata(testData)
		thumbnailSize = (size, size)
		img.thumbnail(thumbnailSize, Image.ANTIALIAS)
		if filename==None:
			outputFilename = "thumb_" + changeExtension(self.filename, "png")
		else:
			outputFilename = filename

		if self.debug: print ("Writing thumbnail file: " + outputFilename)
		img.save(outputFilename, "PNG", clobber=True)
		self.thumbnailSrc = os.path.basename(outputFilename)


	def combineImages(self, images):
		if self.debug: print("Combining %d multiple images."%len(images))
		WFC = False
		try:
			instrument = self.properties['INSTRUME']
			print("Instrument detected:", instrument)
			if instrument=='WFC': WFC = True
		except KeyError:
			pass

		# Reduce the images sizes by 1/4
		for num, i in enumerate(images):
			percent = 25
			if self.debug: print("Shrinking image %d by %d percent."%(num, percent))
			i['data'] = scipy.misc.imresize(self.boostImageData(i['data']), percent)
			i['size'] = numpy.shape(i['data'])
			if self.debug: print("New size:", i['size'])

		if WFC:
			# Custom code to stitch the WFC images together
			CCD1 = images[0]
			CCD2 = images[1]
			CCD3 = images[2]
			CCD4 = images[3]
			width = CCD1['size'][1]
			height = CCD1['size'][0]
			fullWidth = width + height
			fullHeight = 3 * width
			if self.debug: print("WFC width", fullWidth, "WFC height", fullHeight)
			fullImage = numpy.zeros((fullHeight, fullWidth))
			CCD3data = numpy.rot90(CCD3['data'], 3)
			fullImage[0:width, width:width+height] = CCD3data
			CCD2data = CCD2['data']
			fullImage[width:width+height, 0:width] = CCD2data
			CCD4data = numpy.rot90(CCD4['data'], 3)
			fullImage[width:2*width, width:width+height] = CCD4data
			CCD1data = numpy.rot90(CCD1['data'], 3)
			fullImage[2*width:3*width, width:width+height] = CCD1data
			fullImage = numpy.rot90(fullImage, 2)
		else:
			totalWidth = 0
			totalHeight = 0
			for i in images:
				totalWidth+= i['size'][1]
				totalHeight+=i['size'][0]
			if self.debug: print("potential width, height", totalWidth, totalHeight)
			if totalWidth<totalHeight:
				if self.debug: print("Stacking horizontally")
				maxHeight = 0
				for i in images:
					if i['size'][0]>maxHeight: maxHeight = i['size'][0]
				fullImage = numpy.zeros((maxHeight, totalWidth))
				if self.debug: print("Full image shape", numpy.shape(fullImage))
				segWstart = 0
				segHstart = 0
				for num, i in enumerate(images):
					segWidth = i['size'][1]
					segHeight = i['size'][0]
					segWend = segWstart + segWidth
					segHend = segHstart + segHeight
					fullImage[segHstart:segHend, segWstart: segWend] = i['data']
					segWstart+= segWidth


		self.fullImage['data'] = fullImage
		self.fullImage['size'] = numpy.shape(fullImage)
		self.size = numpy.shape(fullImage)
		if self.debug: print("Final size:", self.size)



class fitsDatabase:
	def __init__(self, filename=None, debug=False):
		if filename is None: self.dbFilename = "db.json"
		else: self.dbFilename = filename
		self.dataPath = '.'
		self.objectList = []
		self.debug = debug

	def addImageMetadata(self, index, data):
		self.objectList[index]['imageData'] = data

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
		if 'imageData' not in fitsObject.keys(): return False
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
