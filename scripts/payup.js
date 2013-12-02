

$(document).on("pageinit", "#payUp", function() {
	if (timesPlayed >= 3) {
		$(".playAgain").hide()
	}
	$(".payNow").click(function(){
		console.log('we clicked payNow!')
		return false
	})

});
