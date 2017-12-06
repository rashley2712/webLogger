#!/usr/bin/env python3
import argparse, os, sys, re, time, shutil, math
import configHelper, generalUtils

defaultConfiguration = {
	'delay': 10,
	"SearchString": ".*.(fits|fits.gz|fits.fz|fit)"
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Copies a list of files from one directory to another at a steady pace in order to simulate the creation of new content in the folder. ')
	parser.add_argument('sourcefolder', type=str, help='Source directory of the original files.')
	parser.add_argument('-d', '--destinationfolder', type=str, default=".", help='Destination folder to copy the files to. Default is current directory.')
	parser.add_argument('-m', '--mask', type=str, help="Regular expression for file match. Default will be ''.*.(fits|fits.gz|fits.fz|fit)'.")
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out all of the files in the destination folder.')

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


	# Get the list of matching filenames in the source folder
	sourceFolder = arg.sourcefolder
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

	# Get a list of existing filenames in the destination folder
	destinationFolder = arg.destinationfolder
	folders = os.walk(destinationFolder)
	subFolders = []
	existingFilenames = []
	for f in folders:
		if debug: print("Folder: %s"%os.path.realpath(f[0]))
		subFolders.append(os.path.realpath(f[0]))
		for file in f[2]:
			m = search_re.match(file)
			if (m):
				existingFilenames.append(file)

	if arg.clean:
		for f in existingFilenames:
			print("removing", f)
			os.remove(os.path.join(destinationFolder, f))
		sys.exit()

	def incrementalItems(firstList, secondList):
		newList = []
		for f in firstList:
			found = False
			for s in secondList:
				if s==f:
					found = True
					continue
			if not found: newList.append(f)
		return newList


	FITSFilenames = incrementalItems(FITSFilenames, existingFilenames)
	FITSFilenames = sorted(FITSFilenames)
	numFiles = len(FITSFilenames)
	print("%d files to copy."%numFiles)
	for index, f in enumerate(FITSFilenames):
		sys.stdout.write("\rCopying from %s to %s\n"%(os.path.join(sourceFolder, f), os.path.join(destinationFolder, f)))
		shutil.copy2(os.path.join(sourceFolder, f), os.path.join(destinationFolder, f))
		filesToGo = numFiles - index
		for i in range(int(config.delay)):
			timeLeft = filesToGo * config.delay - i
			timeLeftMinutes = math.floor(timeLeft/60)
			timeLeftHours = math.floor(timeLeftMinutes/60)
			timeLeftMinutes = timeLeftMinutes % 60
			timeLeftSeconds = timeLeft % 60
			if timeLeftHours>0: sys.stdout.write("\rWaiting for %ds  Total time left: %02d:%02d:%02d   "%(config.delay - i, timeLeftHours, timeLeftMinutes, timeLeftSeconds))
			else: sys.stdout.write("\rWaiting for %ds Total time left: %02d:%02d   "%(config.delay - i, timeLeftMinutes, timeLeftSeconds))
			time.sleep(1)
		sys.stdout.flush()
