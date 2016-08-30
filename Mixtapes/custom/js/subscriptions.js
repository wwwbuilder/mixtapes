function subscribe(subtype) {
    $('#loading-spinner').removeClass('hidden');

	$.ajax({
		url: '/subscribe_endpoint/',
		type: 'POST',
		dataType: 'JSON',
		data: JSON.stringify({
			'type':subtype
		})
	})
	.done(function() {
		window.location.reload();
	})
}

function equalHeights (target) {
    $(target).height('auto');

    var heights = []
    $(target).each(function(){
        heights.push($(this).height());             
    });
    var highest = Math.max.apply(Math, heights)
    $(target).height(highest);
}