#!/usr/bin/env python3
import argparse, os, sys, re, time, shutil, math
import configHelper, generalUtils, fitsObjects

defaultConfiguration = {
	"webPath": "/home/rashley/webLogger/www",
	}

def changeExtension(filename, newExtension):
	return os.path.splitext(filename)[0] + "." + newExtension



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Copy the original FITS file to the web folder.')
	parser.add_argument('-f', '--folder', type=str, default='.', help='Directory containing db file. Default is the current directory.')
	parser.add_argument('-o', '--output', type=str, default='.', help='Directory for the output files. Defaults to ''.''')
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--force', action='store_true', help='Force copy of all files (not implemented yet).')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out the destination folder of all copied FITS files (Not implemented yet).')
	arg = parser.parse_args()
	debug = True

	config = configHelper.config(debug = False)
	if not config._loaded:
		config.setProperties(defaultConfiguration)
		config.save()

	if arg.clear:
		config.clear()
		sys.exit()

	if arg.show:
		print(config)
		sys.exit()

	if arg.set is not None:
		print(arg.set)
		if len(arg.set)!=2:
			print("Please specify a parameter and a value.")
			sys.exit()
		try: config.set(arg.set[0], float(arg.set[1]))
		except ValueError: config.set(arg.set[0], arg.set[1])
		config.save()
		sys.exit()

	sourceFolder = arg.folder
	destinationFolder = arg.output

	fitsDB = fitsObjects.fitsDatabase(os.path.join(sourceFolder, "db.json"), debug=debug)

	fitsDB.load()

	modifiedCount = 0

	if arg.clean:
		for f in fitsDB.objectList:
			try:
				rmFile = os.path.join(destinationFolder, f['filename'])
				if os.path.exists(rmFile):
					print("Deleting file: " + rmFile)
					os.remove(rmFile)
					f['originalavailable'] = False
			except:
				print("Could not delete the file")

		fitsDB.save()
		fitsDB.compress()

		sys.exit()

	for f in fitsDB.objectList:
		try:
			copyStatus = f['originalavailable']
		except:
			copyStatus = False;
		if copyStatus:
			print("Already copied")
		else:
			source = f['originalFilename']
			destination = os.path.join(destinationFolder, f['filename'])
			print(source + " --> writing to: " + destination)
			shutil.copy(source, destination)
			shutil.copystat(source, destination)
			f['originalavailable'] = True

	fitsDB.save()
	fitsDB.compress()
	sys.exit()









	for index in range(len(fitsDB.objectList)):
		if not fitsDB.hasImageData(index) or arg.force:
			fitsObject = fitsObjects.fitsObject(fitsDB.objectList[index])
			if fitsObject.lookForImageData():
				fitsObject.getBoostedImage()
				outputFilename = os.path.join(sourceFolder, changeExtension(fitsDB.objectList[index]['filename'], "png"))
				thumbnailFilename = os.path.join(sourceFolder, "thumb_" + changeExtension(fitsDB.objectList[index]['filename'], "png"))
				print("Will write the png image to %s"%outputFilename)
				fitsObject.writeAsPNG(True, outputFilename)
				fitsObject.createThumbnail(thumbnailFilename)
				imageData = fitsObject.getImageMetadata()
				print("Image metadata: " + str(imageData))
				fitsDB.addImageMetadata(index, imageData)
				modifiedCount+=1
			else:
				print("No image data here...")
	print("Produced image data for %d files."%modifiedCount)
	if modifiedCount>0:
		fitsDB.save()
		fitsDB.compress()
