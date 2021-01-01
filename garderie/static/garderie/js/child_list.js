$(document).ready(function() {
		

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
			<td>${formattedDateFromString(arrival)}</td>\
			<td></td>\ 
			<td>${formattedDateFromString(expected_arrival)}</td>\
			<td>${formattedDateFromString(expected_departure)}</td></tr>`);
	}

	// enfants absents : au clic, envoie (async) l'id de l'enfant cliqué
	// une fois le Schedule ajouté, appelle addChildRow avec les données reçues
	
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
				else 
					addChildRow(data, child_id);
			}
		});
	});

	// enfants présents : au clic, envoie l'id'
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

