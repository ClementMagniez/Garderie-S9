$(document).ready(function() {
	console.log(csrf);

	// enfants absents : au clic, les ajoute à table_in et crée un Schedule avec
	// leur date d'arrivée
	
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
				
					let d=new Date(data['arrival'])
					$("#table1").find("tbody")
						.append(`<tr class='child_in' data-value=${child_id}><td><a href="${child_id}">${data['name']}</a></td><td>${d.getHours()}:${d.getMinutes()}`)
						.append("</td></tr>");					
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
						.find('td:last').after('<td>'+d.getHours()+':'+d.getMinutes()+'</td>');
				}
			}
		});
	});

});

