var FG_DONATE_BUTTON = ( function() {
		var e = {};
		e.openDonationWindow = function(J, z) {
			var q = J.id;
			q = q.replace(".", "/");
			var z = z;
			if (window.screenX != undefined) {
				var p = window.screenX;
				var m = window.screenY;
				var n = 120;
			} else {
				var p = window.screenLeft;
				var m = window.screenTop;
				var n = 10;
			}
			var j = a();
			var B = "540";
			var t = "750";
			var G = ((j / 2) - 270) + p;
			var F = m + n;
			var l = "width=" + B + ",height=" + t;
			l += ",menubar=no,location=no,top=" + F + ",left=" + G;
			var u = [];
			if ( typeof FG_DONATE_BUTTON_PARAMS != "undefined") {
				var C = FG_DONATE_BUTTON_PARAMS;
				for (var k in C) {
					if (C.hasOwnProperty(k)) {
						if (k == "attribution") {
							if (C.attribution_name != undefined) {
								u.push(k + "=" + C[k]);
							}
						} else {
							if (k == "attribution_name") {
								if (C.attribution != undefined) {
									u.push(k + "=" + C[k]);
								}
							} else {
								u.push(k + "=" + C[k]);
							}
						}
					}
				}
			}
			u.push("parentPath=" + encodeURI(window.location));
			var v = u.join("&");
			var s = z + "/secure/donate";
			var o = "/" + q + "?" + v;
			var i = s + o;
			var A = document.createElement("div");
			var y = "fgDonationPopupOverlay";
			A.setAttribute("id", y);
			A.style.zIndex = "100000";
			A.style.width = "300%";
			A.style.height = "100%";
			A.style.position = "fixed";
			A.style.marginLeft = "-1000px";
			A.style.top = "0";
			A.style.backgroundColor = "#000000";
			A.style.opacity = ".75";
			A.style.filter = "alpha(opacity=75)";
			var D = document.createElement("div");
			var r = "fgOverlayInfo";
			D.setAttribute("id", r);
			D.style.zIndex = "100001";
			D.style.width = "300px";
			D.style.height = "300px";
			D.style.position = "fixed";
			D.style.left = "50%";
			D.style.marginLeft = "-150px";
			D.style.marginTop = "150px";
			D.style.padding = "20px";
			D.style.backgroundColor = "#000000";
			D.style.color = "#FFFFFF";
			D.style.textAlign = "center";
			D.style.fontSize = "18px";
			D.appendChild(document.createTextNode("You currently have a donation window open. Would you like to:"));
			D.style.display = "none";
			var x = D.appendChild(document.createElement("a"));
			var w = "fgDonationWindowLink";
			x.setAttribute("id", w);
			x.style.display = "block";
			x.style.paddingTop = "40px";
			x.style.color = "#607890";
			x.style.cursor = "pointer";
			x.style.textDecoration = "underline";
			x.style.fontSize = "14px";
			if (x.addEventListener) {
				x.addEventListener("click", function() {
					H.focus();
				}, false);
			} else {
				if (x.attachEvent) {
					x.attachEvent("onclick", function() {
						H.focus();
					});
				}
			}
			x.appendChild(document.createTextNode("Return To The Donation Window"));
			var E = D.appendChild(document.createElement("a"));
			var h = "fgReturnLink";
			E.setAttribute("id", h);
			E.style.display = "block";
			E.style.paddingTop = "60px";
			E.style.color = "#607890";
			E.style.cursor = "pointer";
			E.style.textDecoration = "underline";
			E.style.fontSize = "14px";
			if (E.addEventListener) {
				E.addEventListener("click", b, false);
			} else {
				if (E.attachEvent) {
					E.attachEvent("onclick", b);
				}
			}
			E.appendChild(document.createTextNode("Remove This Black Box"));
			document.body.insertBefore(A, document.body.childNodes[0]);
			document.body.insertBefore(D, document.body.childNodes[0]);
			var H = window.open(i, "fgDonationPopup", l);
			if (H == null) {
				return false;
			}
			H.focus();
			var I = "true";
			if (window.addEventListener) {
				window.onfocus = function() {
					f(D);
				};
				window.onblur = function() {
					c(D);
				};
			} else {
				if (window.attachEvent) {
					document.onfocusin = function() {
						f(D);
					};
					document.onfocusout = function() {
						c(D);
					};
				}
			}
			d(H, "", "shutItDown", 10);
		};
		function a() {
			var h = 0;
			if (self.innerHeight) {
				h = self.innerWidth;
			} else {
				if (document.documentElement && document.documentElement.clientHeight) {
					h = document.documentElement.clientWidth;
				} else {
					if (document.body) {
						h = document.body.clientWidth;
					}
				}
			}
			return h;
		}

		function g() {
			var h = 0;
			if (self.innerHeight) {
				h = self.innerHeight;
			} else {
				if (document.documentElement && document.documentElement.clientHeight) {
					h = document.documentElement.clientHeight;
				} else {
					if (document.body) {
						h = document.body.clientHeight;
					}
				}
			}
			return h;
		}

		function d(i, l, k, j) {
			j = j || 20;
			setTimeout(function h() {
				if (i == null || i.closed) {
					b();
				} else {
					setTimeout(h, j);
				}
			}, j);
		}

		function b() {
			if ( typeof FG_DONATE_BUTTON_BEHAVIORS != "undefined") {
				if ( typeof FG_DONATE_BUTTON_BEHAVIORS.windowCloseCallbacks != "undefined") {
					var l = FG_DONATE_BUTTON_BEHAVIORS.windowCloseCallbacks;
					for (var h = 0; h < l.length; h++) {
						if ( typeof l[h] === "function") {
							l[h].call();
						} else {
							if ( typeof l[h].call != "undefined") {
								l[h].call();
							}
						}
					}
				}
			}
			var k = document.getElementById("fgDonationPopupOverlay");
			var j = document.getElementById("fgOverlayInfo");
			if (j != null) {
				document.body.removeChild(j);
			}
			if (k != null) {
				document.body.removeChild(k);
			}
		}

		function f(h) {
			var h = h;
			h.style.display = "block";
		}

		function c(h) {
			var h = h;
			h.style.display = "none";
		}
		return e;
	}());
