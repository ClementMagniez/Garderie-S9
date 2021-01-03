
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

// Permet l'édition de la date d'arrivée du schedule schedule_id d'un enfant child_id
// Si succès, affiche la date modifiée 

function showDeparture(departure, child_id, schedule_id) {
	$("#table1").find(`[data-value=${child_id}]`).find('.in_departure')
		.html(formattedDateFromString(departure));
	$("#table1").find(`[data-value=${child_id}]`).find('.in_departure').next()
		.html(`<button class="button_departure" onclick="editDeparture(${child_id},${schedule_id})">E</button>`);
}

function editDeparture(child_id, schedule_id) {
	newDate=window.prompt("Entrer l'heure modifiée");

	if(newDate) {
		$.ajax({
			headers: { "X-CSRFToken": csrf}, 
			type: 'POST',
			url: url_edit,
			data: {
				'id': schedule_id,
				'hour': newDate
			},
			dataType: 'json',
			success: function (data) {
				
				if(data['error'])
					alert(data['error']);	
				else 
					showDeparture(data['departure'], child_id, schedule_id);
			}
		});
	}	
}



$(document).ready(function() {
		
	// A partir d'un map data contenant des dates 'arrival, 'expected_arrival' 
	// et 'expected_departure' au format aaaa-MM-jj hh:mm:ss, 
	// ainsi qu'un string 'name', ajoute une entrée à #table1 affichant ces infos
	function addChildRow(data, child_id) {
		let arrival=data['arrival'];
		let expected_arrival=data['expected_arrival'];
		let expected_departure=data['expected_departure'];
		let table=$("#table1").find("tbody");
		table=table.append(`<tr class='child_in' data-value=${child_id}>\
			<td><a href="${child_id}">${data['name']}</a></td>\
			<td class="in_arrival">${formattedDateFromString(arrival)}</td>\
			<td class="in_departure"></td><td class="button_departure"></td>\ 
			<td class="in_expected_arrival">${formattedDateFromString(expected_arrival)}</td>\
			<td class="in_expected_departure">${formattedDateFromString(expected_departure)}</td></tr>`);
	}

	// enfants absents : au clic, envoie (async) l'id de l'enfant cliqué
	// une fois le Schedule ajouté, appelle addChildRow avec les données reçues
	
	$('.child_out').click( function() {
		child_id=$(this).data("value");

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
					addChildRow(data, child_id);
			}
		});
	});

	// enfants présents : au clic, envoie l'id
	// à la réponse, affiche la date de départ ou une erreur
	$('#table1').on('click', '.in_departure', function() {
		child_id=$(this).parent().data("value");
		console.log("gr"+child_id);
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
					showDeparture(data['departure'], child_id, data['sid']);
			}
		});
	});

});

