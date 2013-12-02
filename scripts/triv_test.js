function submitAnswer() {
	var url = '/trivia'
	// the script where you handle the form input.
	$('#answerCountdown').countdown('destroy')
	$.ajax({
		type : "POST",
		url : url,
		dataType : 'json',
		data : $("#answerForm").serialize(), // serializes the form's elements.
		success : function(data) {
			var answerText = data.answer[0] + ", " + data.answer[1];
			var choiceLi = $('#list_' + data.choice);
			var answerLi = $('#list_' + data.answer[0]);
			var possUl = $('#possUl');
			var redX = '<a href="#"><img src="/img/red-x.png" class="ui-li-icon">' + choiceLi.text() + '</a>'
			var greenCheck = '<a href="#"><img src="/img/green-check.png" class="ui-li-icon">' + answerLi.text() + '</a>'

			//$('.answerChoice').text(data.choice)
			$('.answerShow').text(answerText)
			$("#answerPosses").hide()

			//answerLi.attr('data-icon', 'check')
			answerLi.html(greenCheck)

			if (data.correct) {
				$("#rightAnswer").show()

			} else {
				$("#wrongAnswer").show()
				//choiceLi.attr('data-icon', 'delete')
				choiceLi.html(redX)
			}
			possUl.listview()
			$('#possList').show()
			//possUl.listview('create')

		}
	})
}

function nextTQ() {
	$.ajax({
			type : "GET",
			url : "/trivia",
			dataType : 'html',

			success : function(data) {
				$('#triviaContent').html(data).trigger('create')
				$("#submitTrivia").click(function() {
					submitAnswer()

					return false
				});
				$('#answerCountdown').countdown({
					until : 15,
					compact : true,
					layout : '(You have <b>{snn}</b> {desc}',
					description : 'seconds to answer this question)',
					onExpiry: submitAnswer
				});
			}
		}).then(function() {
			$.mobile.changePage('#trivia')
		})
}


$(document).on("pageinit", "#trivGame", function() {
	$('#getTQ').click(function() {
		nextTQ()
		return false
	});

});

