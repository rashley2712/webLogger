#!/usr/bin/env python3
import argparse, os, sys, re, time, shutil, math, datetime, subprocess
import configHelper, generalUtils, fitsObjects

defaultConfiguration = {
	"webPath": "/home/rashley/webLogger/www",
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Polls the Parameter Notice Board at the WHT and publishes a JSON file for use on the web interfaces.')
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out the database and regenerate all of the metadata.')
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

	noticeBoardCommand = ["ParameterNoticeBoardLister | grep TCS."]
	print("Executing: " + str(noticeBoardCommand))
	response = subprocess.getoutput(noticeBoardCommand)

	for line in response.split('\n'):
		fields = line.split('->')
		parameter = fields[0].strip()[4:]
		typevalue = fields[1].strip().split(' ')
		datatype = typevalue[0]
		value = typevalue[1]
		print("Parameter %s : %s  (%s)"%(parameter, value, datatype))


	