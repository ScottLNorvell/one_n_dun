var homeList = []

function setHome(id) {

	var litem = $('#' + id);
	var homeNm = litem.text();
	var ul = $("#autocomplete");
	var homeListView = $("#homeList");
	var html = homeListView.html();
	var input = $('.ui-input-text');
	var homeJson = [homeNm, id]

	homeList.push(homeJson)
	console.log('homelist = ' + JSON.stringify(homeList))
	html += '<li>' + homeNm + '</li>'
	homeListView.html(html);
	homeListView.listview('refresh')
	input.val('');
	$("#thisIsHome").html('<p>' + homeNm + '</p>')
	ul.html('');
	ul.listview("refresh");
	ul.trigger("updatelayout");
	console.log(id)
	console.log(litem.text())
}




$(document).on("pageinit", "#setPrefs", function() {
	var input = $('.ui-input-text');
	input.keypress(function(e){
		var inp = $(this);
		if (e.keyCode == 13 || e.which == 13) {
			var finalVal = inp.val()
			console.log("inp.val = " + inp.val())
			autoComplete(finalVal)
			inp.val(finalVal + ' ')
		}
		else {
			console.log(e.keyCode)
		}
	});
	function autoComplete(value) {
		$("#autocomplete").on("listviewbeforefilter", function(e, data) {

			var $ul = $(this), $input = $(data.input),  html = "";
			//console.log('data.input = ' + $input.attr('class'))
			$ul.html("");
			console.log('value = ' + value)
			if (value && value.length > 5) {
				$ul.html("<li><div class='ui-loader'><span class='ui-icon ui-icon-loading'></span></div></li>");
				$ul.listview("refresh");
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
						html += '<li><a href="#" onclick="setHome(\'' + home_id + '\')" data-rel="dialog" data-transition="pop" id="' + home_id + '">' + home + '</a></li>';
					});
					$ul.html(html);
					$ul.listview("refresh");
					$ul.trigger("updatelayout");

				});
			}

		});
	}

	var testObj = {
		home : 'this is home',
		id : 'this is id'
	};
	var JtestObj = JSON.stringify(testObj);
	console.log(JtestObj);
	$('#testObj').val(JtestObj);
});
