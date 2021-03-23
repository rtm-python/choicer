$(function() {
	$("a#signInFormSubmit").on('click', function() {
		event.preventDefault();
		$("#signInForm").submit();
	});
	if ($("#signInFormPassword").val()) {
		setInterval(verifyPin, 5000);
	}
});
function verifyPin() {
	$.ajax({
		type: "post",
		async: false,
		url: $("#signInForm").attr("actions"),
		data: $("#signInForm").serialize(),
		success: function (data, textStatus, request) {
			if (data.redirect) {
				location.pathname = data.redirect;
			} else if (!data.wait) {
				location.href = location.origin;
			}
		}
	});
}

