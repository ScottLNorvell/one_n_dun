function setHome(id) {
	//puts home vals in the locklist for home rendering!
	var litem = $('#ch' + id);
	var homeNm = litem.attr('data-homenm');
	var homeLockList = $('#homeLockList');
	var homeHTML = homeLockList.html()

	var ul = $("#autoCompList");

	var input = $('#autocomplete');
	var homeLockHTML = '<li class="hLock" data-hid ="' + id + '">' + homeNm + '</li>'

	homeHTML += homeLockHTML

	homeLockList.html(homeHTML);
	homeLockList.listview("refresh");
	homeLockList.trigger("updatelayout");
	input.val('');

	ul.html('');
}

function setHomeCBs() {
	//updates checkboxes with new data!
	var $homeList = $("#homeList");
	var homeLockList = $('#homeLockList');
	$('li.hLock').each(function() {
		var hid = $(this).attr('data-hid');
		if ($('#' + hid).val() == undefined) {

			var homeNm = $(this).text();
			var homeJSON = homeNm + '|||' + hid;
			var inputHTML = '<input type="checkbox" name="homes" id="' + hid + '" value="' + homeJSON + '" data-mini="true" checked="true" >';
			var labelHTML = '<label for="' + hid + '">' + homeNm + '</label>';
			$homeList.append(inputHTML, labelHTML).trigger('create');

		}

	})

	homeLockList.html('')

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

				html += '<li><a href="#" onclick="setHome(\'' + home_id + '\')" data-homenm="' + home + '" id="ch' + home_id + '">' + dispVal + '</a></li>';
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


$(document).on("pageinit", "#index", function() {
	var isAuthed = $('#isAuthed').attr('data-authed');
	if (isAuthed == "true") {
		$('.auth').hide();
		$('.authed').show();
	}
	if ($('#homeList').html().length > 0) {
		//console.log("It's greater");
		$('.noHomePrefs').hide()
	}

	//add id to this?

	$('#setMyPrefs').click(function() {

		var url = '/post_prefs'
		// the script where you handle the form input.

		$.ajax({
			type : "GET",
			url : url,
			dataType : 'json',
			data : $("#prefForm").serialize(), // serializes the form's elements.
			success : function(data) {
				//console.log(data);
				// we have the data, what to do with it?
				for (var i = 0; i < data.homes.length; i++) {
					console.log(data.homes[i][0])
				}
				for (var i = 0; i < data.charities.length; i++) {
					console.log(data.charities[i][0])
				}
				console.log(data.robot_posts)
			}
		}).then(function() {
			$.mobile.changePage('#prefsSet')
		})
		//
		return false;
		// avoid to execute the actual submit of the form.
	});

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

function togglePermSelect(cid, checked) {
	var $cid = $('#' + cid);
	var $charList = $('#charList')
	var charNm = $('#pref_' + cid).val();
	var charJSON = charNm + '|||' + cid
	var inputHTML = '<input type="checkbox" name="charities" id="' + cid + '" value="' + charJSON + '" data-mini="true" checked="true" >';
	var labelHTML = '<label for="' + cid + '">' + charNm + '</label>';

	if (checked) {
		//add or check
		if ($cid.val()) {
			$cid.prop('checked', true)//.checkboxradio('refresh')
		} else {
			$charList.append(inputHTML, labelHTML).trigger('create');
		}

	} else {
		if ($cid.val()) {
			$cid.prop('checked', false).checkboxradio('refresh')
		}
	}
}

function toggleSelect($this) {
	var charPossList = $('#charPossList')
	var cid = $this.attr('id').substring(5);
	var $cid = $('#' + cid);
	var $acc = $('#acc' + cid + ' .ui-collapsible-heading-toggle .ui-btn-text')
	var html = $acc.html()
	var togHTML = '<small> [selected]</small>'
	console.log($this.is(":checked"))
	if ($this.is(":checked")) {

		html += togHTML
		$acc.html(html)
		togglePermSelect(cid, true)
	} else {
		html = html.replace(togHTML, '')
		//console.log(html)
		$acc.html(html)
		togglePermSelect(cid, false)
	}
}


$(document).on("pageinit", "#searchCharity", function() {
	//functions for charity page

	$('#charList input[type="checkbox"]').each(function() {
		var $this = $(this)
		var cid = $this.attr('id');
		var prefCB = $('#pref_' + cid)
		var $acc = $('#acc' + cid + ' .ui-collapsible-heading-toggle .ui-btn-text')
		var html = $acc.html()
		var togHTML = '<small> [selected]</small>'
		if ($this.is(":checked")) {
			prefCB.prop('checked', true).checkboxradio("refresh")
			html += togHTML
			$acc.html(html)
			console.log('status of the checking = ' + cid)
			console.log(prefCB.is(":checked"))

		}
	})

	$('#charPossList input[type="checkbox"]').click(function() {
		//var testit = $(this).attr('id');
		var $this = $(this)
		toggleSelect($this)
		//charPossList.trigger('create')
		//console.log(cid);

	})
});

$(document).on("pageinit", "#prefsSet", function() {
	//functions for prefsSet page
	$('#prefSetBack').click(function() {
		$.mobile.changePage('#index')
		window.location.reload(true)
		return false
	})
});

