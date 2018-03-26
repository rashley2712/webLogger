#!/usr/bin/env python3
import argparse, os, sys, re, time, shutil, math, datetime, subprocess
import configHelper, generalUtils, fitsObjects

defaultConfiguration = {
	"SearchString": ".*.(fits|fits.gz|fits.fz|fit)",
	"webPath": "/home/rashley/webLogger/www",
	"rootDataPath": "/home/rashley/webLogger/"   		# This is will be /obsdata in the production version
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Reads the files in an ING obsdata folder an triggers the other programs to create the webLogger files.')
	parser.add_argument('-d', '--date', type=str, default='today', help='The date to the run. Format is YYYYMMDD. Leave blank to perform for ''today'' (starting at the most recent midday).')
	parser.add_argument('telescope', type=str, help='Telescope. Options are WHT or INT.')
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out the database and regenerate all of the metadata.')
	parser.add_argument('--force', action='store_true', help='Force regeneration of the png and thumbnails.')
	parser.add_argument('--noimages', action='store_true', help='Don''t process the image data.')
	parser.add_argument('--copy', action='store_true', help='Copy original FITS files to the web archive.')

	arg = parser.parse_args()
	debug = False
	installPath = os.path.dirname(os.path.realpath(__file__))

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

	if arg.date=="today":
		logDateTime = datetime.datetime.now()
		if logDateTime.hour<12:
			logDateTime = logDateTime - datetime.timedelta(days=1)
		logDate = logDateTime.strftime("%Y%m%d")
	else: logDate = arg.date

	if arg.telescope=="WHT":
		telPath = 'whta'
	elif arg.telescope=="INT":
		telPath = 'inta'
	else:
		print("Please specify either 'INT' or 'WHT' for the telescope name.")
		sys.exit()

	print("Performing night log generation for %s on %s"%(arg.telescope,logDate))

	dataPath = os.path.join(config.rootDataPath, telPath, logDate)
	print("Looking for files in : %s"%dataPath)

	outputPath = os.path.join(config.webPath, telPath, logDate)
	print("Writing webLogger files to: %s"%outputPath)

	metadataCommand = [installPath + "/getMetadata.py"]
	metadataCommand.append('-f')
	metadataCommand.append(dataPath)
	metadataCommand.append('-o')
	metadataCommand.append(outputPath)
	if arg.clean:
		print("Performing clean")
		metadataCommand.append('--clean')

	print("Executing: " + str(metadataCommand))
	subprocess.call(metadataCommand)
	if arg.clean: sys.exit()

	if arg.noimages: sys.exit()

	imageCommand = [installPath + "/getImageData.py"]
	imageCommand.append('-f')
	imageCommand.append(outputPath)
	if arg.force:
		print("Forcing image regeneration")
		imageCommand.append('--force')


	subprocess.call(imageCommand)

	if arg.copy:
		fitsCopyCommand = [installPath + "/copyOriginals.py"]
		fitsCopyCommand.append('-o')
		fitsCopyCommand.append(outputPath)
		fitsCopyCommand.append('-f')
		fitsCopyCommand.append(outputPath)
		subprocess.call(fitsCopyCommand)
