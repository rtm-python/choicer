Dropzone.autoDiscover = false;
$(function() {
	$("#fileDropzone").dropzone({
		url: "/upload/",
		headers: {
			"X-CSRFToken": $("input#csrf_token").val()
		},
		paramName: "file",
		maxFilesize: 32, // MB
		addRemoveLinks: true,
		maxFiles: parseInt($("#fileDropzone").attr("maxFiles")),
		dictDefaultMessage: $("#fileDropzone").attr("defaultMessage"),
		dictRemoveFile: $("#fileDropzone").attr("removeFile"),
		dictCancelUpload: $("#fileDropzone").attr("cancelUpload"),
		acceptedFiles: $("#fileDropzone").attr("acceptedFiles"),
		init: function() {
 			this.on("success", function(file, resp){
				if (resp["status"] == "ok") {
					fileUploaded(file.name, resp["fileinfo"]);
				}
			});
			this.on("removedfile", function(file){
				fileRemoved(file.name);
			});
			this.on("maxfilesexceeded", function(file){
		    this.removeFile(file);
	    });
		}
	});
//	console.log(Dropzone.options.fileDropzone);
//	XMLHttpRequest.prototype.open = (function(open) {
//		return function(method, url, async) {
//			open.apply(this, arguments);
//			this.setRequestHeader('X-CSRFToken', $("input#fileCsrfToken").val());
//		};
//	})(XMLHttpRequest.prototype.open);
});
function fileServed(files) {
	var fileDropzone = Dropzone.forElement("#fileDropzone");
	var mockFile = {};
	Object.keys(files).forEach(function(key) {
		mockFile = {name: key, size: files[key]["size"]};
		fileDropzone.options.addedfile.call(fileDropzone, mockFile);
		fileDropzone.options.thumbnail.call(fileDropzone, mockFile, files[key]['url']);
		fileDropzone.options.complete.call(fileDropzone, mockFile);
	});
}
