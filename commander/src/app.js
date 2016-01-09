var UI = require('ui');
var ajax = require('ajax');
var Settings = require('settings');
var Voice = require("ui/voice");

// get pebble revision
if(Pebble.getActiveWatchInfo) {
	var watchinfo= Pebble.getActiveWatchInfo();
	var platform=watchinfo.platform;
} else {
	platform="aplite";
}

// Set a configurable with the open callback
Settings.config(
	{ url: 'https://c0decat.github.io/pebble-commander/settings/' },
	function(e) {
		console.log('opening configurable');
	},
	function(e) {
		console.log('closed configurable');
	}
);


var CONTROL_URL = Settings.option('server'); 
var AUTH_KEY = Settings.option('authkey');
var OUTPUT_MODE = Settings.option('commandoutput');

var APP_VERSION = "1.5";
var ABOUT_TEXT = "Author: Colin Murphy (mrtux@riseup.net)\n\nWebsite: www.mrtux.org/projects/commander";

// Initial window
var initWindow = new UI.Card({
	title: "Pebble Commander",
	scrollable: true,
	style: 'small',
	body: "Getting commands list..."
});
initWindow.show();


if (!CONTROL_URL || !AUTH_KEY) {
	// App not configured
	initWindow.title("App not configured");
	initWindow.body("Enter in the server IP and password on your phone. When done, restart this app.");
	
	if (platform == 'basalt') {
		initWindow.backgroundColor('red');
	}
}
else
{
	// all is good, you can run the app
	runApp();
}

function sendCommand(id, name) {
	// Show a card showing that the command was executed
	var detailCard = new UI.Card({
		backgroundColor: 'white',
		textColor: 'black',
		style: 'small',
		scrollable: true,
		title: name,
		subtitle: "Sending command to server",
		body: ""
	});

	// Show the new Card
	detailCard.show();
	
	ajax({url: 'http://' + CONTROL_URL + "/exec/" + AUTH_KEY + "/" + id, type: 'plain'},
		function (data) {
			detailCard.subtitle("Command sent");
			if (OUTPUT_MODE === true) {
				detailCard.body(data);
			}
			else
			{
				detailCard.body("");
			}
			if (platform == 'basalt') {
				detailCard.backgroundColor('green');
			}

			// hide this after 2 seconds and return to the menu
			setTimeout(function() {detailCard.hide();}, 2000);
		},
		function (error) {
			detailCard.title("Data retrieval failed");
			detailCard.body(error);
			detailCard.subtitle("");
			if (platform == 'basalt') {
				detailCard.backgroundColor('red');
			}
		}
	);
}



function runApp() {
	
	ajax({url: 'http://' + CONTROL_URL + "/send_json/" + AUTH_KEY, type: 'json'},
		function(json) {
			// Data retrieval worked, hide this and show the menu!
			var commandMenu = new UI.Menu({
				backgroundColor: platform == 'aplite' ? 'white' : '#AAAAAA',
				textColor: 'black',
				highlightBackgroundColor: platform == 'aplite' ? 'black' : 'blue',
				highlightTextColor: 'white',
				fullscreen: false,
				sections: platform == 'aplite' ? 
				[{
					title: 'Commands',
					items: json
				},{
					title: 'Commander',
					items: [
						{"title": "Connection info"},
						{"title": "About", "subtitle": "Version " + APP_VERSION}
					]
				}] :
				[{
					items: [{"title": "Voice command", "subtitle": "Select then talk"}]	
				},{
					title: 'Commands',
					items: json
				},{
					title: 'Commander',
					items: [
						{"title": "Connection info"},
						{"title": "About", "subtitle": "Version " + APP_VERSION}
					]
				}]
			});
			
			commandMenu.show();
			initWindow.hide();
			
			// Add a click listener for select button click
			commandMenu.on('select', function(event) {
				console.log('Selected item #' + event.itemIndex + ' of section #' + event.sectionIndex);
				console.log('The item is titled "' + event.item.title + '"');
				
				// Item index 0 (list 1) is the voice command option
				if (event.sectionIndex === 0) {
					
					// Dictate voice then run the command if it worked out
					Voice.dictate('start', true, function(e) {
						if (e.err) {
							console.log('Error: ' + e.err);
							return;
						}
						console.log('Transcription: ' + e.transcription);
						
						// search for the name in the list of commands
						for (var i = 0; i < json.length; i++){
							// put the text in lowercase so it can be matched
							var transcription = e.transcription.toLowerCase();
							var itemTitle = json[i].title.toLowerCase();
							
							if (itemTitle == transcription || itemTitle.indexOf(transcription) >= 0) {
								var voiceCommand = json[i].id;
								console.log('Voice command: ' + voiceCommand);
								sendCommand(voiceCommand, json[i].title);
							}
						}
					});

				}
				// If the item is in the 2nd list, its a command
				else if (event.sectionIndex === 1 ) {
					commandMenu.fullscreen(false);
					sendCommand(json[event.itemIndex].id, json[event.itemIndex].title);
				}
				else
				{
					// selection index isn't 0 so this is a different type :)
					
					var infoMenu = new UI.Menu({
						backgroundColor: '#AAAAAA',
						textColor: 'black',
						highlightBackgroundColor: 'blue',
						highlightTextColor: 'white',
					});
					
					if (event.itemIndex === 0) {
						// an id if 0 is the connection settings card
						infoMenu.sections([{
							title: "Connection info",
							items: [
								{"title": "Server", "subtitle": CONTROL_URL},
								{"title": "Auth key", "subtitle": AUTH_KEY}
							]
						}]);
						infoMenu.show();
					}
					else
					{
						// an id of 1 is the about app card
						var aboutCard = new UI.Card({
							style: "small",
							scrollable: true,
							title: ">_ Commander",
							subtitle: "Version " + APP_VERSION,
							body: ABOUT_TEXT
						});
						if (platform == 'basalt') {
							aboutCard.titleColor("#00AA00");
							aboutCard.backgroundColor("#AAAAAA");
							aboutCard.bodyColor("black");
							aboutCard.subtitleColor("#555555");
						}
						aboutCard.show();
					}
				}
			});
		},
		function(error) {
			console.log('Ajax failed: ' + error);
			initWindow.title('Data retrieval failed');
			initWindow.body(error);
			if (platform == 'basalt') {
				initWindow.backgroundColor('red');
				initWindow.textColor('black');
			}
		}
	);
}
