function initSortable() {
	$("#sortable").sortable({
		placeholder: "sortable-placeholder"
	});
	$("#reordererFormSubmit").fadeTo(0, 0.5);
	$("#sortable").on("sortchange", function() {
		$("#reordererFormSubmit").fadeTo(1000, 1.0);
	});
	$("#reordererFormSubmit").on("click", function() {
		var uidList = [];
		$('[class*="entity-uid"]').each(function() {
			uidList.push($(this).attr("uid"));
		});
		console.log(uidList);
		$("#reordererFormData").val(JSON.stringify({"uidList": uidList}, null));
	});
}
