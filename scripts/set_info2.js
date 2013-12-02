function setHome(home, home_id) {
	console.log('this clicked: ' + home + home_id)
	$('#home').val(home);
	$('#home_id').val(home_id);
	$('#home_okay').text("Okay, you need to get to " + home);
	$('#mess').hide();
};

$(function() {
	var $ws = $("#wage_slider");
	var initval = $ws.attr('value');
	var wage_mess = $('#wage_message p');
	var messages = ["Really? That's like one beer... You can do better!", "That's barely the cost of a couple beers. Do you really think this will get you home on time?", "I think that sound's like a reasonable wager. Unless it doesn't... ", "Okay, Now we're talking!", "Wow, you really don't trust your self control! Can I suggest a good therapist?", "That might be pushing it... but it's your money!", "Sheesh... Okay!"];
	var time = new Date();
	var hours = time.getHours();
	var mins = time.getMinutes();

	function getMerid(hours) {
		if (hours < 12) {
			return 'AM'
		} else {
			return 'PM'
		}
	};
	var merid = getMerid(hours)
	var now = hours % 12 + ':' + mins + ' ' + merid
	console.log(now);
	$('#now').text(now);
	$ws.slider({

		stop : function(event, ui) {
			var val = $(".ui-slider .ui-slider-track .ui-slider-handle").attr('title');

			console.log(val);
			$("#amount").val("$" + val);
			if (val == 5) {
				//console.log(messages[0]);
				wage_mess.text(messages[0])
			} else if (val <= 20) {
				//console.log(messages[1]);
				wage_mess.text(messages[1])
			} else if (val <= 75) {
				//console.log(messages[2]);
				wage_mess.text(messages[2])

			} else if (val <= 150) {
				//console.log(messages[3]);
				wage_mess.text(messages[3])
			} else if (val <= 250) {
				//console.log(messages[4]);
				wage_mess.text(messages[4])
			} else if (val <= 400) {
				//console.log(messages[5]);
				wage_mess.text(messages[5])
			} else {
				//console.log(messages[6]);
				wage_mess.text(messages[6])
			}

		}
	});
	$("#amount").val("$" + initval);
	wage_mess.text(messages[2]);

});

$(document).on("pageinit", "#setInfo", function() {
	console.log('page loded, funct ready!')
	var mess = $('#mess input');
	var dt = false;
	var typingTimer;
	//timer identifier
	var doneTypingInterval = 5000;
	//time in ms, 5 second for example

	//on keyup, start the countdown
	mess.keyup(function() {
		typingTimer = setTimeout(doneTyping, doneTypingInterval);
	});

	//on keydown, clear the countdown
	mess.keydown(function() {
		dt = false
		clearTimeout(typingTimer);
	});

	//user is "finished typing," do something
	function doneTyping() {
		//do something
		console.log('done typing!')
		dt = true
	}


	$("#autocomplete").on("listviewbeforefilter", function(e, data) {
		console.log('before filter');
		console.log('data = ' + data);

		var $ul = $(this), $input = $(data.input), value = $input.val(), html = "";
		$ul.html("");
		console.log('value = ' + value)
		if (value && value.length > 2) {
			$ul.html("<li><div class='ui-loader'><span class='ui-icon ui-icon-loading'></span></div></li>");
			$ul.listview("refresh");
			$.ajax({
				url : "/autocomp_homes",
				dataType : "json",
				crossDomain : true,
				data : {
					term : $input.val()
				}
			}).then(function(response) {
				console.log('then response for dt = ' + dt)

				$.each(response, function(i, val) {
					var home = val[0];
					var home_id = val[1];
					html += '<li><a href="#" onclick="setHome(\'' + home + "','" + home_id + '\')">' + home + "</a></li>";
				});
				$ul.html(html);
				$ul.listview("refresh");
				$ul.trigger("updatelayout");

			});
		}
	});
});
