import random, subprocess, json
from flask import Flask,Response,render_template,Markup,jsonify
app = Flask(__name__)

# Load json file
with open('settings.json') as data_file:
	JSONData = json.load(data_file)

# Use the json data for flask
AUTH_KEY = JSONData["auth_key"]
DEBUG = bool(JSONData["debug_mode"])
SHOW_OUTPUT = bool(JSONData["show_output"])
HTTP_HOST = JSONData["host"]
HTTP_PORT = int(JSONData["port"])

#### FUNCTIONS ####
def listCommands():
	""" Lists all commands in a list. """
	# start at -1 since python begins at 0, not 1
	count = -1
	itemstext = "<table class=\"table\"><thead><tr><th>Title</th><th>Command</th></tr></thead><tbody>"

	# put the items in a list
	for item in JSONData["commands"]:
		count = count + 1
		itemstext = itemstext + '<tr><td><a href="/exec/' + AUTH_KEY + '/' + str(count) + '">' + item["title"] + '</a></td><td><code>' + item["command"] + '</code></td></tr>\n'

	itemstext += "</tbody></table>"
	return itemstext

# list commands as json for the pebble app
def listCommandsAsJSON():
	return json.dumps(JSONData["commands"])


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
		return subprocess.check_output(split)
	else:
		subprocess.call(split)

# Settings preview
def currentSettings():
	output = "<p><strong>Debugging:</strong> "
	if DEBUG == True:
		output += "enabled"
	else:
		output += "disabled"
	output += "<br><strong>Command output:</strong> "
	if SHOW_OUTPUT == True:
		output += "enabled"
	else:
		output += "disabled"
	output +="</p>"
	return output

# App Home page
@app.route("/")
def index():
	return render_template('index.html', settings=Markup(currentSettings()))

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

# Page that lists all commands as HTML
@app.route("/list_commands")
def list_commands():
	return render_template("commands.html", commands=Markup(listCommands()))

# Page that sends the JSON file so the pebble can read it
@app.route("/send_json/<authkey>")
def send_json(authkey):
	# verify authentication key
	if authkey == AUTH_KEY:
		# auth key is correct, display file.
		with open("settings.json", "r") as jsonfile:
			ResponseText = jsonfile.read()
	else:
		ResponseText = "ERROR: Incorrect authentication key."
	
	# return response as PLAIN TEXT.
	return Response(ResponseText, mimetype='text/plain')

if __name__ == "__main__":
	app.debug=DEBUG # enable debugging
	app.run(host=HTTP_HOST,port=HTTP_PORT) # run the app
