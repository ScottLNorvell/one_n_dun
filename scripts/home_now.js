
function liftOff() {
	//console.log("WE Did It!");
	$('#youDidIt').hide();
	$('#countdownArea').hide();
	$("#sorry").fadeIn()
}

function hideTimer() {
	$('#countdownArea').fadeOut();
}

$(document).on("pageinit", "#homeNow", function() {
	var now = new Date();
	console.log(now.getTime())
	var then = $('#then').val();
	var diff = then - now.getTime();
	var madeIt = $('#madeIt').val();
	console.log(diff)
	if (madeIt == 'y') {
		console.log(madeIt)
	}
	else {
		liftOff()
	}
	
	var thenDate = new Date(parseInt(then));
	var nowSoon = new Date(now.getTime() + 5000);
	if (diff > 0) {
		//$('#countdown').countdown({until: thenDate, format: 'yowdHMS', compact: true});
		$('#glowingLayout').countdown({until: thenDate,  
		compact: true, 
    	layout: '<span class="image{h10}"></span><span class="image{h1}"></span>' + 
        '<span class="imageSep"></span>' + 
        '<span class="image{m10}"></span><span class="image{m1}"></span>' + 
        '<span class="imageSep"></span>' + 
        '<span class="image{s10}"></span><span class="image{s1}"></span>',
        onExpiry: hideTimer});
	}
	else {
		$('#countdownArea').hide();
		console.log("it's not greater")
	}
	
})