var fgModalOps = {
	cdn : "http://donate.firstgiving.com/",
	appPath : "http://donate.firstgiving.com",
	contentBlockLoaded : 0,
	charityName : "",
	init : function() {
		var a = document.createElement("link");
		a.setAttribute("href", fgModalOps.cdn + "dpa/static/css/fg_modal_style.min.css");
		a.setAttribute("rel", "stylesheet");
		a.setAttribute("type", "text/css");
		document.getElementsByTagName("head")[0].appendChild(a);
		var b = '<div id="fgGetButtonModal" style="display: none;"><div id="fgCloseModal"></div><div id="fgGetButtonHeader"><div id="fgGetButtonHeaderSite" class="fgSectionHeader active"></div><div id="fgGetButtonHeaderFb" class="fgSectionHeader"></div></div><div id="fgGetButtonHeaderSite-block" class="fgModalContentBlock"><div id="codeBlockLoader"><label>Retrieving Your Button</label><img src="' + fgModalOps.cdn + 'dpa/static/img/fg_modal_ajax-loader.gif" id="fgLoadingSpinner"/></div><div id="fgGetForOtherCause"><span>Create a Donation Button for a different charity?</span><a href="http://donatetab.firstgiving.com?ref=consumer-modal-setup" target="_blank">Setup</a></div></div><div id="fgGetButtonHeaderFb-block" class="fgModalContentBlock"><p>Facebook page administrators can easily customize and install donation buttons to support any non-profit. Click the button below to setup your button.</p><a href="http://donatetab.firstgiving.com/pageselector?charity_uuid=' + jQuery(".fg-donation-button-4ccb04fb46c30").attr("id") + '&fbprompt=0" id="fgFacebookButton" target="_blank"></a><img src="' + fgModalOps.cdn + 'dpa/static/img/facebook_tab_screenshot.png" id="fgFacebookScreenshot" /></div></div><div id="fgModalOverlay" style="display: none;"></div>';
		jQuery("body").prepend(b);
		jQuery("#fg_donation-button-block #fg_get-this-action a").click(function() {
			fgModalOps.showModal();
		});
		jQuery("#fgModalOverlay").live("click", function() {
			fgModalOps.closeModal(this);
		});
		jQuery(".fgSectionHeader").click(function() {
			fgModalOps.selectNav(this);
		});
		jQuery("#fgCloseModal").click(function() {
			fgModalOps.closeModal(jQuery("#fgModalOverlay"));
		});
		jQuery("#fgCodeSnippet").live("click", function() {
			this.select();
		});
		jQuery("#fgGetButtonModal").scrollTop();
	},
	buildCodeBlock : function() {
		jQuery.ajax({
			type : "get",
			url : fgModalOps.appPath + "/configurator/get-consumer-modal/" + jQuery(".fg-donation-button-4ccb04fb46c30").attr("id") + "/fgModalOps.buildDOM",
			dataType : "jsonp",
			timeout : 5000,
			jsonp : "fgModalOps.buildDOM",
			success : function(a) {
			},
			error : function(a) {
			}
		});
	},
	buildDOM : function(b) {
		fgModalOps.charityName = jQuery(b).find("#fgOrganizationName").html();
		var a = "<p>Install your " + fgModalOps.charityName + ' donation button by copying the code below and pasting it somewhere inside your website\'s <em>&lt;body&gt;</em> tag.</p><textarea id="fgCodeSnippet">' + b + "</textarea>";
		jQuery("#fgGetButtonHeaderSite-block #codeBlockLoader").hide();
		jQuery("#fgGetButtonHeaderSite-block").prepend(a);
		fgModalOps.contentBlockLoaded = 1;
	},
	showModal : function() {
		var a = jQuery(window).scrollTop();
		jQuery("#fgGetButtonModal").css("top", (a + 100 + "px"));
		if (fgModalOps.contentBlockLoaded == 0) {
			fgModalOps.buildCodeBlock();
		}
		jQuery("#fgModalOverlay").css({
			opacity : 0
		}).fadeTo("fast", 0.9, function() {
			jQuery("#fgGetButtonModal").show();
		});
	},
	closeModal : function(a) {
		jQuery("#fgGetButtonModal").hide();
		jQuery(a).hide();
	},
	selectNav : function(a) {
		jQuery(".fgSectionHeader").removeClass("active");
		jQuery(a).toggleClass("active");
		jQuery(".fgModalContentBlock").hide();
		jQuery("#" + jQuery(a).attr("id") + "-block").show();
	}
};
if (document.getElementById("fg_get-this-action")) {
	if ( typeof jQuery == "undefined") {
		var script = document.createElement("script");
		script.type = "text/javascript";
		if (script.readyState) {
			script.onreadystatechange = function() {
				if (script.readyState == "loaded" || script.readyState == "complete") {
					script.onreadystatechange = null;
					if (fgModalOps.contentBlockLoaded == 0) {
						fgModalOps.init();
					}
				}
			};
		} else {
			script.onload = function() {
				if (fgModalOps.contentBlockLoaded == 0) {
					fgModalOps.init();
				}
			};
		}
		script.src = "//ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.js";
		document.body.appendChild(script);
	} else {
		if (fgModalOps.contentBlockLoaded == 0) {
			fgModalOps.init();
		}
	}
}