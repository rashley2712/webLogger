#!/usr/bin/env python3
import argparse, os, sys, re, time, shutil, math
import configHelper, generalUtils, fitsObjects

defaultConfiguration = {
	"webPath": "/home/rashley/webLogger/www",
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Loads FITS information from a JSON db file and looks for image data to generate thumbnails.')
	parser.add_argument('-f', '--folder', type=str, default='.', help='Directory containing db file. Default is the current directory.')
	parser.add_argument('-o', '--output', type=str, default='.', help='Directory for the output files. Defaults to ''.''')
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out the database and regenerate all of the metadata.')
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


	fitsDB = fitsObjects.fitsDatabase(os.path.join(sourceFolder, "db.json"), debug=debug)

	if arg.clean:
		fitsDB.clean()
		sys.exit()

	fitsDB.load()


	filesToProcess = []
	# for index in range(len(fitsDB.objectList)):
	for index in range(1):
		if not fitsDB.hasImageData(index):
			filesToProcess.append(fitsDB.objectList[index]['originalFilename'])
			fitsObject = fitsObjects.fitsObject(fitsDB.objectList[index])
			fitsObject.lookForImageData()
