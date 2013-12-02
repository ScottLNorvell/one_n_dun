
function pad(number, length) {
	var str = '' + number;
	while (str.length < length) {
		str = '0' + str;
	}
	return str;
}

function formatTime2(time) {
	var hr = parseInt(time / 360000), min = parseInt(time / 6000) - (hr * 60), sec = parseInt(time / 100) - (min * 60) - (hr * 3600), hundredths = pad(time - (sec * 100) - (min * 6000) - (hr * 360000), 2);
	return (hr > 0 ? pad(hr, 2) : "00") + ":" + (min > 0 ? pad(min, 2) : "00") + ":" + pad(sec, 2) + ":" + hundredths;
}

function formatTime(time) {

	var seconds = Math.floor((time / 1000) % 60);
	var minutes = Math.floor((time / (60 * 1000)) % 60);
	var hours = Math.floor((time / (60 * 60 * 1000)) % 60)

	return hours + ":" + pad(minutes, 2) + ":" + pad(seconds, 2);
}

function liftOff() {
	//console.log("WE Did It!");
	$('#doThis').hide();
	$('#countdownArea').hide();
	$("#sorry").fadeIn()
}

$(document).on("pageinit", "#timerPost", function() {
	var now = new Date();
	var then = $('#then').val();
	var diff = then - now.getTime()
	var thenDate = new Date(parseInt(then));
	var nowSoon = new Date(now.getTime() + 10000);
	if (diff > 0) {
		//$('#countdown').countdown({until: thenDate, format: 'yowdHMS', compact: true});
		$('#glowingLayout').countdown({until: thenDate,  
		compact: true, 
    	layout: '<span class="image{h10}"></span><span class="image{h1}"></span>' + 
        '<span class="imageSep"></span>' + 
        '<span class="image{m10}"></span><span class="image{m1}"></span>' + 
        '<span class="imageSep"></span>' + 
        '<span class="image{s10}"></span><span class="image{s1}"></span>',
        onExpiry: liftOff});
	}
	else {
		liftOff()
	}
	
})
