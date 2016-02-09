import os, subprocess, json, pwd, sys
from flask import Flask,Response,Markup
app = Flask(__name__)

# Load json file
__dir__ = os.path.dirname(os.path.abspath(__file__))                
filepath = os.path.join(__dir__, 'settings.json')                   
if os.path.isfile(filepath):
        with open(filepath) as data_file:                           
                JSONData = json.load(data_file)

# Use the json data for flask
AUTH_KEY = JSONData["auth_key"]
DEBUG = bool(JSONData["debug_mode"])
SHOW_OUTPUT = bool(JSONData["show_output"])
HTTP_HOST = JSONData["host"]
HTTP_PORT = int(JSONData["port"])

# For users using old config files:
try:
	ROOT_WARNING = bool(JSONData["rootwarn"])
except KeyError:
	print """*** NOTICE ***
Your config file is outdated. See the documentation for the new settings.
https://mrtux.org/projects/commander/docs/settings-json.html
"""
	ROOT_WARNING = True
	pass
	# program will continue to run


# Root detection
if ROOT_WARNING == True:
	if pwd.getpwuid == 0:
		print """*** WARNING ***\n
This program will not run as root by default for security purposes. If you
understand the risks of running software as root, set 'rootwarn' in
settings.json to false.\n
Exiting."""
		sys.exit() # Exit the program

#### FUNCTIONS ####
def listCommandsAsJSON():
	""" Lists all commands in the json file as json """
	count = -1
	for item in JSONData["commands"]:
		count = count + 1
		JSONData["commands"][count]["id"] = count
	
	# Return the json
	return json.dumps(JSONData["commands"], sort_keys=True, indent=4, separators=(',', ': '))


def runCommandFromList(command):
	""" Executes a command from a list/tuple of commands. """

	global SHOW_OUTPUT
	global JSONData

	# We are using try here since we don't want the server to error out if a command id
	# doesn't exist
	try:
		command2run = JSONData["commands"][command]["command"]
	except IndexError:
		# Print an error statement. The code will not continue executing so dont worry
		# about the other lines in the function being executed
		return "invalid command id"

	# Split the command at spaces so it can be passed onto something
	# subprocess.call will accept
	split = command2run.split(' ')
	
	# Execute the command in a way that the output is given to the client not shown in a terminal

	if SHOW_OUTPUT == True:
		proc = subprocess.Popen(split, stdout=subprocess.PIPE)
		return proc.stdout.read()
	else:
		subprocess.call(split)

# Settings preview
def getSetting(setting):
	if setting == "debug":
		if DEBUG == True:
			output = "enabled"
		else:
			output = "disabled"
	elif setting == "showoutput":
		if SHOW_OUTPUT == True:
			output = "enabled"
		else:
			output = "disabled"
	else:
			output = "Invalid setting"
	return output

# App Home page
@app.route("/")
def index():
	IndexText = "Commander web server\nSee documentation for information.\n\nSettings:\nDebug mode is " + getSetting('debug')
	IndexText += "\nCommand output is " + getSetting('showoutput')
	return Response(IndexText, mimetype='text/plain')

# Run commands
@app.route("/exec/<authkey>/<int:command_id>")
def commandr(authkey,command_id):
	ResponseText = ""	

	# Show debug information:
	if DEBUG == True:
		ResponseText += "Auth key: " + str(authkey) + "\nCommand-ID: " + str(command_id) + "\n\n"

	# Check if the authkey is correct.
	if authkey == AUTH_KEY:
		# Auth key is correct.
		ResponseText += str(runCommandFromList(command_id))
	else:
		# Auth key isn't correct
		ResponseText += "ERROR: Incorrect authentication key."

	return Response(ResponseText, mimetype='text/plain')

# Page that sends the JSON file so the pebble can read it
@app.route("/send_json/<authkey>")
def send_json(authkey):
	# verify authentication key
	if authkey == AUTH_KEY:
		# auth key is correct, display file.
		ResponseText = listCommandsAsJSON()

	else:
		ResponseText = "ERROR: Incorrect authentication key."
	
	# return response as PLAIN TEXT.
	return Response(ResponseText, mimetype='text/plain')


if __name__ == "__main__":
	app.debug=DEBUG # enable debugging
	app.run(host=HTTP_HOST,port=HTTP_PORT) # run the app
