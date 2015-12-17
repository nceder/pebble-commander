var UI = require('ui');
var ajax = require('ajax');
var Settings = require('settings');


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
  
	//when you press the select button, restart the app
	initWindow.on('select', function(event) {
		runApp();
	});
}
else
{
	// all is good, you can run the app
	runApp();
}


function runApp() {
	ajax({url: 'http://' + CONTROL_URL + "/send_json/" + AUTH_KEY, type: 'json'},
		function(json) {
			// Data retrieval worked, hide this and show the menu!
			var commandMenu = new UI.Menu({
				backgroundColor: 'white',
				textColor: 'black',
				highlightBackgroundColor: 'blue',
				highlightTextColor: 'white',
				sections: [{
					title: 'Commands',
					items: json
				}]
			});
			commandMenu.show();
			initWindow.hide();
		
			// Add a click listener for select button click
			commandMenu.on('select', function(event) {
			// Show a card showing that the command was executed
			var detailCard = new UI.Card({
				backgroundColor: 'white',
				textColor: 'black',
				style: 'small',
				scrollable: true,
				title: json[event.itemIndex].title,
				subtitle: "Sending command to server",
				body: ""
			});

			// Show the new Card
			detailCard.show();

			ajax({url: 'http://' + CONTROL_URL + "/exec/" + AUTH_KEY + "/" + json[event.itemIndex].id, type: 'plain'},
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
					setTimeout(function() {detailCard.hide(); commandMenu.show();}, 2000);
				},
				function (error) {
					detailCard.title("Data retrieval failed");
					detailCard.body(error);
					detailCard.subtitle("");
					if (platform == 'basalt') {
						detailCard.backgroundColor('red');
					}
				});
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