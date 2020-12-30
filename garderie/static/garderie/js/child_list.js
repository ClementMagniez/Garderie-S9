$(document).ready(function() {

	// enfants absents : au clic, envoie en AJA 
	
	$('.child_out').click( function() {
		child_id=$(this).data("value");
		console.log(child_id);
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_in,
			data: {
				'id': child_id,
			},
			dataType: 'json',
			success: function (data) {
				
				if(data['error'])
					alert(data['error']);	
				else {

					let arrival=new Date(data['arrival']);
					let expected_arrival=new Date(data['expected_arrival']);
					let expected_departure=new Date(data['expected_departure']);
					$("#table1").find("tbody") // TODO TODO TODO
						.append(`<tr class='child_in' data-value=${child_id}><td><a href="${child_id}">${data['name']}</a></td><td>${arrival.getHours()}:${arrival.getMinutes()}</td><td></td><td>${expected_arrival.getHours()}:${expected_arrival.getMinutes()}</td>><td>${expected_departure.getHours()}:${expected_departure.getMinutes()}</td></tr>`);					
				}
			}
		});
	});

	// enfants présents : au clic, update leur Schedule avec leur date de départ
	$('#table1').on('click', '.child_in', function() {
		child_id=$(this).data("value");
		console.log(child_id);
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_out,
			data: {
				'id': child_id,
			},
			dataType: 'json',
			success: function (data) {
				if(data['error'])
					alert(data['error']);
				else {
				
					let d=new Date(data['departure']);
					$("#table1").find(`[data-value=${child_id}]`)
						.find('td:nth-child(3)').append(d.getHours()+':'+d.getMinutes());
				}
			}
		});
	});

});

