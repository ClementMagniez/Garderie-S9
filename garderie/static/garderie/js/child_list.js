// transforme un string aaaa-MM-jj hh:mm:ss en hh:mm
// ne valide pas str au préalable ; on ne manipule revanche rien s'il fait
// moins de 10 caractères (valeur arbitraire en-dessous de laquelle 
// on considère que str est un placeholder)
function formattedDateFromString(str) {
	// TODO : fonctionnel mais pas du tout future-proof
	if(str.length>10)
		return str.slice(11, 16);
	else
		return str
}

// Supprime un Schedule et le row associé
function removeArrival(schedule_id) {
	$.ajax({
		headers: { "X-CSRFToken": csrf}, 
		type: 'POST',
		url: url_remove_arrival,
		data: {
			'id': schedule_id,
		},
		dataType: 'json',
		success: function (data) {			
			if(data['error'])
				alert(data['error']);	
			else {
				data_tab1.rows(`[data-sid='${schedule_id}']`).remove().draw();
			}
		}
	});
}


// A partir d'un map data contenant des dates 'arrival, 'expected_arrival' 
// et 'expected_departure' au format aaaa-MM-jj hh:mm:ss, 
// ainsi qu'un string 'name', ajoute une entrée à la DataTable table_object affichant ces infos
function addChildRow(data, child_id, table_object) {
	let arrival=formattedDateFromString(data['arrival']);

	let new_row=[
		`<button class="btn btn-danger btn-sm" onclick="removeArrival(${data['sid']})">x</button>`,
		`<a href="${child_id}">${data['name']}</a>`,
		`<input type="time" class="input_arrival" required value="${arrival}"></input>`,
		``
	];

	table_object.row.add(new_row).draw();	
	new_row_tr=$("#table1 tr:last");
	new_row_tr.addClass('child_in');
	new_row_tr.attr('data-cid', child_id);
	new_row_tr.attr('data-sid', data['sid']);

	
}


function addDeparture(data, cid, parent_row) {
	let departure=formattedDateFromString(data['departure'])

	let row_selector=data_tab1.rows(parent_row).nodes()
	row_selector.cell(0,3).data(`<input type="time" class="input_departure" required value="${departure}"></input>`).draw();

}


$(document).ready(function() {
	
	// génère une heure d'arrivée
	$('.child_out').click( function() {
		child_id=$(this).data("cid");

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
				else 
					addChildRow(data, child_id, data_tab1);
			}
		});
	});

	// génère une heure de départ
	$('#table1').on('click', '.in_departure', function() {
		child_id=$(this).parent().data("cid");
		var tr=$(this).closest('tr') // simplifie la récupération du node par DataTable
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
				else
					addDeparture(data, child_id, tr);
			}
		});
	});

	// Modifie une date d'arrivée
	data_tab1.on('blur', '.input_arrival', function(event) { 
		console.debug('modif de l\'arrivée');	
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_update_arrival,
			data: {
				'id': $(this).parent().parent().data("sid"),
				'hour': $(this).val()
			},
			dataType: 'json',
			success: function (data) {
				
				if(data['error'])
					alert(data['error']);	
			}
		});
	});
	
	// Modifie une date de départ
	data_tab1.on('blur', '.input_departure', function(event) { 
		console.debug('modif du départ');	
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_update_departure,
			data: {
				'id': $(this).parent().parent().data("sid"),
				'hour': $(this).val()
			},
			dataType: 'json',
			success: function (data) {
				
				if(data['error'])
					alert(data['error']);	
			}
		});
	});
	
});

