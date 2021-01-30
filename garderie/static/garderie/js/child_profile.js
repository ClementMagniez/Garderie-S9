$(document).ready(function() {

	$('.button_modal').click(function() {
		let schedule_id=$(this).data('sid');
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_get_form_modal,
			data: {
				'id': schedule_id,
			},
			dataType: 'html',
			success: function (data) {
				if(data['error'])
					alert(data['error']);	
				else {
				
					$('#myModal').html(data);
					$('#myModal').modal('toggle');
				}
			}
		});
	
	
	
	});



});
