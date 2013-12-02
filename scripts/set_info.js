function setHome(home_id) {
	// Possibly rename to setHomeRadio? So that we can set home from search results as well...
	var $radio = $('#' + home_id);
	var home = $radio.attr('data-homename');
	console.log('this clicked: ', home, home_id)
	$('#home').val(home);
	$('#home_id').val(home_id);
	$('#home_okay').html('<code>' + home + '</code>');
	$('#home_button').hide();
	$('#home_reset').show();
	renderSubmitButton();
};

function setHomeFromSearch(home_id) {
	//will set home from search id's
	
	//sim to funct!
	var $autoCompChoice = $('#ch' + home_id);
	var home = $autoCompChoice.attr('data-homename');
	console.log('this clicked: ', home, home_id)
	$('#home').val(home);
	$('#home_id').val(home_id);
	$('#home_okay').html('<code>' + home + '</code>');
	$('#home_button').hide();
	$('#home_reset').show();
	renderSubmitButton();
	
	//at the end go back to #setInfo!
	$.mobile.changePage('#setInfo')
}

function setTimer() {
	//Modify to pull from search results or checkbox
	var timestr = $('#set_time').val();
	var time = new Date;
	var timesplit = timestr.split(':');
	var hours = timesplit[0];
	var mins = timesplit[1];
	console.log("timesplit = " + timesplit + ' hours = ' + hours);
	console.log("day = " +  time.getDate());
	
	if (time.getHours() > hours ) {
		time.setDate(time.getDate() + 1)
		console.log('it was!')
	}
	
	console.log('newday = ' + time.getDate())
	
	time.setHours(hours);
	time.setMinutes(mins);
	console.log('this clicked: ', time);
	var humanThen = time.toLocaleTimeString();
	var then = time.getTime();
	var now = new Date;
	//var then = hours + ':' + minutes + ' ' + merid
	$('#nowSubmit').val(now.getTime());
	$('#thenSubmit').val(then);
	$('#humanTime').val(humanThen);
	
	console.log('then = ' + then);
	console.log('now = ' + now.getTime());
	console.log('diff = ' + (then - now));
	console.log(humanThen);
	//$('#time_id').val(time_id); // possibly this will be the a useable storable value for time?
	$('#time_okay').html('<code>' + humanThen + '</code>');
	// a human readable value...
	$('#time_button').hide();
	$('#time_reset').show();
	renderSubmitButton();
};

function setWager() {
	//Modify to pull from search results or checkbox
	var humanWager = $('#amount').val();
	var wager = $("#amount").attr('data-wagamount');
	console.log('this clicked: ', wager, humanWager)
	$('#wager').val(wager);
	$('#human_wager').val(humanWager);
	//$('#wager_id').val(wager_id); // possibly this will be the a useable storable value for wager?
	$('#wager_okay').html('<code>' + humanWager + '</code>');
	// a human readable value...
	$('#wager_button').hide();
	$('#wager_reset').show();
	renderSubmitButton();
};

function setCharity(charity_id) {
	// Possibly rename to setCharityRadio? So that we can set home from search results as well...
	var $radio = $('#' + charity_id);
	var charity = $radio.attr('data-charityname');
	console.log('this clicked: ', charity, charity_id)
	$('#charity').val(charity);
	$('#charity_id').val(charity_id);
	$('#charity_okay').html('<code>' + charity + '</code>, a charity you HATE!');
	$('#charity_button').hide();
	$('#charity_reset').show();
	renderSubmitButton();
};

function setRobot() {
	var robotCB = $('#robot_cb');
	var robotIP = $('#robot_pref');
	
	if (robotCB.is(':checked')) {
		robotIP.val('true')
	}
	else {
		robotIP.val('')
	}
	console.log('robot_pref val = ' + robotIP.val())
	
}

function renderSubmitButton() {
	console.log('trying to submit')
	if ($('#thenSubmit').val() && $('#charity').val() && $('#wager').val() && $('#home').val()) {
		$('#submit_button').show()
	}
}



