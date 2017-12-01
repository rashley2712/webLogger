#!/usr/bin/env python3
import argparse, os, sys
import configHelper

defaultConfiguration = {
	'delay': 10
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Copies a list of files from one directory to another at a steady pace in order to simulate the creation of new content in the folder. ')
	parser.add_argument('sourcefolder', type=str, help='Source directory of the original files.')
	parser.add_argument('-d', '--destinationFolder', type=str, default=".", help='Destination folder to copy the files to. Default is current directory.')
	parser.add_argument('-m', '--mask', type=str, help="Regular expression for file match. Default will be all files. ")
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter')
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
		config.set(arg.set[0], float(arg.set[1]))
		config.save()
		sys.exit()


	sourceFolder = arg.sourcefolder
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
