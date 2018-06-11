#!/usr/bin/env python3
import argparse, sys, re, subprocess, os, datetime, time
import configHelper, json

defaultConfiguration = {
	"webPath": "/var/www/webLogger",
	}


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Polls the Parameter Notice Board at the WHT and publishes a JSON file for use on the web interfaces.')
	parser.add_argument('-t', '--wait', type=int, default=1, help='Time to refresh (in seconds). Default is 1.')
	parser.add_argument('-n', '--number', type=int, default=100, help='Number of iterations. Default is 100.')
	parser.add_argument('--verbose', action='store_true', help='Show the info that is being push to the web server area.')
	parser.add_argument('--show', action='store_true', help='Showed stored configuration and exit.')
	parser.add_argument('--clear', action='store_true', help='Clear stored configuration and exit.')
	parser.add_argument('--set', type=str, nargs='*', help='Set a parameter.')
	parser.add_argument('--clean', action='store_true', help='Clean out the database and regenerate all of the metadata.')
	arg = parser.parse_args()
	
	debug = False
	if arg.verbose:
		debug = True

	sleep = arg.wait
	
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

	noticeBoardCommand = ["ParameterNoticeBoardLister | grep -E 'TCS\.|WEATHER\.WHT'"]
	if debug: print("Executing: " + str(noticeBoardCommand))
	response = subprocess.getoutput(noticeBoardCommand)
	
	for iteration in range(arg.number):
		print("Iteration %d of %d"%(iteration+1, arg.number))
		now = datetime.datetime.now()
		# Extract the TCS information
		if debug: print("TCS Info")
		TCSObject = {"Date" : str(now)}
		for line in response.split('\n'):
			if line[:3] != "TCS": continue
			fields = line.split('->')
			parameter = fields[0].strip()[4:]
			typevalue = fields[1].strip()
			datatype = typevalue[:typevalue.find(' ')]
			value = typevalue[typevalue.find(' ')+1:]
			m = re.search('\{(.*?)\}', value)
			if m is not None:
				value = value[1:-1]
				m = re.search('\{(.*?)\}', value)
				if m is not None:
					value = value[1:-1]
		
			try:
				value = float(value)
			except ValueError:
				value = str(value)

			if debug: print("Parameter %s : %s  (%s)"%(parameter, value, type(value)))
			TCSObject[parameter] = value

		if debug: print("\nWeather info:")
		
		# Extract the WHT weather information
		weatherObject = {}
		weatherObject = {"Date" : str(now)}
		for line in response.split('\n'):
			if line[:7] != "WEATHER": continue
			fields = line.split('->')
			parameter = fields[0].strip()[12:]
			typevalue = fields[1].strip()
			datatype = typevalue[:typevalue.find(' ')]
			value = typevalue[typevalue.find(' ')+1:]
			try:
				value = float(value)
			except ValueError:
				value = str(value)

			if debug: print("Parameter %s : %s  (%s)"%(parameter, value, type(value)))
			weatherObject[parameter] = value
		if debug: print()
			
		# Publish both objects as JSON files
		TCSjson = "tcs.json"
		outputFilename = os.path.join(config.webPath, TCSjson)
		if debug: print("Writing TCS data to: %s"%outputFilename)
		outputFile = open(outputFilename, 'wt')
		json.dump(TCSObject, outputFile, indent = 4)
		outputFile.close()

		weatherjson = "weather.json"
		outputFilename = os.path.join(config.webPath, weatherjson)
		if debug: print("Writing TCS data to: %s"%outputFilename)
		outputFile = open(outputFilename, 'wt')
		json.dump(weatherObject, outputFile, indent = 4)
		outputFile.close()

		time.sleep(sleep)