function autoComplete() {
	var $ul = $("#autoCompList"), html = "", value = $('#autocomplete').val();
	var latlon = $('#latlon').val();
	//testval = '40.7508390901,-73.9183463601'

	console.log('latlon = ' + latlon)
	$.ajax({
		url : "/autocomp_homes",
		dataType : "json",
		//crossDomain : true,
		data : {
			term : value,
			latlon : latlon
		}
	}).then(function(response) {
		console.log("resp len = " + response.length)

		if (response.length > 0) {

			$.each(response, function(i, val) {

				var home = val.venue;
				var home_id = val.venue_id;
				var dispVal = home;
				if (val.been_here) {
					dispVal += ' (You\'ve been here)'
				}

				html += '<li><a href="#" onclick="setHomeFromSearch(\'' + home_id + '\')" data-homename="' + home + '" id="ch' + home_id + '">' + dispVal + '</a></li>';
			});
			$ul.html(html);
			$ul.listview("refresh");
			$ul.trigger("updatelayout");
		} else {
			html = '<li>Sorry! No results for ' + value + '! Please try again.</li>'
			$ul.html(html);
			$ul.listview("refresh");
			$ul.trigger("updatelayout");

		}
	});
	$('#autocomplete').blur()
}

function clearAutoComp() {
	var $ul = $("#autoCompList");
	$ul.html('');
	$ul.listview("refresh");
	$ul.trigger("updatelayout");
}


$(document).on("pageinit", "#setInfo", function() {
	var $ws = $("#wage_slider");
	var initval = $ws.attr('value');
	var wage_mess = $('#wage_message p');
	var messages = ["Really? That's like one beer... You can do better!", "That's barely the cost of a couple beers. Do you really think this will get you home on time?", "I think that sound's like a reasonable wager. Unless it doesn't... ", "Okay, Now we're talking!", "Wow, you really don't trust your self control!", "That might be pushing it... but it's your money!", "Sheesh... Okay!"];
	var time = new Date();
	var timestr = time.toLocaleTimeString();
	var now = timestr.substring(0, 5) + timestr.substring(8, 11);
	var timeInt = setInterval(myTimer ,1000);

	function myTimer() {
		var d = new Date();
		var t = d.toLocaleTimeString();
		$('#now').text(t);
		//document.getElementById("demo").innerHTML = t;
	}


	console.log('now = ' + now);
	//$('#now').text(now);
	//console.log($ws)
	$ws.slider({

		stop : function(event, ui) {
			var val = $(".ui-slider .ui-slider-track .ui-slider-handle").attr('title');
			console.log('stopped the functios')

			console.log('val = ' + val);
			$("#amount").val("$" + val);
			$("#amount").attr('data-wagamount', val);
			console.log('datawagamount = ' + $("#amount").attr('data-wagamount'))
			if (val == 5) {
				//console.log(messages[0]);
				wage_mess.text(messages[0])
			} else if (val <= 15) {
				//console.log(messages[1]);
				wage_mess.text(messages[1])
			} else if (val <= 55) {
				//console.log(messages[2]);
				wage_mess.text(messages[2])

			} else if (val <= 85) {
				//console.log(messages[3]);
				wage_mess.text(messages[3])
			} else if (val <= 120) {
				//console.log(messages[4]);
				wage_mess.text(messages[4])
			} else if (val <= 140) {
				//console.log(messages[5]);
				wage_mess.text(messages[5])
			} else {
				//console.log(messages[6]);
				wage_mess.text(messages[6])
			}

		}
	});
	$("#amount").val("$" + initval);
	$("#amount").attr('data-wagamount', initval);
	wage_mess.text(messages[2]);

});

$(document).on("pageinit", "#searchHome", function() {
	//functions for home page
	$('.ui-input-clear').click(function() {
		console.log("I CLICKED IT!!!")
		clearAutoComp()
	});

	$("#autoCompSubmit").click(function(e) {
		autoComplete()
		return false
	});
});

