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
function removeArrival(schedule_id, child_id) {

 if(confirm('Êtes-vous sûr de vouloir le supprimer ?')){
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
				$(`#table2 [data-cid=${child_id}] td:eq(1)`).html('<button type="button" class="button_out_arrival btn btn-secondary btn-sm">Arrivée</button>');
			}
		}
	});
 }
}


// Utilitaire pour addChildUnexpectedArrival et editChildExpectedArrival 
// Renvoie le contenu d'un row selon data (une réponse JSon) et child_id
function getRowForChildIn(data, child_id) {
	let arrival=formattedDateFromString(data['arrival']);

	return [
		`<button class="btn btn-danger btn-sm" onclick="removeArrival(${data['sid']}, ${child_id})">x</button>`,
		`<a href="${child_id}">${data['name']}</a>`,
		`<input type="time" class="input_arrival" required value="${arrival}"></input>`,
		`<button type='button' class='button_in_departure btn btn-secondary btn-sm'>Départ</button>`
	];
}

// A partir d'un map data contenant des dates 'arrival, 'expected_arrival' 
// et 'expected_departure' au format aaaa-MM-jj hh:mm:ss, 
// ainsi qu'un string 'name', ajoute une entrée à la DataTable table_object affichant ces infos
function addChildUnexpectedArrival(data, child_id, table_object) {

	let new_row=getRowForChildIn(data, child_id);

	new_row=table_object.row.add(new_row).draw().node();	
	$(new_row).addClass('child_in');
	$(new_row).attr('data-cid', child_id);
	$(new_row).attr('data-sid', data['sid']);
}

// Voir addChildUnexpectedArrival, mais se contente d'éditer un row déhà présent
function editChildExpectedArrival(data, child_id, table_object) {
	
	let new_row=getRowForChildIn(data, child_id);
	let row=table_object.row(`[data-cid='${child_id}']`).nodes();	

	new_row.forEach(function (item, index) {
		row.cell(row,index).data(item).draw();
	})	
	
	let tr=$("#table1").find(`[data-cid='${child_id}']`);
	tr.attr('data-sid', data['sid']);
}

function addDeparture(data, cid) {
	let departure=formattedDateFromString(data['departure'])

	let row=data_tab1.row(`[data-cid='${cid}']`).nodes();	
	row.cell(row,3).data(`<input type="time" class="input_departure" required value="${departure}"></input>`).draw();

}

async function sendDeparture(child_id) {
	await $.ajax({
		headers: { "X-CSRFToken": csrf}, 
		type: 'POST',
		url: url_out,
		data: {
			'id': child_id,
		},
		dataType: 'json',
		success: function (data) {
			if(data['error']) {
			
				alert(data['error']);
			}
			else
				addDeparture(data, child_id);
		}
	});
} 

async function sendArrival(child_id) {
	await $.ajax({
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
				editChildExpectedArrival(data, child_id, data_tab1);
		}
	});

}

function sendArrivalFromAll(cell, child_id) {
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
				addChildUnexpectedArrival(data, child_id, data_tab1);
				cell.html("</span>Présent<span>");								
			}
		}
	});
}

function editArrival(sid) {
	$.ajax({
		headers: { "X-CSRFToken": csrf}, 
		type: 'POST',
		url: url_update_arrival,
		data: {
			'id': sid,
			'hour': $(this).val()
		},
		dataType: 'json',
		success: function (data) {
			
			if(data['error'])
				alert(data['error']);	
		}
	});
}

function editDeparture(sid) {
	$.ajax({
		headers: { "X-CSRFToken": csrf}, 
		type: 'POST',
		url: url_update_departure,
		data: {
			'id': sid,
			'hour': $(this).val()
		},
		dataType: 'json',
		success: function (data) {
			
			if(data['error'])
				alert(data['error']);	
		}
	});
}


$(document).ready(function() {
	
	// génère une heure d'arrivée depuis un enfant imprévu
	data_tab2.on( 'click', '.button_out_arrival', function() {
		cell=$(this).parent();
		child_id=cell.parent().data("cid");
		sendArrivalFromAll(cell,child_id);
	});

	// génère une heure d'arrivée depuis un enfant prévu
	data_tab1.on('click', '.button_in_arrival', function(event) { 
		sendArrival($(this).parent().parent().data("cid"));
	});



	// génère une heure de départ
	data_tab1.on('click', '.button_in_departure', function(event) { 
		sendDeparture($(this).parent().parent().data("cid"));
	});

	// Modifie une date d'arrivée
	data_tab1.on('blur', '.input_arrival', function(event) { 
		editArrival($(this).parent().parent().data("sid"));
	});
	
	// Modifie une date de départ
	data_tab1.on('blur', '.input_departure', function(event) { 
		editDeparture($(this).parent().parent().data("sid"))
	});
	
	
	// Valide tous les départs
	$('.button_all_arrivals').click(function() {
		$('.button_in_arrival').each(function() {
			$(this).click();
		});
	});
	// Valide toutes les arrivées
	$('.button_all_departures').click(function() {
		$('.button_in_departure').each(function() {
			$(this).click();
		});
	});
	
		
	$('#submit_date_day').click(function(event) {
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_children_here_day,
			data: {
				'day': $("#input_date_day").val()
			},
			dataType: 'html',
			success: function (data) {
				
				if(data['error'])
					alert(data['error']);	
				else {
				
					$("#childrenModal").html(data);
					$("#childrenModal").modal('toggle');
				}
			}
		});	
	});
	
});

