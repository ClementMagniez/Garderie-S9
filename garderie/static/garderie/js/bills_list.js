$(document).ready(function() {

	$('.button_detail').click(function() {
		let bill_id=$(this).data('bid');
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_get_bill_modal,
			data: {
				'id': bill_id,
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
