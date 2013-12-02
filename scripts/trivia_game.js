function submitAnswer() {
	var url = '/_trivia'
	// the script where you handle the form input.
	$('#answerCountdown').countdown('destroy')
	$.ajax({
		type : "POST",
		url : url,
		dataType : 'json',
		data : $("#answerForm").serialize(), // serializes the form's elements.
		success : function(data) {
			var answerText = data.answer[0] + ", " + data.answer[1];

			//the right and possibly wrong answer elements
			var choiceLi = $('#list_' + data.choice);
			var answerLi = $('#list_' + data.answer[0]);

			//markup for right and wrong
			var redX = '<a href="#"><img src="/img/red-x.png" class="ui-li-icon">' + choiceLi.text() + '</a>'
			var greenCheck = '<a href="#"><img src="/img/green-check.png" class="ui-li-icon">' + answerLi.text() + '</a>'

			//list containing answers for markup
			var possUl = $('#possUl');

			var $currWager = $("#currWager")
			var currWager = $currWager.val()
			var qWinnings = wagerTable[i][0]

			//insert answer text and hide question radios
			$('.answerShow').text(answerText)
			$("#answerPosses").hide()

			answerLi.html(greenCheck)

			if (data.correct) {
				$("#rightAnswer").show()
				currWager -= qWinnings
				//console.log(currWager.toFixed(2))
				$currWager.val(currWager)
				$('.currHumanWager').text("$" + currWager.toFixed(2))

			} else {
				$("#wrongAnswer").show()
				//choiceLi.attr('data-icon', 'delete')
				choiceLi.html(redX)
			}
			possUl.listview()
			$('#possList').show()

			i += 1
			console.log('i = ' + i)
		}
	})
}

function nextTQ() {
	$.ajax({
		type : "GET",
		url : "/_trivia",
		dataType : 'html',

		success : function(data) {
			$('#triviaContent').html(data).trigger('create')
			$("#submitTrivia").click(function() {
				submitAnswer()

				return false
			});
			$('#answerCountdown').countdown({
				until : 25,
				compact : true,
				layout : '(You have <b>{snn}</b> {desc}',
				description : 'seconds to answer this question)',
				onExpiry : submitAnswer
			});
			$(".questionHumanWinnings").text(wagerTable[i][1]);

			$("#questionWinnings").val(wagerTable[i][0].toString());
			//console.log('qw.val = ' + $("#questionWinnings").val())
			$("#trivGameBack").click(function() {
				if (i > 10) {
					$.mobile.changePage('#triviaDone')
					return false
				} else {
					$.mobile.changePage('#trivGame')
					$(".questionHumanWinnings").text(wagerTable[i][1])

					return false
				}
			})
		}
	}).then(function() {
		$.mobile.changePage('#trivia')
	})
}

function updateTransaction(redUrl) {
	url = '/trivia'
	$.ajax({
		type : "POST",
		url : url,
		dataType : 'json',
		data : $("#wagerData").serialize(), // serializes the form's elements.
		success : function(data) {
			console.log('We Did It!')
		}
	}).then(function(){
		window.location.href = redUrl
	})
}

function goToPay() {
	console.log('goPay!')
}

$(document).on("pageinit", "#trivGame", function() {
	console.log("timesPlayed = " + timesPlayed)
	
	$('#getTQ').click(function() {
		nextTQ()
		return false
	});

	//put the winnings in the boxes
	$(".questionHumanWinnings").text(wagerTable[i][1])
	

});

$(document).on("pageinit", "#triviaDone", function() {
	var triesLeft = 2 - timesPlayed
	var $triesLeft = $("#triesLeft")
	$("#playAgain").click(function() {
		var redUrl = $(this).attr('href')
		console.log('redUrl = ' + redUrl)
		updateTransaction(redUrl)
		return false
	});
	if (triesLeft == 1) {
		$triesLeft.text(triesLeft + " turn remaining!")
	} else {
		$triesLeft.text(triesLeft + " turns remaining!")
	}
	
	$("#payUp").click(function() {
		var redUrl = $(this).attr('href')
		console.log('redUrl = ' + redUrl)
		updateTransaction(redUrl)
		return false
	});
	if (timesPlayed == 2) {
		$(".noMoreTurns").hide()
	}

}); 