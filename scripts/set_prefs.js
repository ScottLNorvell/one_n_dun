function setHome(id) {
	var litem = $('#ch' + id);
	var homeNm = litem.text();
	//homeList.push([id, homeName])
	// These need to be tweeked
	var ul = $("#autoCompList");
	var $homeList = $("#homeList");
	var input = $('.ui-input-text');
	var homeJSON = homeNm + '|||' + id;
	var inputHTML = '<input type="checkbox" name="homes" id="' + id + '" value="' + homeJSON + '" checked="true" >';
	var labelHTML = '<label for="' + id + '">' + homeNm + '</label>';
	console.log(inputHTML);
	console.log(labelHTML);
	$homeList.append(inputHTML, labelHTML).trigger('create');
	input.val('');
	
	ul.html('');
}

function renderSubmitButton() {
	console.log('trying to submit')
	if ($('#homeList').html()) {
		console.log("hl HTML = " + $('#homeList').html());
		$('#submit_button').show()
	}
}


$(document).on("pageinit", "#setPrefs", function() {
	var input = $('#autocomplete');

	// runs the autocomplete listview if we press enter = sloppy
	// instead, dialog with submit function? there is a form that ajax submits the querie and returns 5-10 posses
	input.keypress(function(e) {
		var inp = $(this);
		if (e.keyCode == 13 || e.which == 13) {
			var finalVal = inp.val()
			console.log("inp.val = " + inp.val())
			autoComplete(finalVal)
		} else {
			console.log(e.keyCode)
		}
	});
	function autoComplete(value) {
		var $ul = $("#autoCompList"), html = "";

		$.ajax({
			url : "/autocomp_homes",
			dataType : "json",
			crossDomain : true,
			data : {
				term : value
			}
		}).then(function(response) {
			//console.log('then response for dt = ' + dt)

			$.each(response, function(i, val) {
				var home = val[0];
				var home_id = val[1];
				//console.log('home = ' + home)
				html += '<li><a href="#" onclick="setHome(\'' + home_id + '\')" data-rel="dialog" data-transition="pop" id="ch' + home_id + '">' + home + '</a></li>';
			});
			$ul.html(html);
			$ul.listview("refresh");
			$ul.trigger("updatelayout");

		});
	}

});
