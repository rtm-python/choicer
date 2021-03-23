$(function() {
	var user_tz = moment.tz.guess();
	$('[class*="modified-timestamp"]').each(function() {
		this.innerText = moment(this.innerText).tz(user_tz).fromNow() + moment(this.innerText).tz(user_tz).format(', HH:mm:ss, DD MMMM YYYY, dddd');
	});
});
