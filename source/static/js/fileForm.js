var files = {};
$(function() {
	if ($("#files").val() != '') {
		files = JSON.parse($("#files").val());
		fileServed(files);
	}
	$("#form").submit(function(event) {
		$("#files").val(JSON.stringify(files));
	});
});
function fileUploaded(filename, fileinfo) {
	files[filename] = fileinfo;
}
function fileRemoved(filename) {
	if (files[filename]) {
		files[filename]['removed'] = true;
	}
}
