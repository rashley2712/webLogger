#!/usr/bin/env python3
import argparse, os, sys, re, time, shutil, math
import configHelper, generalUtils, fitsObjects

defaultConfiguration = {
	'delay': 10,
	"SearchString": ".*.(fits|fits.gz|fits.fz|fit)",
	"webPath": "/home/rashley/webLogger/www",
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Reads the files in the folder and generates metadata from the FITS headers.')
	parser.add_argument('-f', '--folder', type=str, default='.', help='Directory containing the files. Default is the current directory.')
	parser.add_argument('-o', '--output', type=str, default='.', help='Directory for the output files. Defaults to ''.''')
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out the database and regenerate all of the metadata.')


	arg = parser.parse_args()
	debug = False

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

	# Get the list of matching filenames in the source folder
	sourceFolder = arg.folder
	search_re = re.compile(config.SearchString)
	folders = os.walk(sourceFolder)
	subFolders = []
	FITSFilenames = []
	for f in folders:
		if debug: print("Folder: %s"%os.path.realpath(f[0]))
		subFolders.append(os.path.realpath(f[0]))
		for file in f[2]:
			m = search_re.match(file)
			if (m):
				FITSFilenames.append(file)

	FITSFilenames = sorted(FITSFilenames)

	fitsDB = fitsObjects.fitsDatabase(os.path.join(arg.output, "db.json"), debug=False)
	fitsDB.dataPath = sourceFolder
	if arg.clean:
		fitsDB.clean()
		sys.exit()

	fitsDB.load()

	newFiles = generalUtils.incrementalItems(FITSFilenames, fitsDB.getFilenames())

	if len(newFiles)==0:
		print("There are no new files.")
		sys.exit()
	if len(newFiles)==1: print("There is 1 new file:")
	else: print("There are %d new files:"%len(newFiles))

	for index, f in enumerate(newFiles):
		print("adding ", f)
		fitsDB.addObject(f)
		fitsDB.addFITSData(f)
		# if index>=0: break

	fitsDB.save()
	fitsDB.compress()
