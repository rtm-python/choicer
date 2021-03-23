$(function() {
	$('[id^="collapse"]').on('show.bs.collapse', function() {
		$('[id^="collapse"][id!="this.id"]').collapse('hide');
	});
});
