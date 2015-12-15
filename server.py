import random, subprocess, json
from flask import Flask,Response,render_template,Markup
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
def listCommands(usehtml):
	""" Lists all commands in a list. """
	global JSONData
	
	itemstext = ""

	# start at -1 since python begins at 0, not 1
	count = -1

	# if html is enabled then start the list output with <ol> so we got an ordered list
	if usehtml == True: itemstext = "<table class=\"table\"><thead><tr><th>Title</th><th>Command</th></tr></thead><tbody>"

	# put the items in a list
	for item in JSONData["commands"]:
		count = count + 1
		if usehtml == True:
			# use html output mode
			itemstext = itemstext + '<tr><td><a href="/exec/' + AUTH_KEY + '/' + str(count) + '">' + item["title"] + '</a></td><td><code>' + item["command"] + '</code></td></tr>\n'
		else:
			# don't use html output mode
			itemstext = itemstext + str(count) + ": " + item["title"] + " | " + item["command"] + " \n"

	# if html is enabled, end the ordered html list
	if usehtml == True: itemstext += "</tbody></table>"

	return itemstext

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
# Home page
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

# Administration panel. Pass key to log in for now
@app.route("/list_commands")
def list_commands():
	return render_template("commands.html", commands=Markup(listCommands(True)))

if __name__ == "__main__":
	app.debug=DEBUG # enable debugging
	#app.port=HTTP_PORT
	#app.host=HTTP_HOST
	app.run() # run the app
